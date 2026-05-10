# If You Don’t Understand AI Evals, Don’t Build AI

Channel: Aakash Gupta

Ankur Goyal is the Founder and CEO of Braintrust, the AI eval platform used by Replit, Vercel, Airtable, Ramp, Zapier, and Notion, valued at $800 million. In this episode, we break down why evals are the new PRD, build an eval from scratch using Linear's MCP server, and walk through the data-task-scores framework every PM needs to master.

Full Writeup: https://www.news.aakashg.com/p/ankur-goyal-podcast
Transcript: https://www.aakashg.com/ankur-goyal-podcast/

---

Timestamps:

0:00 - Intro
1:43 - Why should anyone care about evals
3:21 - LLMs are imperfect yet capable
6:35 - The role of the PM in defining evals
8:45 - The Claude Code evals controversy
11:34 - Ads
13:05 - Distance from the end user determines eval need
14:27 - How big is Braintrust today
18:48 - Building an eval from scratch (live demo)
20:20 - Ads
22:15 - Creating the data set and scoring function
30:20 - Ads
33:01 - Iterating on prompt and MCP tools
39:12 - Why you need evals that fail
43:36 - Offline vs online evals
47:40 - How to maintain eval culture
50:00 - Outro

---

🏆 Thanks to our sponsors:

1. Kameleoon: Leading AI experimentation platform - http://www.kameleoon.com/
2. Testkube: Leading test orchestration platform - http://testkube.io/
3. Pendo: The #1 software experience management platform - http://www.pendo.io/aakash
4. Bolt: Ship AI-powered products 10x faster - https://bolt.new/solutions/product-manager?utm_source=Promoted&utm_medium=email&utm_campaign=aakash-product-growth
5. Product Faculty: Get $550 off their #1 AI PM Certification with my link - https://maven.com/product-faculty/ai-product-management-certification?promoCode=AAKASH550C7

---

Key Takeaways:

1. Vibe checks are evals - When you look at an AI output and intuit whether it is good or bad, you are using your brain as a scoring function. It is evaluation. It just does not scale past one person and a handful of examples.

2. Every eval has three parts - Data (a set of inputs), Task (generates an output), and Scores (rates the output between 0 and 1). That normalization forces comparability across time.

3. Evals are the new PRD - In 2015, a PRD was an unstructured document nobody followed. In 2026, the modern PRD is an eval the whole team can run to quantify product quality.

4. Start with imperfect data - Auto-generate test questions with a model. Do not spend a month building a golden data set. Jump in and iterate from your first experiment.

5. The distance principle - The farther you are from the end user, the more critical evals become. Anthropic can vibe check Claude Code because engineers are the users. Healthcare AI teams cannot.

6. Use categorical scoring, not freeform numbers - Give the scorer three clear options (full answer, partial, no answer) instead of asking an LLM to produce an arbitrary number.

7. Evals compound, prompts do not - Models and frameworks change every few months. If you encode what your users need as evals, that investment survives every model swap.

8. Have evals that fail - If everything passes, you have blind spots. Keep failing evals as a roadmap and rerun them every time a new model drops.

9. Build the offline-to-online flywheel - Offline evals test your hypothesis. Online evals run the same scorers on production logs. The gap between them is your improvement roadmap.

10. The best teams review production logs every morning - They find novel patterns, add them to the data set, and iterate all day. That morning ritual is what separates teams that ship blind from teams that ship with confidence.

---

👨‍💻 Where to find Ankur Goyal:
LinkedIn: https://www.linkedin.com/in/ankrgyl/
Braintrust: https://www.braintrust.dev
X: https://x.com/ankrgyl

👨‍💻 Where to find Aakash:
Twitter: https://x.com/aakashgupta
LinkedIn: https://www.linkedin.com/in/aakashgupta/
Newsletter: https://www.news.aakashg.com

#aievals #aipm 

---

🧠 About Product Growth:

The world's largest podcast focused solely on product + growth, with over 200K+ listeners.
🔔 Subscribe and turn on notifications to get more videos like this.

Source: https://www.youtube.com/watch?v=71qvIkO9d_A
