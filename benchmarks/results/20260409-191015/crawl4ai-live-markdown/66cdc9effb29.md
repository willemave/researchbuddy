# What OpenAI and Google engineers learned deploying 50+ AI products in production
[Lenny's Podcast: Product | Career | Growth](https://pod.wave.co/podcast/lennys-podcast-product-career-growth-b65486a6-7cff-4966-bbea-2bc239e90aa4)Saved by 9 users
Sun Jan 11 2026
### Get Free Podcast Summaries in Your Inbox
Subscribe to your favorite podcasts and get free AI summaries within minutes of release.
1
#### Pick Your Shows
Browse trending podcasts or search for your favorites
2
#### Subscribe Free
One click to follow any show — always free, no credit card
3
#### Get Instant Summaries
Free AI summaries delivered by email within minutes of release
Sign In
Free forever · No credit card · Unsubscribe anytime
Never miss an episode of Lenny's Podcast: Product | Career | Growth. [Subscribe for free →](https://pod.wave.co/podcast/lennys-podcast-product-career-growth-b65486a6-7cff-4966-bbea-2bc239e90aa4)
## Summary
# Podcast Summary
## Lenny's Podcast: Product | Career | Growth
**Episode** : What OpenAI and Google Engineers Learned Deploying 50+ AI Products in Production **Date** : January 11, 2026 **Host** : Lenny Rachitsky **Guests** : Aishwarya Raganti (AI researcher, consultant, Alexa, Microsoft) & Kriti Badam (OpenAI, ex-Google, Codex, Kumo)
## Episode Overview
This episode dives into the concrete lessons and tactical advice that come from deploying over 50 AI products at leading companies such as OpenAI, Google, Amazon, and Databricks. Lenny interviews Aishwarya Raganti and Kriti Badam, who have “been in the weeds” launching and iterating on real-world AI products and now teach a highly-rated AI course for product leaders. The goal: help founders, PMs, and engineers avoid the painful pitfalls and wasted effort that plague AI products, and shift mindsets for the new way of building in the AI era.
## Key Discussion Points & Insights
### 1. How Building AI Products Differs from Traditional Software
  * **Non-determinism:**
    * AI products are powered by non-deterministic APIs (LLMs), so both user input and AI output are unpredictable.
    * Example: Unlike booking.com (deterministic workflow), an AI-powered interface must handle a huge range of natural language inputs and outputs.
    * **Quote — Aishwarya Raganti** (08:01): 
> "You don't know how your user might behave with your product, and you also don't know how the LLM might respond to that."
  * **Agency vs. Control Tradeoff:**
    * Giving more agency/autonomy to AI agents means relinquishing human control, so you need to calibrate and earn trust before increasing autonomy.
    * **Quote — Aishwarya Raganti** (10:18): 
> "The agency-control tradeoff ... every time you hand over decision-making to agentic systems, you're relinquishing some control."


### 2. The “Start Small” Approach: Agency and Control in Practice
  * **Build stepwise: high control, low agency → gradually increase autonomy.**
    * Don’t jump straight to fully autonomous agents (V3) — begin with humans fully in control and gather behavioral data.
    * **Example — Coding assistant:**
      * V1: Suggest small code snippets
      * V2: Suggest larger code blocks for human review
      * V3: AI autonomously creates and submits code changes (18:00)
  * **Example — Customer support agent:**
    * Start with AI suggesting answers to human agents
    * Collect data, increase agent autonomy as accuracy grows (13:38)


### 3. Why Organizations Struggle & How to Succeed
#### Success Factors (the “Triangle”)
  * **Leaders & Culture:**
    * Leaders need to get hands-on again, rebuild their intuition, and foster a culture of empowerment, not FOMO.
    * **Quote — Aishwarya Raganti** (25:43): 
> "Great leaders, good culture, and technical prowess ... Leaders have to get back to being hands on ... be comfortable with the fact that your intuitions might not be right."
  * **Subject Matter Experts:**
    * Their buy-in and expertise is critical for product tuning and training, but fear of replacement can poison collaboration.
  * **Technical Obsession with Workflows:**
    * Successful teams are experts in their data and workflow, not just AI tools, and iterate quickly to build reliable feedback loops.


#### Common Pitfalls
  * Skipping steps: Attempting to deploy fully autonomous agents before understanding the problem/data.
  * Not building feedback/evaluation loops.
  * Neglecting the messy, non-deterministic nature of both user and AI behavior.
  * Underestimating the challenge of enterprise data and taxonomies.


### 4. Evals, Metrics, and Monitoring
  * “Evals” now means too many things; don’t get hung up on terminology.
  * Evals are valuable (test known issues), but production monitoring is crucial to catch new and unexpected issues.
  * Use both: Evals (pre-deployment, regression), production metrics (live issues, customer signals), and iterate. **Quote — Kriti Badam** (33:46): 
> "There's this false dichotomy ... no reason to trust one of the extremes ... evals are important, production monitoring is important."


### 5. "Continuous Calibration, Continuous Development" (CCCD) Framework
  * **Iterative loop:**
    * Start with scoping, collecting input-output pairs, define evaluation metrics.
    * Deploy and evaluate with metrics and live feedback.
    * Analyze behaviors, spot patterns, and recalibrate with real-world user data.
  * **Progress agency gradually:**
    * Design systems for safe expansion from low-risk, human-in-the-loop to greater autonomy.
  * **Log human corrections and behaviors:**
    * Builds a data flywheel: system can improve reliably based on real feedback.
**Quote — Aishwarya Raganti** (46:17):
> "The idea is pretty simple ... continuous development ... you scope capability and curate data ... and then you set up the application and design evaluation metrics ... The second part is the continuous calibration ... you analyze your behavior, spot error patterns, apply fixes, and design new evaluation metrics as you go."


## Notable Quotes & Moments
**Agency-Control Tradeoff**
  * “If you give your AI agent more agency ... you are also losing some control ... you want to make sure the agent has earned that ability.” — Aishwarya Raganti (10:18)


**Start Small Pattern**
  * “Don't start with agents with all the tools and context you have on day one. You need to be deliberately starting in places where there is minimal impact and more human control.” — Kriti Badam (11:39)


**On Feedback/Evals**
  * “No company at OpenAI we talk to has never had been the case that, oh, AI cannot help me in this case ... there is this set of things that it can optimize for me.” — Kriti Badam (23:54)


**CCCD Framework**
  * “When you build with CCCD in mind ... it's all about minimizing surprise ... If you're not seeing new data distribution patterns, then you know you can actually go to the next stage.” — Aishwarya Raganti (58:18)


**Pain is the New Moat**
  * “Pain is the new moat ... As you are going through the pain of developing multiple approaches and then solving the problem, that pain is what translates into the moat of the company.” — Kriti Badam (73:00)


## Timestamps for Key Segments
| Timestamp | Segment / Insight | |-----------|---------------------------------------------------------------| | 00:08 | AI product building is fundamentally different (non-determinism, agency-control tradeoff) | | 05:54 | Transformation from slap-on-chatbots to deep workflow redesign | | 13:38 | Example: Customer support ai, progression from suggestion to autonomy | | 16:02 | Behavior calibration, constraining autonomy, and flywheel building | | 25:43 | The success triangle: leadership, culture, technical mastery | | 33:21 | The "evals" debate — production vs. preproduction evaluation | | 46:17 | CCCD Framework — stepping through the AI product lifecycle | | 57:16 | When to progress to the next stage of agency in AI calibration | | 61:24 | What’s over/underhyped; future vision for AI | | 68:52 | Key skills for AI product builders: taste, judgment, persistence, pain-as-mote| | 74:24 | Closing insights: Be obsessed with the customer & problem | | 75:27 | Lightning round: books, products, life mottos, mutual admiration |
## Practical Advice for AI Product Teams
  * **Prioritize problem clarity** (be “problem-first," not “solution/AI-first”).
  * **Begin with high human control and low autonomy.** Expand only as reliability and confidence increase.
  * **Build quick feedback loops** through evals and continuous monitoring—don’t rely on pre-production tests alone.
  * **Design your development cycle as iterative behavior calibration** , not a waterfall of features.
  * **Get leaders hands-on and foster a culture of empowerment and learning.
  * **Obsess over your data and workflow details.** Success rests on real-world, messy context, not just shiny models.
  * **Document human corrections and learnings** —these provide the feedback needed for system improvement.


## Memorable Takeaways
  * **“Pain is the new moat”** for AI products: Surviving the messy iteration, not just rushing to market, is the actual competitive advantage.
  * **Leadership is the #1 predictor** of successful AI adoption. CEOs/founders must engage and be deeply curious.
  * **Don't buy 'one-click AI agents':** Real enterprise deployments require deep workflow understanding and months of careful iteration.
  * **AI does not replace the need to know your customer & data—if anything, it demands even greater understanding.**
  * **The future is in multimodal and proactive “background agents”** —AI that anticipates needs and augments workflows proactively.


## Final Words
> “AI is just a tool. Try to make sure you're really understanding your workflows. 80% of so-called AI engineers and AI PMs spend their time actually understanding their workflows very well ... They’re not building the fanciest models...They're actually in the weeds." — Aishwarya Raganti (74:24)
### Resources and Further Links
  * Follow Aishwarya Raganti and Kriti Badam on LinkedIn for pragmatic AI product insights.
  * Their free GitHub resource repository: “Good Resources for Learning AI”
  * Highly-rated Maven course: "Building Enterprise AI Products" (see description for link)
  * CCCD framework visual & newsletter post (see episode links at Lenny's Podcast website)


This episode is essential listening for any founder or builder aiming to navigate the messy, fast-moving world of applied AI, with wisdom that applies far beyond just “AI" products.
What OpenAI and Google engineers learned deploying 50+ AI products in production - Lenny's Podcast: Product | Career | Growth | Wave AI Podcast Notes