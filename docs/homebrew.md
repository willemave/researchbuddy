# ResearchBuddy Homebrew Tap

ResearchBuddy can be published as a third-party Homebrew tap.

## Generate the tap repo

From the source repository:

```bash
researchbuddy tap export
```

By default this writes a sibling repository at:

```text
../homebrew-researchbuddy
```

You can override the target:

```bash
researchbuddy tap export --output-dir /absolute/path/to/homebrew-researchbuddy
```

## What gets generated

- `Formula/researchbuddy.rb`
- `README.md`
- `.github/workflows/validate.yml`
- `skills/researchbuddy-tap-maintainer/SKILL.md`
- `skills/researchbuddy-tap-maintainer/references/publishing.md`

## Publish flow

1. Create and push a tagged release in the source repo, for example `v0.1.4`.
2. Compute the release tarball SHA:
   ```bash
   curl -L https://github.com/<owner>/researchbuddy/archive/refs/tags/v0.1.4.tar.gz | shasum -a 256
   ```
3. Update `Formula/researchbuddy.rb` with the real `sha256`.
4. Validate the tap:
   ```bash
   brew audit --strict --online researchbuddy
   brew install --build-from-source ./Formula/researchbuddy.rb
   brew test researchbuddy
   ```
5. Push the tap repo to `https://github.com/<owner>/homebrew-researchbuddy`.

## User install

```bash
brew tap <owner>/researchbuddy
brew install researchbuddy
```

## Hermes / OpenClaw paste block

Paste this into Hermes or another OpenClaw-style agent:

```text
Install ResearchBuddy with Homebrew:

brew tap willemave/researchbuddy
brew install researchbuddy

Before asking for any new search-provider key, check ~/.openclaw/openclaw.json.
If exa, tavily, or firecrawl is already configured there, ask whether ResearchBuddy should reuse that existing provider/key.
If the user says yes, do not collect a duplicate secret. Let ResearchBuddy setup/doctor use the OpenClaw config.

researchbuddy commands --agent
researchbuddy doctor --fix

If you support SKILL.md directories, load this bundled skill:
$(brew --prefix)/opt/researchbuddy/share/researchbuddy/skills/researchbuddy-cli

Read:
- $(brew --prefix)/opt/researchbuddy/share/researchbuddy/skills/researchbuddy-cli/SKILL.md

Do not start research runs until `researchbuddy doctor` passes.
```
