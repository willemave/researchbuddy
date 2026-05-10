> *There’s a company who spent almost $50,000 because an agent went into an infinite loop and they forgot about it for a month.*
>
> *It had no failures and I guess no one was monitoring these costs. It’s nice that people do write about that in the database as well. After it happened, they said: watch out for infinite loops. Watch out for cascading tool failures. Watch out for silent failures where the agent reports it has succeeded when it didn’t!*

**We Discuss:**

- Why the most successful teams are **ripping out and rebuilding their agent systems every few weeks** as models improve, and why over-engineering now creates technical debt you can’t afford later;

- The **$50,000 infinite loop disaster** and why “silent failures” are the biggest risk in production: agents confidently report success while spiraling into expensive mistakes;

- How **ELIOS built emergency voice agents** with sub-400ms response times by aggressively throwing away context every few seconds, and why these extreme patterns are becoming standard practice;

- Why **DoorDash uses a three-tier agent architecture** (manager, progress tracker, and specialists) with a persistent workspace that lets agents collaborate across hours or days;

- Why simple **text files and markdown** are emerging as the best “continual learning” layer: human-readable memory that persists across sessions without fine-tuning models;

- The **100-to-1 problem**: for every useful output, tool-calling agents generate 100 tokens of noise, and the three tactics (reduce, offload, isolate) teams use to manage it;

- Why companies are **choosing Gemini Flash for document processing and Opus for long reasoning chains**, and how to match models to your actual usage patterns;

- The debate over **vector databases versus simple grep and cat**, and why giving agents standard command-line tools often beats complex APIs;

- What **“re-architect” as a job title** reveals about the shift from 70% scaffolding / 30% model to 90% model / 10% scaffolding, and why knowing when to rip things out is the may be the most important skill today.

You can also find the full episode on [Spotify](https://open.spotify.com/show/3yuz89gqAhcMcdy3SZPe4X?si=AKl2jvIARD2Liw1bBH2Nng&nd=1&dlsi=8dfe7221896c4fc3), [Apple Podcasts](https://podcasts.apple.com/us/podcast/vanishing-gradients/id1610318868), and [YouTube](https://www.youtube.com/live/uf80BfD70Lw?si=RtkR2C5aYqBea2Us).

[You can also interact directly with the transcript here in NotebookLM](https://notebooklm.google.com/notebook/ceef53be-ffe8-47d5-8850-07335c434100): If you do so, let us know anything you find in the comments!

[https://www.youtube-nocookie.com/embed/uf80BfD70Lw?rel=0&amp;autoplay=0&amp;showinfo=0&amp;enablejsapi=0](https://www.youtube-nocookie.com/embed/uf80BfD70Lw?rel=0&amp;autoplay=0&amp;showinfo=0&amp;enablejsapi=0)

👉 ***Want to learn more about Building AI-Powered Software? Check out our [Building AI Applications course](https://maven.com/hugo-stefan/building-ai-apps-ds-and-swe-from-first-principles?promoCode=ss-rav)***. It’s a live cohort with hands on exercises and office hours. **Our final cohort starts March 10, 2026**. Here is a [25% discount code](https://maven.com/hugo-stefan/building-ai-apps-ds-and-swe-from-first-principles?promoCode=vgch) for readers. 👈

- [Alex Strick van Linschoten on LinkedIn](https://www.linkedin.com/in/strickvl/)

- [Alex Strick van Linschoten on Twitter/X](https://x.com/strickvl)

- [LLMOps Database](https://www.zenml.io/llmops-database)

- [LLMOps Database Dataset on Hugging Face](https://huggingface.co/datasets/zenml/llmops-database)

- [Hugo’s MCP Server for LLMOps Database](https://huggingface.co/spaces/hugobowne/llmops-database-mcp)

- [Alex’s Blog: What 1,200+ Production Deployments Reveal About LLMOps in 2025](https://www.zenml.io/blog/what-1200-production-deployments-reveal-about-llmops-in-2025)

- [Previous Episode: Practical Lessons from 750 Real-World LLM Deployments](https://hugobowne.substack.com/p/practical-lessons-from-750-real-world)

- [Previous Episode: Tales from 400 LLM Deployments](https://hugobowne.substack.com/p/episode-43-tales-from-400-llm-deployments-f60)

- [Context Rot Research by Chroma](https://research.trychroma.com/context-rot)

- [Hugo’s Post: AI Agent Harness - 3 Principles for Context Engineering](https://hugobowne.substack.com/p/ai-agent-harness-3-principles-for)

- [Hugo’s Post: The Rise of Agentic Search](https://hugobowne.substack.com/p/the-rise-of-agentic-search)

- [Episode with Nick Moy: The Post-Coding Era](https://high-signal.delphina.ai/episode/the-post-coding-era-what-happens-when-ai-writes-the-system)

- [Hugo’s Personal Podcast Prep Skill Gist](https://gist.github.com/hugobowne/959419146f1a8276c78511e801b85e40)

- [Claude Tool Search Documentation](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)

- [Gastown on GitHub (Steve Yegge)](https://github.com/steveyegge/gastown)

- [Welcome to Gastown by Steve Yegge](https://steve-yegge.medium.com/welcome-to-gas-town-4f25ee16dd04)

- [ZenML - Open Source MLOps & LLMOps Framework](https://www.zenml.io)

- [Upcoming Events on Luma](https://luma.com/calendar/cal-8ImWFDQ3IEIxNWk)

- [Vanishing Gradients on YouTube](https://www.youtube.com/@vanishinggradients)

- [Watch the podcast livestream on YouTube](https://www.youtube.com/live/uf80BfD70Lw?si=RtkR2C5aYqBea2Us)

- [Join the final cohort of our Building AI Applications course in March, 2026 (25% off for listeners)](https://maven.com/hugo-stefan/building-ai-apps-ds-and-swe-from-first-principles?promoCode=vgfs)

👉 ***Want to learn more about Building AI-Powered Software? Check out our [Building AI Applications course](https://maven.com/hugo-stefan/building-ai-apps-ds-and-swe-from-first-principles?promoCode=ss-rav)***. It’s a live cohort with hands on exercises and office hours. **Our final cohort starts March 10, 2026**. Here is a [25% discount code](https://maven.com/hugo-stefan/building-ai-apps-ds-and-swe-from-first-principles?promoCode=vgch) for readers. 👈
