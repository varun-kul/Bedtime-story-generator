# Hippocratic AI Coding Assignment
Welcome to the [Hippocratic AI](https://www.hippocraticai.com) coding assignment

## Instructions
The attached code is a simple python script skeleton. Your goal is to take any simple bedtime story request and use prompting to tell a story appropriate for ages 5 to 10.
- Incorporate a LLM judge to improve the quality of the story
- Provide a block diagram of the system you create that illustrates the flow of the prompts and the interaction between judge, storyteller, user, and any other components you add
- Do not change the openAI model that is being used. 
- Please use your own openAI key, but do not include it in your final submission.
- Otherwise, you may change any code you like or add any files

---

## How to run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your OpenAI API key
```bash
export OPENAI_API_KEY="sk-..."   # macOS / Linux
set OPENAI_API_KEY=sk-...        # Windows CMD
```

### 3. Run the script
```bash
python main.py
```

You will be prompted to enter a story request. Press Enter with no input to use the built-in example request.

---

## System design

### Components

| Component | Role |
|---|---|
| **User** | Types a free-form story request |
| **Storyteller LLM** | GPT-3.5-turbo with a detailed system prompt — writes a 300-450 word bedtime story following a 3-act arc |
| **LLM Judge** | GPT-3.5-turbo with a separate evaluation system prompt — scores the story on 5 criteria and returns PASS or FAIL |
| **Revision loop** | If the judge returns FAIL, its feedback is injected back into the storyteller's prompt for a retry (max 2 retries) |

### Block diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                            USER                                 │
│                     (story request)                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │ prompt
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STORYTELLER LLM                              │
│               (gpt-3.5-turbo, temp=0.8)                        │
│  System prompt: age 5-10, 3-act arc, soothing tone, 300-450w   │
└───────────────────────────┬─────────────────────────────────────┘
                            │ draft story
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LLM JUDGE                                  │
│               (gpt-3.5-turbo, temp=0.2)                        │
│  Scores: age fit · story arc · calm tone · engagement · moral  │
│  Verdict: PASS (avg ≥ 3.5, all ≥ 3)  or  FAIL + feedback      │
└──────────┬──────────────────────────────────────┬──────────────┘
           │ FAIL + feedback                       │ PASS
           │ (max 2 retries)                       │
           ▼                                       ▼
   back to STORYTELLER                    ┌─────────────────┐
   with feedback injected                 │  FINAL STORY    │
   into the next prompt                   │  shown to user  │
                                          └─────────────────┘
```

### Prompting strategies used

- **Dedicated system prompts** — the storyteller and judge each have their own system prompt, keeping their roles cleanly separated.
- **Structured judge output** — the judge is instructed to respond in a rigid, machine-readable format (`SCORES: … VERDICT: … FEEDBACK: …`) so parsing is reliable.
- **Feedback injection** — on a FAIL, the judge's bullet-point feedback is appended to the storyteller's next user message, giving the model concrete instructions for improvement rather than asking it to "do better".
- **Temperature tuning** — storyteller uses `temperature=0.8` for creative variety; judge uses `temperature=0.2` for consistent, repeatable scoring.
- **Soft landing** — if the story still fails after `MAX_REVISIONS` retries, the best available story is shown rather than crashing or returning nothing.

---

## Rules
- This assignment is open-ended
- You may use any resources you like with the following restrictions
   - They must be resources that would be available to you if you worked here (so no other humans, no closed AIs, no unlicensed code, etc.)
   - Allowed resources include but not limited to Stack overflow, random blogs, chatGPT et al
   - You have to be able to explain how the code works, even if chatGPT wrote it
- DO NOT PUSH THE API KEY TO GITHUB. OpenAI will automatically delete it

---

## What does "tell a story" mean?
It should be appropriate for ages 5-10. Other than that it's up to you. Here are some ideas to help get the brain-juices flowing!
- Use story arcs to tell better stories
- Allow the user to provide feedback or request changes
- Categorize the request and use a tailored generation strategy for each category

---

## How will I be evaluated
Good question. We want to know the following:
- The efficacy of the system you design to create a good story
- Are you comfortable using and writing a python script
- What kinds of prompting strategies and agent design strategies do you use
- Are the stories your tool creates good?
- Can you understand and deconstruct a problem
- Can you operate in an open-ended environment
- Can you surprise us

---

## Other FAQs
- How long should I spend on this? 
No more than 2-3 hours
- Can I change what the input is? 
Sure
- How long should the story be?
You decide