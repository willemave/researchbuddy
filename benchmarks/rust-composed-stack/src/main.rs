use anyhow::{anyhow, Context, Result};
use clap::{Parser, ValueEnum};
use chromiumoxide::{Browser, BrowserConfig};
use dom_smoothie::Readability;
use futures_util::StreamExt;
use html_to_markdown_rs::convert;
use rusty_ytdl::Video;
use scraper::{Html, Selector};
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::{Path, PathBuf};
use std::time::{Duration, Instant};

#[derive(Parser, Debug)]
struct Args {
    #[arg(long)]
    manifest: PathBuf,
    #[arg(long)]
    output: PathBuf,
    #[arg(long)]
    markdown_dir: Option<PathBuf>,
    #[arg(long, value_enum)]
    mode: Mode,
    #[arg(long, value_enum, default_value_t = Tool::Static)]
    tool: Tool,
    #[arg(long, default_value_t = 0)]
    limit: usize,
    #[arg(long, default_value_t = 45_000)]
    timeout_ms: u64,
}

#[derive(Clone, Copy, Debug, ValueEnum)]
enum Mode {
    Live,
    ExtractOnly,
}

#[derive(Clone, Copy, Debug, ValueEnum, Eq, PartialEq)]
enum Tool {
    Static,
    Hybrid,
}

#[derive(Debug, Deserialize)]
struct Manifest {
    entries: Vec<CorpusEntry>,
}

#[derive(Debug, Deserialize)]
struct CorpusEntry {
    url: String,
    domain: String,
    category: String,
    tags: Vec<String>,
    html_path: Option<String>,
}

#[derive(Debug, Serialize)]
struct BenchResult {
    url: String,
    domain: String,
    category: String,
    tags: Vec<String>,
    mode: String,
    strategy: String,
    success: bool,
    elapsed_ms: f64,
    markdown_chars: usize,
    markdown_output_path: Option<String>,
    error: Option<String>,
}

#[derive(Debug, Serialize)]
struct Summary {
    total: usize,
    successes: usize,
    failures: usize,
    mean_elapsed_ms: Option<f64>,
    median_elapsed_ms: Option<f64>,
    p95_elapsed_ms: Option<f64>,
    min_elapsed_ms: Option<f64>,
    max_elapsed_ms: Option<f64>,
    mean_markdown_chars: Option<f64>,
}

#[derive(Debug, Serialize)]
struct OutputPayload {
    tool: String,
    mode: String,
    manifest: String,
    markdown_dir: Option<String>,
    timeout_ms: u64,
    summary: Summary,
    results: Vec<BenchResult>,
}

struct MarkdownCandidate {
    markdown: String,
    strategy: String,
}

struct BrowserRuntime {
    browser: Browser,
    handler_task: tokio::task::JoinHandle<()>,
    timeout_ms: u64,
}

