# Why build this? What problem does it solve?

When searching for jobs, people usually suggest two strategies. Either tailor your resume perfectly to a small number of roles, researching the company, the culture, and the team to increase the chances that you get hired for that specific role.

Or you apply to a lot of companies and hope that the surface area is big enough that one of them will hit and you get a job from that. Or some kind of monstrous hybrid of these where you maintain multiple resumes for multiple roles.

I like asking questions. Maybe a bit too much at that. So I asked one question. Why? I asked why can't you have the best of both worlds. Why can't you apply to all the roles you're qualified for and maintain an ultra high quality of application material (Both the Resume and the Cover Letter)

These were the reasons I was given:

- It takes too much time, it will become another full time job.
- You can use AI to tailor but, you have to review output manually and AI isn't the best at what it does anyway. And if you're applying to a lot of jobs AI gets very expensive.
- Just follow what people have done before, don't try to reinvent the wheel.

So I told them something: What if I was able to design a system where you could apply to as many jobs as you want every single day, have the quality at a much higher level than a human with AI access could reasonably produce, and keep it cheap.

(I didn't know how to do it, I was just bluffing)

This is what I was told:

- All those three are three separately impossible things. Stick to building defensible CRUD apps.
- Entire engineering teams are built to solve the same kind of issue, nobody has been able to figure it out otherwise it would've been a mass market product already, you're wasting your time.
- You're overthinking everything, just apply to jobs like everyone else, you have a decent profile, some employer will take notice and give you a job
- I was laughed off saying AI output is unpredictable and hallucinated, by nature your output will be bad because you're choosing the wrong tool and I'm sinking my time into a blackhole.

I am no great one man engineering team, I am no "makes the impossible possible" 100x Engineer, I am a new grad looking for my first job. Tailor stemmed out of the belief I am qualified for most new grad roles being posted out there. I have worked with Python, C++, Java, I have productionized them, I know git, I know good coding and engineering practices, I know how to write good git commits, etc. etc.

As such, maybe I was naive in thinking that I just need to figure out how to tailor to every JD in a way to best represent my experience. That this is not an impossible problem, and simply a problem looking for the right architecture to solve it. So I told myself a white lie that I will solve every single one of these bottlenecks, for myself, so that I can make my job search more efficient. It wasn't easy. 18-hour days for 14 days straight. 

---
# What can it do?

The repository that you see in front of you is the solution to all the problems I was facing:

- It can tailor your resume and cover letter to an extent beyond what an average jobseeker with AI access could do in an hour or two. You don't have to worry about the quality; quality assurance is built into the architecture itself.
- If suddenly there are 50 new grad job postings in the past hour, and you need to apply to all of them, the architecture will rise to meet your demand. Be it 10, 20, 50, 100, 500, 1000, 2000, the only limiting factor is your API credits and your hardware.
- Every single resume and cover letter are ATS compatible, and optimised for human eye tracking as well to give you the best shot at the job application.
- If at any point for whatever reason the pipelines fail, not only will they recover and fix themselves automatically, they will tell you every single time in the learnings.yaml file where it's going wrong so that it can be permanently fixed. Once fixed, it won't occur again.

Again, there will be mistakes, there will be hallucinations, there will be problems, no system, not even AWS or Google or Instagram is perfect enough to guarantee there will never be any issue. But in the applications that this system has handled just from my side, I go thoroughly through every resume and cover letter outputted by it and have yet to notice a single misrepresentation of facts. That does not mean it is perfect, it just means the decisions I made were sound.

In a market where people have to submit 50k applications for just one callback, my numbers are nothing, and the system will be tested more and more as I keep using it for my daily applications more and more. That being said, empirically, it has given me enough confidence that if you asked me to apply to my dream role with Jobbernaut Tailor materials without double checking, it wouldn't be a very hard decision for me, I would do it in the blink of an eye.

---
# Is it a spam tool?

**Word of Caution:** This was not built to help you spam applications. There is a reason why you have to manually paste into the applications.yaml manually instead of simply automating it. It is an engineering piece. It is possible to build it with just a laptop and $5 worth of API credit. It is intentionally a nightmare to setup and tune for the average person. If you go through the commits you will realize that it was initially built to be compatible with any API, but I changed it to support only Poe. Because the Poe library is a pain to work with, you have to pay for it separately, and it is rate limited by design. The people who are technically skilled enough to even get it to work are the people I trust won't misuse this engineering piece and will appreciate the amount of effort that went into designing this.

The 100 applications at one time by lunch is an engineering goal that I set for myself, not what I want it to do every single day. It has the capability to handle that kind of volume is what you should take away. The true value from this system comes when you find 10 good high-quality job applications a day that you are a perfect fit for, then instead of tailoring each one for 2 - 3 hours, use Jobbernaut Tailor to do all of them in 1 minute, and use the rest 20 - 30 hours of your week on networking and good projects. You anyways need to decide and put a price on your time, I'm reducing that price to 10 cents an application and 12 - 15 hours of initial setup time.

To business competitors, I cannot in good faith issue an open source license for this project as this technology if made accessible will make the market worse for everyone. But, I cannot stop you either and request that you act in good faith. Contact me and I will guide you on monetization and how you can implement this tech to make the experience better for your customers.

---
# What do you have to gain?

To me, it is a statement that even when people tell me I can't do it, I will still figure it out. This is source available because I think it's a good way of showing employers how "I think" because its easy for me to learn or say oh I know Java, I know Flutter, but it's hard to showcase how I think. And this is how I think.

The stack, the technology, the programming language does not matter to me. I will learn. One way or the other, I will ask seniors, I will google it, and I will learn. I saw a problem, and I solved it, that's all I know. This system is a massive advantage to anyone who can use it effectively, and it is source available now because I'm confident that the advantage is not in this codebase but in my own skill. How I do anything is how I do everything, and this is how I do things. I make life easier for myself and the people around me. 

---

# How is it better than tailoring your resume manually?
1. **Sound Prompt Engineering:** Every single prompt that you see has been tuned over tens of thousands of iterations, contributed to by my extensive knowledge of LLMs.
2. **Linear Rolling-Context:** There are over 5-6 prompts working in conjuction with one output flowing from one pipeline to the other to keep costs in check. The quality generated by this kind of system is hard to match with the 1-2 prompts you can paste into Claude/ChatGPT.
3. **One Time Setup:** You have to set this codebase up just once. After that, you find jobs how many ever you want, and run one command, all the resumes/cover letters will be sitting in the output folder with a baseline guarantee that they're really good. If you are in a time crunch, you can directly submit them without checking. You don't have to trust me, see the output and gauge it yourself.
4. **Maintenance Guarantee:** I use this tool regularly myself, and if something doesn't work as intended it's a big issue for me, and I will be rushing to fix it. Who benefits from this? Anyone using it.
5. **Costs:** 20 USD a month for Claude/ChatGPT. If you keep tailoring on it, you will run out of the requests fast. For 20 USD in API tokens with Jobbernaut Tailor, you can submit 200 ultra high quality applications a month. And you don't have restrictions, it's completely upto you to make it cheaper or more expensive. The code is open after all.
6. **Speed:** ATS might go for stricter anti-AI measures, and I will always be 3 steps ahead because I apply on these systems regularly, and I can move at a pace they simply cannot. You are actually safer using this than manually tailoring it yourself when it comes to passing through the ATS.
7. **Resume and Cover Letter Factory:** A perfectly crafted and tailored resume/cover letter is a piece of art that will take you 3-4 hours. 3-4 hours that you could've spent on anything else for a small chance at one job. Like an Aston Martin. The problem I'm trying to solve is supply and demand. There are 30-40 new grad postings a day that I'm aware of that I'm perfectly qualified to apply. Where do I have time to tailor to all of them? So I built a factory that will push out top class resumes and cover letters like a factory assembly line. It checks itself at every point, by the time you get a coffee you have 40/50 application materials ready to send which are guaranteed to be better than a majority of the applicant pool because of the sophistication of this system.

---

# Why don't you monetize it, if it's that good?
Monetization is a completely different kind of game that I do not intend to play. Payments, marketing, making it easy to use, legal liability for building a mass application tool and taking payment for it is a nightmare of its own. I just want a job where I can apply my engineering skills to the max.

---

# How good is it? The metrics seem all inflated
I have heard the same thing about my resume as well. The metrics are too inflated to be true, the impact is too much for an intern to do at a large company. The task is too impossible to do. I am being punished for being really good at what I do. The code is open for you to verify, You can demo it on your own terms, you can see it run on your own system, and I am using it regularly, updating it regularly, Workday  automatically fills out when I upload Jobbernaut Tailor resumes, etc etc.

---

# Where are the sample outputs to verify the claims?
Set it up for yourself and run it on your own master resume. The magic feels more magical when it's happening right in front of you. You will not believe it even after sample outputs are given anyways, you'll say they were handcrafted and cherry picked so run it for yourself. 

---

# How is it so cheap at 10 cents?
10 cents is quite expensive by my standards. The architecture was designed in a way that only one step would require a large prompt and a SOTA model. I could possibly even rearchitect the system to bring the cost down to 5 cents, but there are diminishing returns from this point on, I already spent a lot of time designing this. Use the config that I'm using on the main branch and it will be the best tradeoff I promise.

---

# Did you use AI to write the code?
I used AI to write the code, I used AI to review the code, I used AI to review the pull requests, I used AI to write the documentation, I used the AI to evaluate architectural and cost tradeoffs. The difference is, the AI didn't wake up one day and think I have to design a 12-step pipeline and reduce the costs to be dirt cheap. I did. AI to me is a force multiplier. I have discarded over 5000 lines of AI generated code and documentation which you can see in my closed PRs and commits. I am very particular about the code that goes in, and I am very particular about the architecture. I scrutinize every single line of code that is written by the AI. Which is why I can give a strong guarantee that it won't just simply fail on you, it's designed to very high standards.

---

# How can you say that the AI doesn't hallucinate? That's impossible!
Of course AI hallucinates, why wouldn't it. That's the best part of this application. In v3.0 I made the validation so strict that it started generating sterile resumes and cover letters. That was the exact opposite of what I wanted from the project. Somewhere you have to take a risk, add a little bit of flair. And from my own empirical testing like I said, I have genuinely not seen a case of the AI inventing facts. Why could this be? The prompts are ultra detailed, and extremely constrained. Even if one single letter is missing from the field, self-healing will start. LLMs are probabilistic machines, and the prompts being so detailed along with the LLMs themselves being so good, along with the self-healing constrain it to a very specific output space.

If it hallucinates, it hallucinates in my favor. For example, a lot of JDs don't have technical keywords, so the technical keywords array will be empty in the first try, which will trigger self-healing, and now at the very top the LLM will see a message saying "Hey, in a previous attempt you return an empty tech array, that really can't happen, don't let it happen" so the AI will pull from its own training data hidden facts about the company and team giving me a leg-up. The goal is to get an interview without lying. Some marketing flair has to be there, that's the whole point.

---

# Why should I use your project over others?
I'm not trying to sell you on the project, I'm trying to solve my own problems. If you think it will solve the specific problems you have with the job search, you're free to use it and I will guide you. If you are not able to see the value, power, and danger behind this system then, be assured you are not the target audience, there are simpler solutions for you. Reach out to me, I will tell you how to supercharge your job search without an application of this much complexity.

---

# Why did something so simple and obvious take you 14 days? 
1. Figure out how to make one good tailored resume automatically [Find out what a good resume is, what tools are available to build your resume, etc.]
2. Figure out how to make one good tailored cover letter [Company Research, Storytelling arc, etc.]
3. Keep R&D/Prod costs cheap because I'm a student with no money [Aggressive Cost Optimization]
4. Figure out how ATS actually work, how recruiters read resume, and how to make one stand out [Eye Tracking and ATS Research]
5. Figure out how to make it catch mistakes by itself without me overseeing it [Validation]
6. Figure out how to make it recover from mistakes because I can't waste money [Self Healing]
7. Figure out how to learn from mistakes [learnings.yaml and debug/]
8. Figure out how to do this for 10 applications one at a time
9. Figure out how to do this for 10 applications all at once
10. Figure out how to do this for 100 applications all at once
11. Figure out how to do this for 100 applications all at once, every single day for however long possible without it failing on me. 

Each problem by itself is a months long deep dive and I'm proud of myself to get it done to a shippable state so quickly while not sacrificing quality. 

The fact that the final solution appears obvious, elegant, and too simple to people is a sign of good engineering taste and ability, not of the problem's nature. 
