*I'm excited to share this guest post from the product team at Productboard. As they've evolved their platform around AI (first with Pulse, now with Spark), they've accumulated hard-won lessons about building AI-powered products customers love. Two insights stood out to me: first, their distinction between guiding and automating (users say they want AI to do tasks for them, but the real value is in AI that helps them think better). Second, their framing of AI quality as a "third dimension" that breaks traditional product development: you might build the UI and backend in two weeks, then spend two months iterating on AI quality. It's one of the more practical pieces I've seen on building AI that consistently delivers.*

Right now every product team is wrestling with the same question: How do we actually build AI products that work?

The advice is often too abstract (”AI will change everything!”) or too technical (“Here’s how you can optimize your RAG pipeline.”). What’s missing is the messy middle: the product decisions, team dynamics, and quality trade-offs that determine whether your AI feature delights users or gets abandoned after one try.

Over the past few years, Productboard has embarked on a journey to completely re-architect our product experience to be AI-first. We started with [Productboard Pulse](https://www.productboard.com/product/voice-of-customer/?utm_medium=influencer_pd&utm_source=substack&utm_campaign=tp_aw_all_product-page_all_pulse-product-page-ravi-mehta_fy25q4&utm_content=building-ai-products-ravi-mehta-substack-intro-section), a specialized product for analyzing customer feedback at scale, which taught us crucial early lessons about quality and user trust. Those learnings informed our work on [Productboard Spark](https://www.productboard.com/product/spark/?utm_medium=influencer_pd&utm_source=substack&utm_campaign=tp_aw_all_product-page_all_spark-product-page-ravi-mehta_fy25q4&utm_content=building-ai-products-ravi-mehta-substack-intro-section)—an agentic experience currently in private beta that represents a fundamental rethinking of the product management workflow, not just AI features bolted onto our existing platform.

Here’s what we’ve learned from building Spark, organized around three critical questions:

1. **How do you know you’re building the right thing?** We’ll cover evaluating AI use cases, the difference between guiding and automating, why *how* you build matters as much as *what* you build, and why you need to build ahead of customer readiness.

2. **How do you ship fast without sacrificing quality?** We’ll share our framework for quality thresholds (Alpha/Beta/GA), the third dimension of AI products, our systematic approach to improving from 40% to 85% accuracy, and why customers’ expectations have fundamentally shifted.

3. **How do you structure teams that scale?** We’ll explain the distinct team phases from tight core groups to specialized pods, why the transition is painful, and how to maintain velocity through rapid growth.

The first challenge hits you immediately: AI is really good at some things and terrible at others, but it’s not always obvious which is which.

Traditional product development is deterministic. You build a feature, test it, and it behaves the same way every time. AI is fundamentally different. The same input can produce different outputs. This non-determinism creates a new challenge: before you can decide *where* to apply AI, you first have to understand *what it can reliably do*. That became our first major hurdle.

So how do you approach this?

You still start with customer pain. That hasn’t changed. But here’s what’s different: you spend way more time on product discovery.

You need to validate not just that your solution is valuable, but that you can actually build it with the level of quality and reliability customers expect. Because customers might love your AI solution when it’s working, but have one too many bad outputs, and they’ll lose patience fast. With AI products, figuring out if you can build it well is just as important as figuring out if you should build it at all.

Here’s our approach:

1. Identify the most critical customer problems

2. Assess what AI capabilities excel at (summarization, analysis, generation)

3. Map those capabilities to customer problems

4. Validate feasibility through extensive testing—can we achieve the quality bar?

5. Prioritize use cases where both value and quality are achievable

And we want to emphasize that this isn’t building solutions in search of problems, but rather being strategic about sequencing. AI excels at summarizing text and analyzing qualitative feedback, so we started there with Pulse. We intentionally pushed back on use cases requiring deterministic outputs or perfect accuracy. Save those for later when you’ve built the muscle for systematic quality improvement.

Once you’ve identified the right use case, you face another critical decision about how AI should help the user solve a problem.

There’s a huge difference between:

- **Automating** = AI completes the task (ex: summarize this customer feedback)

- **Guiding (or as Ravi puts it, Amplifying)** = AI helps users think through the task and deliver better results (ex: what questions should I ask about this feedback?)

Users often say they want automation, but in reality, people are still wary of AI output quality (rightfully so!). The bar for full automation is much harder to achieve, and it’s one that users are skeptical of. AI tools need to build trust with users first. That’s why we see guiding as the current preferred operating model for product managers.

Plus, as AI becomes a strategic thinking partner, it becomes an embedded part of the users’ day to day workflows, driving deeper engagement and a stickier product. When we evaluated Spark, we realized PMs don’t need AI to just craft product artifacts for them, they need help thinking through customer needs, competitive alternatives, and business context.
> “The process is not that you tell the agent, ‘Hey, write an initiative brief or PRD’ and it just writes it for you. The process rather is that the agent needs to guide you through the steps that you need to go through as a human in order to gain a deep understanding of customers, their needs, your existing product limitations, competing alternatives, and the context of your business objectives. That’s what Spark is about. It’s the richness of the agent interaction.”
>
> *— Hubert Palan, Founder & CEO, Productboard*

This insight became our filter to create a valuable experience. Don’t ask “can AI do this task faster?” Ask “will AI help users make better decisions and take better action?” That’s where you find use cases worth building.

For Spark, this meant building an agent that enhances how product managers approach strategic thinking, not just automating their deliverables.

The interface shapes whether your AI becomes indispensable or just another tool. Most teams default to chat because it’s familiar, but that’s rarely enough. You need to make this decision during discovery, not after you’ve already built the backend.

**Align your interface to the task type:**

Conversational interfaces work best for:

- Exploration and discovery

- Text generation and editing

- Open-ended questions

- Individual work

- Empowering users who know what they want

Structured interfaces work best for:

- Visualization and comparison

- Collaboration in a shared, persistent view

- Prioritization and decision-making

- Workflow orchestration

- Guiding users who aren’t sure what they need

Most valuable AI products need both.
> “The value in having structured interfaces is that they create a shared mental model for people to consume information, which creates consistency in how people then collaborate together.”
>
> *— Hubert Palan, Founder & CEO, Productboard*

Think about it: if every sales rep saw a completely different Salesforce interface, collaboration would be impossible. The same applies to AI products. Assess your UI trade-offs early.

Once you understand your interface needs, your users’ entry point, you can rethink workflows from scratch:
> “Good AI products realize that the world in the AI era is going to change the flows itself. They’re introducing new flows that are AI-first.”
>
> *— Dominik Ilichman, Senior AI Product Manager, Productboard*

Many companies bolt AI onto existing workflows, creating “legacy tools with AI features somewhere.” The better approach: Start from the beginning. Reimagine workflows, especially ones that are only possible with AI.

To validate without over-building, start maximally flexible. Build the simplest interaction pattern, validate with users, then optimize specific workflows that show strong adoption signals.

Once you know what to build, you face an even harder question: How do you invest in AI while supporting existing customers who aren’t ready yet?

We had to accept a painful reality: you can’t satisfy early adopters and the late majority simultaneously. Early adopters will embrace imperfect AI and provide valuable feedback. The late majority expects “AI magic”—polished, predictable, and high quality outputs.

Almost always, you have to pick who you’re building for.
> “You have early adopters, you have early majority, late majority, and so on, and you need to start building. We know that AI is getting diffused into society faster than any other technology. And so you are putting more resources towards that, expecting that people will catch up. You’re building ahead.”
>
> *— Hubert Palan, Founder & CEO, Productboard*

The case we made to existing customers: “Bet on a company that will lead in the AI era, even if you’re not ready today.” Because, the company pushing boundaries today will be the one delivering mature, reliable AI when customers are ready to adopt.

Speed and quality feel like opposing forces in AI. Move too fast and customers hate the output. Move too slow and you miss the window. The key is knowing what quality bar matters at each stage.

[https://substackcdn.com/image/fetch/$s_!pK1l!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F01790874-d1c1-4776-a0fa-3fa2b23c7a11_1080x1350.png](https://substackcdn.com/image/fetch/$s_!pK1l!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F01790874-d1c1-4776-a0fa-3fa2b23c7a11_1080x1350.png)

We learned to think about AI quality in tiers, not as a binary. Here’s an example framework (...emphasis on example because specific thresholds will vary based on your use case):

**Alpha: Internal validation (40-60% accuracy)**

- Does the AI understand the task?

- Are responses valuable?

- Can we articulate why it fails?

**Beta: Controlled customer testing (70-85% accuracy)**

- Would users trust this output?

- Does it accelerate their work?

- Are failures recoverable?

- Do customers come back?

**GA: Broad release (85%+ accuracy)**

- Is quality consistent across use cases?

- Can we maintain this at scale?

If you don’t have explicit frameworks to measure these thresholds, you’re guessing.

I would be lying if I said we had quality out of the gate with Pulse. We were a little bit premature given it was our first foray into generative AI and the entire industry was learning in real time. We launched before the quality was consistent enough to build user trust. And more generally, expectations outpaced what the technology could deliver. But through that process, we learned a lot more about the guardrails and bounds necessary for bringing an AI product to market. We fixed the quality issues (Pulse is now at 95% accuracy, soon to be 99%), and applied those lessons to Spark: rigorous evals, stricter quality gates, and systematic improvement before each release stage (the framework you saw above).

Specifically, we used a combination of engaged user metrics and AI quality evaluation scores to measure quality and determine when we were ready to move between thresholds.

During private beta, our primary signal was engagement and activation. We closely monitored how participants were using the product, where they were getting value, and where they were dropping off. We paired those quantitative activation metrics with live customer feedback, and actively pivoted the roadmap based on that data until we saw consistent improvements in activation and repeat usage. This was our bar for moving into public beta.

In parallel, we built a more robust AI evaluation framework to measure output quality directly. We use a mix of automated and human evaluations, grounded in “golden” datasets made up of both curated and synthetic data. These datasets allow us to score AI outputs against specific quality dimensions that vary by agent. For example, for our customer feedback analysis agent, we track metrics like feedback citation accuracy and insight relevance.

Once in production, we continue to validate quality by sampling real user traces and scoring them to flag strong versus poor AI interactions. This helps us understand how outputs are being received by users in real workflows and ensures we’re consistently meeting the quality threshold required for a reliable, high-trust experience.

But, it’s not just our process that has evolved. Generative AI is changing user expectations, even from our enterprise customers. Thanks to the likes of OpenAI and ChatGPT, people understand that innovation happens quickly and you don’t want perfect to get in the way of good.

Our observation: customers will accept solutions at 70-80% accuracy if they see you improving it frequently (ideally weekly). Traditional enterprise software taught users to expect perfection at launch, then slow annual updates. AI has inverted this. Ship when it’s useful, iterate in public, show progress constantly.

With AI products, “beta” means “good enough to accelerate your work today, measurably better next week.”

Traditional SaaS products have two dimensions: what users see (frontend) and what makes it work (backend). AI products have three.
> “Traditional SaaS products have backend and frontend. With AI, there is the third dimension of AI quality that you really need to focus on.”
>
> *— Dominik Ilichman, Senior AI Product Manager, Productboard*

This changes everything about estimation. Teams estimate AI projects like traditional projects. Frontend time + backend time = done. This is wrong.
> “When we started building AI functionalities, we took the same approach. We implemented frontend, we implemented backend including the AI backend, and then we released it. And we failed often because we didn’t account for the time on the quality iterations.”
>
> *— Dominik Ilichman, Senior AI Product Manager, Productboard*

The reality is that you might build the UI and backend in two weeks, then spend two months iterating on AI quality. And that’s where setting team expectations, especially with leadership, is critical. The time to build says nothing about how complex quality iteration will be. Give yourself room to fail (and get better).

Here’s the process that took us from 40% to 85% accuracy with Spark:

**Step 1: Write test scenarios rooted in customer understanding.**

Pick a specific use case. Write 20-50 example questions a user would ask. Create reference answers that represent high quality outputs. This becomes your evaluation dataset.

Here’s the important part: you need deep domain expertise to[write effective evals.](https://www.productboard.com/blog/ai-evals-for-product-managers/?utm_medium=influencer_pd&utm_source=substack&utm_campaign=tp_aw_all_blog_all_ai-evals-blog-promo-ravi-mehta_fy26q4&utm_content=building-ai-products-ravi-mehta-substack-evals-section) You must understand exactly what good outcomes look like for your customers and infuse your market knowledge and key guardrails into these scenarios. Shallow understanding means imprecise evals, which means inconsistent quality.

Some best practices we’ve learned:

- **Prioritize evaluating individual quality dimensions/metrics**: Single dimensions are easier for evaluation tools to judge accurately; combining several single-criterion evaluations into an evaluation suite gives you granular insight into what’s performing well and what needs attention. For example, instead of one evaluation asking “Does the AI provide a good response?” (multi-dimension), create separate evaluations for accuracy, completeness, actionability, and tone—this reveals you might score 90% on accuracy but only 60% on actionability, pinpointing exactly what needs work.

- **Make sure you’re testing what you care about**: Similar to writing unit tests, it’s easy to write too many or irrelevant evals. Identifying the exact dimensions you care about is a useful exercise to clarify what quality means and align the team.

- **Leave room for improvement**: If everything scores 100%, you can’t measure further improvements. Make evals stricter or add more dimensions to enable continuous improvement.

- **Don’t over-index on scores**: Evaluation scores are highly variable and not super useful on their own. Use them to direct human reviewers’ attention and development effort.

**Step 2: Automate measurement.** Feed scenarios into an evaluation tool. Get a quality score (often starting at 40-50%). Set a target threshold (usually 80-90%). Iterate on prompts, context, and architecture until you hit it. And make sure to track changes so that you can tie your eval efforts to product improvements.

**Step 3: Enable internal testing.** Release to internal users early and often. Make it easy to report issues (Slack channel). The team sees real failures and fixes them immediately. This catches edge cases evaluations miss.

At Productboard, we start every new AI capability with eval frameworks.
> “Very often we start at like 40% accuracy and then we have a target, and step by step we iterate until we get to 80-90% of accuracy.”
>
> – Dominik Ilichman, Senior AI Product Manager, Productboard

This takes weeks, but it’s the only way to ensure quality before customers see it.

The most liberating insight for us has been that **we’re all figuring it out together**. It’s trial and error on how to build agentic workflows, how to manage context windows, and handovers between agents. No one has it down perfectly right now.

You’re not behind because you don’t have all the answers. The teams winning are those failing fast and moving through the learning curve.

AI products require different team structures at different stages. The mistake is trying to scale too early or staying small too long. Here’s how teams typically evolve and the risks at each stage:

Start with a tight group who knows everything. The goal is finding product-market fit for one use case. Ship internally weekly while iterating on quality.

**What works:**

- Everyone understands the full system

- Decisions happen fast

- Context is shared naturally

- Iteration is rapid

**The risk:**

- Everything lives in people’s heads

- Nothing is documented

- You can’t onboard new people easily

As you prove the concept and expand use cases, you bring in more people. This is where things get messy.

Because when you have one team do everything, they know everything. The context and communication exist in one room. But the bigger the scale and the more people involved, the harder it can be to ensure you’re all working in the same direction.

**What breaks:**

- New team members lack context

- Communication overhead explodes

- Velocity often slows down

- Quality becomes inconsistent

**The solution:** Teams need to know what they’re working toward. They need a strong product vision.

With traditional deterministic software, this might be a 12-month roadmap with clear features and timelines. AI products work differently. Your concrete, tactical vision might only look 3 months ahead, focused on specific use cases and measurable quality improvements. But you still need a longer-term north star: how you want to impact your users and the space you’re working in over the next year.

The key is grounding your vision in problems, not solutions. In traditional software, you’re constrained by your ability to deliver what you’ve envisioned. With AI, you often don’t know how the solution will look months from now, but you should have deep clarity on the problems you’re solving.

Keep your documentation as centralized as possible, and ensure everyone understands how their work connects to both the near-term goals and the broader mission

As you build multiple use cases and complex features, teams need to specialize: one for navigation, another for editing experiences, another for building agents, another for orchestration, and so on, depending on your circumstances. But do note, AI is no longer it’s own team. As Ravi himself has told us, every PM is really an AI PM, every team is really an AI team. It’s part of the fabric of modern products, not something distinct and separate.

**What’s required:**

- Clear ownership boundaries

- Shared architectural vision

- Strong documentation

- Regular sync points

Your team structure should match your product’s maturity. Don’t specialize too early (you’ll lose velocity). Don’t stay generalized too long (you’ll build inconsistent experiences).

After a few years of building AI products and supporting teams that are building AI products, one truth became clear: **the fundamentals of product management haven’t changed**.

Understanding customer needs. Defining clear workflows. Building with quality in mind. Iterating based on feedback. Creating shared context for teams. These principles still drive great products.

What has changed is how these fundamentals manifest. AI introduces non-determinism that requires new quality frameworks. Team structures evolve faster. Timeline estimation practices must account for quality iteration. Building ahead of customer readiness requires new conviction.

But at its core, building AI products is still about solving real problems for real people.
> “Working on Spark is the most exciting product I’ve worked on. From the very beginning we were solving a problem that I, as an individual contributor PM, faced massively. And from maybe the first week, we already had a prototype that I started using in my day-to-day life.”
>
> *— Dominik Ilichman, Senior AI Product Manager, Productboard*

If you’re building AI products, start by matching customer pain to your tech capabilities. Build prototypes fast. Measure quality rigorously. Let your team evolve as you scale. And remember: everyone is figuring this out together.

The teams that ship great AI products aren’t the ones who knew all the answers from day one—they’re the ones who learned fastest from what didn’t work.

See how we brought all of these learnings to life with [Productboard Spark. Try Spark in public beta today!](https://www.productboard.com/product/spark/?utm_medium=influencer_pd&utm_source=substack&utm_campaign=tp_aw_all_product-page_all_spark-product-launch-ravi-mehta_fy25q4&utm_content=building-ai-products-ravi-mehta-substack-final-cta)

No posts
