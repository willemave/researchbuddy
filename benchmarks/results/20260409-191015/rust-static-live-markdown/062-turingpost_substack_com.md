On March 2, the Financial Times reported that Reflection AI is raising at least another $2 billion, with its potential valuation approaching $20 billion. This follows a rapid series of raises: the company emerged from stealth in March 2025 with $130 million and a valuation of around $545 million, then raised $2 billion at an $8 billion valuation in October 2025, and is now back in the market again. Reflection frames its mission in the language of openness and open science. The awkward part is that, as of early March 2026, the frontier open-weight model at the center of its pitch still has not been released publicly, its code research agent Asimov remains on a waitlist, and the company’s website features product docs and blog posts but no research papers.

As it happened, we had recently spoken with Ioannis Antonoglou, co-founder and CTO of Reflection AI. I came away from that conversation with more doubts than answers, which made Reflection a natural fit for a deep-dive episode in our GenAI Unicorns series: either to dispel those doubts, or to confirm them.

What are they actually building? Why has it all been so slow and secretive if the promise is openness? Is it realistic that their much-discussed open-weight model could outperform the closed labs and Chinese contenders? How are they planning to make money? Is government demand alone enough to sustain the business? There is a lot to unpack.

Now let’s take a look at what’s brewing inside the Reflection AI lab.

**In today’s episode:**

- *Starting point of Reflection AI*

- *From autonomous coding to the “missing Western open model”*

- *“$2 billions later…” What Reflection has actually built so far*

- *What “open” means here, and what it does not*

- *Can Reflection realistically beat closed labs and Chinese contenders?*

- *Business strategy: Sovereignty, enterprises, and governments*

- *How big is the sovereign AI market, really?*

- *What would make the strategy more believable*

- *Conclusion*

- *Bonus: Resources*

Ioannis Antonoglou carries the original “AGI virus” of early DeepMind: the belief that AGI belongs first to science, as a serious research program, before it becomes a product category. He joined Shane Legg and Demis Hassabis as one of the founding engineers in 2012, at a time when working on that kind of thing still seemed almost weird, and when it was nearly impossible to imagine valuations for such startups becoming this silly. He later worked on the now-legendary DQN, AlphaGo, AlphaZero, and MuZero, and eventually on Gemini-related post-training at Google DeepMind. Across his public appearances, and in conversation, he comes across less like a startup salesman than like a mission-driven reinforcement learning lifer who simply never stopped believing that the road to AGI runs through agents that learn by doing.

Misha Laskin is different in temperament, but not in seriousness. Before Reflection, he worked on Gemini at DeepMind, after a Berkeley postdoc and an earlier startup detour. On his personal site he still describes himself as someone interested in how RL can unlock new capabilities in language and multimodal models. According to the public founder mythology, reading AlphaGo paper changed the course of his life. That sounds dramatic, but in AI this is practically a genre.

The two met at Google DeepMind, where Antonoglou was leading post-training efforts for Gemini and Laskin was leading reward model development in RLHF team. They **knew extremely well how to train and scale reinforcement learning systems**, especially in post-training, reward modeling, and building agents that improve through interaction and feedback.

What they felt was missing was **a reliable general-purpose product surface**: language models gave breadth, but not depth or dependable autonomy. In their view, the missing piece was combining LLM generality with RL-driven capability to create agents that can actually do useful work end to end. They left comfortable job in Google DeepMind and, in late February-early March 2024, started working on Reflection AI.

The whole year they were in stealth. In March 2025, Reflection AI emerged publicly with this thesis: building superintelligent autonomous systems, starting with autonomous coding. Its official two-step plan was simple: first build a superintelligent autonomous coding system, then use that blueprint to expand to other categories of computer-based work. The logic was straightforward enough to be compelling. Coding is measurable, digital, tool-rich, and close to the operating system of modern knowledge work.

Wonderful plan. Other companies were already shipping exactly that. Anthropic, for example, had just launched Claude Code in February 2025, which quickly became a flagship product and changed the way we think about coding.

You might think they doubled down on openness because Claude Code was not open and DeepSeek, along with other Chinese models, was tearing through the market with high-quality open models. But no. In Lightspeed’s announcement about Reflection’s Series A, openness didn’t feature at all:
> Reflection AI is leveraging its deep expertise in reinforcement learning and large language models to solve autonomous coding – and, more broadly, unlock the path to superintelligence.
>
> From Lightspeed blog, March 2025

By the October 2025 Series B, the messaging had shifted:
> We’re building frontier open intelligence accessible to all.
>
> From Reflection AI’s announcement, October 2025

In our conversation, Antonoglou explained the logic behind this pivot: “If you want to do reinforcement learning at the frontier, you need an extremely powerful base model to post-train,” he said. “What we saw – especially with Llama 4 not being a particularly strong model – was that the whole Western ecosystem was missing a powerful open base model that we could even use to do reinforcement learning at scale. We realized this was a gap we were the only ones positioned to fill.”

I pressed on whether this meant the target was still a coding model. “It’s a general agent model,” he said. Why the change? “Because we think it’s important that there is a general open model in the West – and there isn’t one. So we have to build it.”

This pivot might be rational. But It is also dangerous. Rational, because RL-heavy post-training only gets you so far if the base model is weak. Dangerous, because it turns a wedge product into a civilization project. An autonomous coding company can ship product, iterate with customers, and build revenue while improving its models. A company trying to build the missing Western open frontier base model is now competing at the deepest layer of the stack, where the incumbents have more compute, more data, more iteration cycles, and more room for error.

What makes the danger concrete is how candidly Antonoglou described the current state. When I asked about applications, he said, very plainly: “The focus right now is just to build the models. Applications will follow, but it’s all hands on deck. Building this model is challenging and requires all of our mental focus.” When I asked how it was going, the answer was a non-answer: “There are lots of incredible things we’ll have to share this year.” **This might be a decent research strategy. It is much less obviously a startup strategy.**

That tension matters because Reflection’s original public promise was not “trust us, we are building a general open agent model from scratch and the applications can wait.” It was autonomous coding, then superintelligence. Now the company is basically saying: yes, but in order to do autonomous coding properly we first need to build the frontier open model that the rest of the Western ecosystem failed to build. That may turn out to be true. It also means the company has chosen the slowest possible road in the fastest market.

[https://www.youtube-nocookie.com/embed/zd3B8sNNgmk?rel=0&amp;autoplay=0&amp;showinfo=0&amp;enablejsapi=0](https://www.youtube-nocookie.com/embed/zd3B8sNNgmk?rel=0&amp;autoplay=0&amp;showinfo=0&amp;enablejsapi=0)

[Read further for free](https://www.turingpost.com/p/reflectionai)