#[tokio::main]
async fn main() -> Result<()> {
    let args = Args::parse();
    let manifest_text = fs::read_to_string(&args.manifest)
        .with_context(|| format!("failed to read manifest {}", args.manifest.display()))?;
    let mut manifest: Manifest =
        serde_json::from_str(&manifest_text).context("failed to parse manifest JSON")?;
    if args.limit > 0 && manifest.entries.len() > args.limit {
        manifest.entries.truncate(args.limit);
    }

    let client = reqwest::Client::builder()
        .timeout(Duration::from_millis(args.timeout_ms))
        .user_agent("researchbuddy-rust-bench/0.2")
        .build()
        .context("failed to build reqwest client")?;

    let mut browser = match (args.tool, args.mode) {
        (Tool::Hybrid, Mode::Live) => Some(BrowserRuntime::launch(args.timeout_ms).await?),
        _ => None,
    };

    let mut results = Vec::with_capacity(manifest.entries.len());
    for (index, entry) in manifest.entries.iter().enumerate() {
        let result = match args.mode {
            Mode::Live => benchmark_live(
                &client,
                browser.as_mut(),
                entry,
                args.tool,
                args.markdown_dir.as_deref(),
                index,
            )
            .await,
            Mode::ExtractOnly => {
                benchmark_extract_only(entry, args.markdown_dir.as_deref(), index).await
            }
        };
        results.push(result);
    }

    if let Some(browser_runtime) = browser.take() {
        browser_runtime.shutdown().await?;
    }

    let payload = OutputPayload {
        tool: match args.tool {
            Tool::Static => "rust-static".to_string(),
            Tool::Hybrid => "rust-hybrid".to_string(),
        },
        mode: match args.mode {
            Mode::Live => "live".to_string(),
            Mode::ExtractOnly => "extract-only".to_string(),
        },
        manifest: args.manifest.display().to_string(),
        markdown_dir: args
            .markdown_dir
            .as_ref()
            .map(|value| value.display().to_string()),
        timeout_ms: args.timeout_ms,
        summary: summarize(&results),
        results,
    };

    if let Some(parent) = args.output.parent() {
        fs::create_dir_all(parent)
            .with_context(|| format!("failed to create output dir {}", parent.display()))?;
    }
    fs::write(&args.output, serde_json::to_string_pretty(&payload)?)
        .with_context(|| format!("failed to write {}", args.output.display()))?;

    println!("tool={} mode={}", payload.tool, payload.mode);
    println!(
        "total={} successes={} failures={}",
        payload.summary.total, payload.summary.successes, payload.summary.failures
    );
    if let Some(mean) = payload.summary.mean_elapsed_ms {
        println!(
            "mean_elapsed_ms={:.2} median_elapsed_ms={:.2} p95_elapsed_ms={:.2}",
            mean,
            payload.summary.median_elapsed_ms.unwrap_or(0.0),
            payload.summary.p95_elapsed_ms.unwrap_or(0.0)
        );
    }
    println!("output={}", args.output.display());

    Ok(())
}

impl BrowserRuntime {
    async fn launch(timeout_ms: u64) -> Result<Self> {
        let config = BrowserConfig::builder()
            .build()
            .map_err(|error| anyhow!("failed to build browser config: {error}"))?;
        let (browser, mut handler) =
            Browser::launch(config).await.context("failed to launch chromiumoxide browser")?;
        let handler_task = tokio::spawn(async move {
            while let Some(event) = handler.next().await {
                if event.is_err() {
                    break;
                }
            }
        });
        Ok(Self {
            browser,
            handler_task,
            timeout_ms,
        })
    }

    async fn fetch_html(&mut self, url: &str) -> Result<String> {
        let timeout = Duration::from_millis(self.timeout_ms);
        let page = tokio::time::timeout(timeout, self.browser.new_page(url))
            .await
            .with_context(|| format!("browser page open timed out for {}", url))?
            .with_context(|| format!("failed to open browser page for {}", url))?;
        tokio::time::timeout(timeout, page.find_element("body"))
            .await
            .with_context(|| format!("browser body wait timed out for {}", url))?
            .with_context(|| format!("browser could not find body for {}", url))?;
        tokio::time::sleep(Duration::from_millis(2_000)).await;
        let html = tokio::time::timeout(timeout, page.content())
            .await
            .with_context(|| format!("browser HTML read timed out for {}", url))?
            .with_context(|| format!("failed to read browser HTML for {}", url))?;
        let _ = tokio::time::timeout(timeout, page.close()).await;
        Ok(html)
    }

    async fn shutdown(mut self) -> Result<()> {
        self.browser.close().await.context("failed to close chromiumoxide browser")?;
        self.handler_task.await.context("failed to join browser handler task")?;
        Ok(())
    }
}

async fn benchmark_live(
    client: &reqwest::Client,
    browser: Option<&mut BrowserRuntime>,
    entry: &CorpusEntry,
    tool: Tool,
    markdown_dir: Option<&Path>,
    index: usize,
) -> BenchResult {
    let start = Instant::now();
    let result = match tool {
        Tool::Static => run_static_live(client, entry).await,
        Tool::Hybrid => run_hybrid_live(client, browser, entry).await,
    };

    build_bench_result(result, entry, "live", start, markdown_dir, index)
}

async fn benchmark_extract_only(
    entry: &CorpusEntry,
    markdown_dir: Option<&Path>,
    index: usize,
) -> BenchResult {
    let start = Instant::now();
    let result = async {
        let html_path = entry
            .html_path
            .as_ref()
            .ok_or_else(|| anyhow!("html_path missing from manifest entry"))?;
        let html = tokio::fs::read_to_string(html_path)
            .await
            .with_context(|| format!("failed to read {}", html_path))?;
        extract_best_candidate(&html, &entry.url)
    }
    .await;

    build_bench_result(result, entry, "extract-only", start, markdown_dir, index)
}

