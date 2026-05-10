 00:00:00

OpenAI is a company where we do spend some amount of time on planning yearly, quarterly, even monthly type basis just because these loops of development are just tightening more and more and more. Part of the planning is to really have some statements around here's what success looks like for us on this time horizon. What problem are we solving and being very, very clear on who is solving that problem.

00:00:24

And the further I do go, the more intrecise it gets or the more higher level that it gets. And then from there, there's the idea of like, OK, so here's what success for us looks like in this time horizon. Here's all the ways that we're going to measure that. And we do a fairly good job at disseminating that to the entire company and just just to make sure that we're extremely high trust environment as well, where people don't consider these to be competitive to each other. They're willing to or they have the humility to learn from each other as well and their explorations.

00:00:54

Hello and welcome to the Engineering Leadership Podcast brought to you by ELC, the engineering leadership community. I'm Jerry Lee, founder of ELC. And I'm Patrick Gallagher, and we're your hosts. Our show shares the most critical perspectives, habits, and examples of great software engineering leaders to help evolve leadership in the tech industry.

00:01:14

In this episode, we joined Solman Chowdhury, head of ChatGPT at OpenAI, live at the OpenAI podcast studio and office for an expansive conversation on how their engineering organization roles and workflows are changing. We talk about OpenAI's shift from silos to fluid mission-driven teams, running vertical versus horizontal team structures, maximizing cross-functional collaboration between research, engineering, product, and design, plus the directly responsible individual framework for high accountability.

00:01:44

Managers as system designers, scaling decision-making to prevent leadership from becoming bottlenecks. Frameworks for mentoring junior engineers, why problem framing is one of the most critical skills for engineers right now, and how engineering managers can stay close to problems and maintain technical intuition. Enjoy our conversation with Solman Chowdhury. So you and I talked a couple weeks ago to sort of ideate where we wanted to go. Since then, we had three different dinners with CTOs, sort of a lot of different scales of company size and team size.

00:02:13

And the kind of context of that conversation was people sort of wrestling with how teams are changing, how workflows are changing, and how that impacts productivity was like a big part of the conversation. Everybody was sort of representing these perspectives of how engineering is shifting as people are trying to become more AI native. And there was just a lot of sort of churn of what to do and what does it look like to do all these things. And I know this is an area where you've spent a considerable amount of time thinking and building and experimenting and have learned a lot along the way.

00:02:41

Our goal is to deconstruct all of your perspectives around teams and organizations, workflows, and how people in our community can help implement that. So I kind of want to start with how AI is reshaping teams and organizations for engineering. Maybe we can sort of talk about generally team composition, maybe where it started and how you're thinking about that right now. And I've got maybe a lot of ways we can kind of deconstruct that, but let's just start with team composition. And maybe I'll take in a slightly different way.

00:03:07

I'll start by answering what has not changed and then we can get into what has changed. If I think about how engineers spend their time, engineers at the end of the day are builders, and we should probably talk about it later. Engineers don't have to be the only functioners that are builders. AI is changing where everyone gets to become a builder. But an engineer, at the end of the day, their job is to really look at a problem, understand that problem, figure out or break that problem into sub-problems, and then oftentimes write code to solve that problem.

00:03:34

And then after they write the code, they test the code and all of that. Once it's ready, they put it in production. And in production, they're getting signals and learnings and all of that. And then they're iterating and that cycle just continues to repeat itself. And the idea here is that they're building and they're maximizing value for the user. So if you think about it, there's two different loops that are here. There's an inner loop of engineers writing code and all of that and shipping code. And then there's the outer loop of like once you ship the code, how do you get the signals?

00:04:04

How do you get the learnings? And how do you then maximize user value? So the biggest thing, well, the thing that has not changed is that there's still this idea of an inner loop and an outer loop. But then the biggest thing that is changing is that that inner loop is just getting tighter and tighter and tighter. And AI is driving extreme amount of efficiency in that inner loop. And I would argue that it is collapsing the cost of generating code to be the cost of generating tokens. And that cost is also just getting closer and closer to zero.