fn build_bench_result(
    result: Result<MarkdownCandidate>,
    entry: &CorpusEntry,
    mode: &str,
    start: Instant,
    markdown_dir: Option<&Path>,
    index: usize,
) -> BenchResult {
    match result {
        Ok(candidate) => {
            let markdown_output_path =
                write_markdown(markdown_dir, index, &entry.domain, &candidate.markdown).ok();
            BenchResult {
                url: entry.url.clone(),
                domain: entry.domain.clone(),
                category: entry.category.clone(),
                tags: entry.tags.clone(),
                mode: mode.to_string(),
                strategy: candidate.strategy,
                success: true,
                elapsed_ms: start.elapsed().as_secs_f64() * 1000.0,
                markdown_chars: candidate.markdown.chars().count(),
                markdown_output_path,
                error: None,
            }
        }
        Err(error) => BenchResult {
            url: entry.url.clone(),
            domain: entry.domain.clone(),
            category: entry.category.clone(),
            tags: entry.tags.clone(),
            mode: mode.to_string(),
            strategy: "failed".to_string(),
            success: false,
            elapsed_ms: start.elapsed().as_secs_f64() * 1000.0,
            markdown_chars: 0,
            markdown_output_path: None,
            error: Some(error.to_string()),
        },
    }
}

async fn run_static_live(client: &reqwest::Client, entry: &CorpusEntry) -> Result<MarkdownCandidate> {
    if is_youtube(entry) {
        if let Ok(candidate) = extract_youtube_markdown(&entry.url).await {
            return Ok(candidate);
        }
    }

    let html = fetch_html(client, &entry.url).await?;
    extract_best_candidate(&html, &entry.url)
}

async fn run_hybrid_live(
    client: &reqwest::Client,
    browser: Option<&mut BrowserRuntime>,
    entry: &CorpusEntry,
) -> Result<MarkdownCandidate> {
    if is_youtube(entry) {
        if let Ok(candidate) = extract_youtube_markdown(&entry.url).await {
            return Ok(candidate);
        }
    }

    let mut best_candidate: Option<MarkdownCandidate> = None;
    let mut latest_error: Option<anyhow::Error> = None;

    match fetch_html(client, &entry.url).await {
        Ok(html) => {
            match extract_best_candidate(&html, &entry.url) {
                Ok(candidate) => best_candidate = Some(candidate),
                Err(error) => latest_error = Some(error),
            }
            if !should_try_browser(entry, best_candidate.as_ref()) {
                return best_candidate.ok_or_else(|| {
                    latest_error.unwrap_or_else(|| anyhow!("static extraction failed for {}", entry.url))
                });
            }
        }
        Err(error) => latest_error = Some(error),
    }

    if let Some(browser_runtime) = browser {
        match browser_runtime.fetch_html(&entry.url).await {
            Ok(browser_html) => {
                let browser_candidate =
                    extract_best_candidate_with_prefix(&browser_html, &entry.url, "browser")?;
                best_candidate = pick_better_candidate(best_candidate, browser_candidate, entry);
            }
            Err(error) => latest_error = Some(error),
        }
    }

    best_candidate.ok_or_else(|| latest_error.unwrap_or_else(|| anyhow!("no extraction result for {}", entry.url)))
}

fn should_try_browser(entry: &CorpusEntry, candidate: Option<&MarkdownCandidate>) -> bool {
    if entry.category == "podcast" {
        return true;
    }
    if entry.tags.iter().any(|tag| tag == "js_heavy") {
        return true;
    }
    match candidate {
        Some(candidate) => candidate.markdown.chars().count() < thin_threshold(entry),
        None => true,
    }
}

fn thin_threshold(entry: &CorpusEntry) -> usize {
    match entry.category.as_str() {
        "youtube" => 600,
        "podcast" => 900,
        "js_heavy" => 700,
        _ => 400,
    }
}

fn pick_better_candidate(
    current: Option<MarkdownCandidate>,
    candidate: MarkdownCandidate,
    entry: &CorpusEntry,
) -> Option<MarkdownCandidate> {
    match current {
        Some(existing) => {
            if candidate_score(&candidate, entry) > candidate_score(&existing, entry) {
                Some(candidate)
            } else {
                Some(existing)
            }
        }
        None => Some(candidate),
    }
}