00:04:34

So that's a big framework here that I have in mind of this inner loop and outer loop. And the idea that the inner loop is the one where we're experiencing a crazy amount of efficiencies and productivity gains for users or for engineers. So when you start to think about like the dynamics there, then how do you start to approach forming teams? You know, for example, there's like so many different product services at OpenAI and like specifically within ChatGPT. Like how do you even start to begin to orient teams around being AI native or across all these different product services?

00:05:03

Like what is what does that start to look like? So we've iterated a lot at OpenAI on what is the best way for us to organize ourselves. And I would say, let's say two years ago or so, were very much a research lab that was just learning how to build and ship product. And it's ironic that I say that because even at that time, ChatGPT was the fastest growing product in the history of all products and the fastest growing business. But as a company, we have always been very much a research company that happens to have a very successful product.

00:05:31

So back then, a lot of our take was that we would have these amazing researchers that continue to iterate on models and they improve models. And then at some point, they would hit different types of breakthroughs. And once they have those breakthroughs, we would we would then start to collaborate with the engineering team on like, here's this amazing model breakthrough and find a way to bring it to the user and to expose that that value to the user. As we've all learned in our careers, that anytime you throw things over the wall, things just don't go well.

00:06:01

So the big learning for us was that we need to get all these functions and all these people working much more closely together. So since then, we are orienting many, if not all of our teams around this idea of end to end teams. And in these end to end teams, traditionally, you would have your engineers and data scientists and designers and PMs. But then we also throw in one more function to the mix, which is researchers.

00:06:24

And all of them are very much aligned behind specific ideas or specific user problems or metrics or any of that. And then they're iterating together in pursuit of that model breakthrough as well as a product breakthrough. And that leads to the best possible outcomes for us. A really good example of it is search that when we decided to take on the problem of ChatGPT needs to have access to as much real-time information as possible.

00:06:50

We effectively got a group of probably half a dozen or so people across different functions, just gave them that problem space and then gave them literally a month or two to really think about how to solve that problem and iterate towards solving that problem. And that's where ChatGPT search came from. I want to dive into how some of those teams operate together because in these conversations with folks on our team, this cross-functional relationship is becoming so much more seamless and smooth and you can incorporate so many different collaborators.

00:07:16

And then I think to link together another part of OpenAI is a much more horizontal engineering team culture, sort of having the people closest to the code be involved end to end. And so I think those are dynamics that folks are starting to feel that trend and the push in that direction. But there's a sort of gap of like, how do I get there? And how did those teams work together in sort of that way? And so I was wondering if you kind of talked to us a little bit more about, you know, when you have research scientists, infrastructure engineers, product engineers, designers, and PMs around one of those initiatives, how does that all work together to then come together with search?

00:07:46

One thing that I would say in terms of org design is that we're also very explicit about what is a horizontal and what is a vertical. So a lot of product teams are very much vertical teams, but then we also have horizontal teams. So a really good example of it is that when we launched our multimodal 4.0, which was our first natively multimodal model, and we had to launch Advanced Voice. Advanced Voice relied on some pretty deep voice and RTC infrastructure.

00:08:14

And at that time, we had absolutely no expertise there. So we did have a vertical team, which is a product team that was responsible for launching Advanced Voice and did a fairly reasonable job. But then very quickly, we realized that if OpenAI is going to take multimodal very seriously, we need a horizontal team. So we very explicitly started a team that was solely responsible for creating the infrastructure needed for real-time communication, not just for that team, but for all the teams at OpenAI as well.

00:08:40

So the first thing that I would say is that we continue to have horizontal teams, but we're very clear about which teams are horizontal and which teams are very vertical. And at the same time, we have good alignment of dependencies across those teams. And then on our vertical teams, what I have noticed is that that distinction across functions is just starting to blur over time. A very obvious example of it is that researchers are not the only ones who can train models now.

... 79 more lines