fn candidate_score(candidate: &MarkdownCandidate, entry: &CorpusEntry) -> usize {
    let markdown_chars = candidate.markdown.chars().count();
    let heading_bonus = candidate
        .markdown
        .lines()
        .filter(|line| line.trim_start().starts_with('#'))
        .count()
        * 200;
    let metadata_penalty = if candidate.strategy.contains("metadata") { 600 } else { 0 };
    let thin_penalty = if markdown_chars < thin_threshold(entry) { 400 } else { 0 };
    markdown_chars + heading_bonus - metadata_penalty - thin_penalty
}

async fn fetch_html(client: &reqwest::Client, url: &str) -> Result<String> {
    let response = client
        .get(url)
        .send()
        .await
        .with_context(|| format!("request failed for {}", url))?
        .error_for_status()
        .with_context(|| format!("non-success status for {}", url))?;
    response
        .text()
        .await
        .with_context(|| format!("failed to decode body for {}", url))
}

fn extract_best_candidate(html: &str, url: &str) -> Result<MarkdownCandidate> {
    extract_best_candidate_with_prefix(html, url, "static")
}

fn extract_best_candidate_with_prefix(html: &str, url: &str, prefix: &str) -> Result<MarkdownCandidate> {
    if let Ok(markdown) = extract_readability_markdown(html, url) {
        return Ok(MarkdownCandidate {
            markdown,
            strategy: format!("{prefix}-readability"),
        });
    }

    if let Some(markdown) = extract_metadata_markdown(html, url) {
        return Ok(MarkdownCandidate {
            markdown,
            strategy: format!("{prefix}-metadata"),
        });
    }

    Err(anyhow!("no markdown candidate for {}", url))
}

fn extract_readability_markdown(html: &str, url: &str) -> Result<String> {
    let mut readability =
        Readability::new(html, Some(url), None).with_context(|| format!("readability init failed for {}", url))?;
    let article = readability
        .parse()
        .with_context(|| format!("readability parse failed for {}", url))?;
    let extracted_html = article.content.to_string();
    let conversion = convert(&extracted_html, None)
        .with_context(|| format!("html-to-markdown conversion failed for {}", url))?;
    Ok(conversion.content.unwrap_or_default())
}

fn extract_metadata_markdown(html: &str, url: &str) -> Option<String> {
    let document = Html::parse_document(html);
    let title_selector = Selector::parse("title").ok()?;
    let meta_selector = Selector::parse("meta").ok()?;

    let title = document
        .select(&title_selector)
        .next()
        .map(|value| value.text().collect::<String>().trim().to_string())
        .filter(|value| !value.is_empty())
        .or_else(|| select_meta_content(&document, &meta_selector, "property", "og:title"))
        .or_else(|| select_meta_content(&document, &meta_selector, "name", "twitter:title"));

    let description = select_meta_content(&document, &meta_selector, "name", "description")
        .or_else(|| select_meta_content(&document, &meta_selector, "property", "og:description"))
        .or_else(|| select_meta_content(&document, &meta_selector, "name", "twitter:description"));

    let site_name = select_meta_content(&document, &meta_selector, "property", "og:site_name");

    if title.is_none() && description.is_none() {
        return None;
    }

    let mut markdown = String::new();
    if let Some(value) = title {
        markdown.push_str("# ");
        markdown.push_str(value.trim());
        markdown.push_str("\n\n");
    }
    if let Some(value) = description {
        markdown.push_str(value.trim());
        markdown.push_str("\n\n");
    }
    if let Some(value) = site_name {
        markdown.push_str("Site: ");
        markdown.push_str(value.trim());
        markdown.push_str("\n\n");
    }
    markdown.push_str("Source: ");
    markdown.push_str(url);
    markdown.push('\n');
    Some(markdown)
}

fn select_meta_content(
    document: &Html,
    selector: &Selector,
    attr_name: &str,
    attr_value: &str,
) -> Option<String> {
    document
        .select(selector)
        .find_map(|element| {
            let matches_name = element.value().attr(attr_name)? == attr_value;
            if !matches_name {
                return None;
            }
            element
                .value()
                .attr("content")
                .map(str::trim)
                .filter(|value| !value.is_empty())
                .map(ToOwned::to_owned)
        })
}

async fn extract_youtube_markdown(url: &str) -> Result<MarkdownCandidate> {
    let video = Video::new(url).with_context(|| format!("rusty_ytdl init failed for {}", url))?;
    let info = video
        .get_info()
        .await
        .with_context(|| format!("rusty_ytdl info fetch failed for {}", url))?;

    let mut markdown = String::new();
    markdown.push_str("# ");
    markdown.push_str(info.video_details.title.as_str());
    markdown.push_str("\n\n");

    if let Some(author) = info.video_details.author.as_ref() {
        markdown.push_str("Channel: ");
        markdown.push_str(author.name.as_str());
        markdown.push_str("\n\n");
    }

    if !info.video_details.description.trim().is_empty() {
        markdown.push_str(info.video_details.description.trim());
        markdown.push_str("\n\n");
    }

    markdown.push_str("Source: ");
    markdown.push_str(url);
    markdown.push('\n');

    Ok(MarkdownCandidate {
        markdown,
        strategy: "youtube-rusty_ytdl".to_string(),
    })
}

fn is_youtube(entry: &CorpusEntry) -> bool {
    entry.tags.iter().any(|tag| tag == "youtube")
}

fn write_markdown(markdown_dir: Option<&Path>, index: usize, domain: &str, markdown: &str) -> Result<String> {
    let markdown_dir = markdown_dir.ok_or_else(|| anyhow!("markdown_dir not configured"))?;
    fs::create_dir_all(markdown_dir)
        .with_context(|| format!("failed to create markdown dir {}", markdown_dir.display()))?;
    let sanitized_domain = domain.replace('.', "_");
    let output_path = markdown_dir.join(format!("{index:03}-{sanitized_domain}.md"));
    fs::write(&output_path, markdown)
        .with_context(|| format!("failed to write {}", output_path.display()))?;
    Ok(output_path.display().to_string())
}

fn summarize(results: &[BenchResult]) -> Summary {
    let mut elapsed: Vec<f64> = results
        .iter()
        .filter(|result| result.success)
        .map(|result| result.elapsed_ms)
        .collect();
    let markdown_chars: Vec<usize> = results
        .iter()
        .filter(|result| result.success)
        .map(|result| result.markdown_chars)
        .collect();

    let total = results.len();
    let successes = results.iter().filter(|result| result.success).count();
    let failures = total.saturating_sub(successes);

    if elapsed.is_empty() {
        return Summary {
            total,
            successes,
            failures,
            mean_elapsed_ms: None,
            median_elapsed_ms: None,
            p95_elapsed_ms: None,
            min_elapsed_ms: None,
            max_elapsed_ms: None,
            mean_markdown_chars: None,
        };
    }

    elapsed.sort_by(|left, right| left.partial_cmp(right).unwrap_or(std::cmp::Ordering::Equal));
    let mean_elapsed_ms = elapsed.iter().sum::<f64>() / elapsed.len() as f64;
    let median_elapsed_ms = percentile(&elapsed, 50.0);
    let p95_elapsed_ms = percentile(&elapsed, 95.0);
    let min_elapsed_ms = elapsed.first().copied();
    let max_elapsed_ms = elapsed.last().copied();
    let mean_markdown_chars = if markdown_chars.is_empty() {
        None
    } else {
        Some(markdown_chars.iter().sum::<usize>() as f64 / markdown_chars.len() as f64)
    };

    Summary {
        total,
        successes,
        failures,
        mean_elapsed_ms: Some(mean_elapsed_ms),
        median_elapsed_ms: Some(median_elapsed_ms),
        p95_elapsed_ms: Some(p95_elapsed_ms),
        min_elapsed_ms,
        max_elapsed_ms,
        mean_markdown_chars,
    }
}

fn percentile(values: &[f64], p: f64) -> f64 {
    if values.is_empty() {
        return 0.0;
    }
    if values.len() == 1 {
        return values[0];
    }

    let rank = (values.len() as f64 - 1.0) * (p / 100.0);
    let lower = rank.floor() as usize;
    let upper = rank.ceil() as usize;
    if lower == upper {
        return values[lower];
    }
    let weight = rank - lower as f64;
    values[lower] * (1.0 - weight) + values[upper] * weight
}
