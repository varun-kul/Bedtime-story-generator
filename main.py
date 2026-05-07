import os
import openai

"""
Before submitting the assignment, describe here in a few sentences what you would have built next
if you spent 2 more hours on this project:

I would have added an interactive feedback loop where the child (or parent) can request changes
mid-story — e.g. "make it funnier" or "add a dragon" — and the storyteller would revise while
the judge re-evaluates. I would also have added text-to-speech output using the `pyttsx3` library
so the story could be read aloud as a proper bedtime story, and a story-category classifier to
tailor the narrative arc (adventure vs. lullaby vs. lesson-based) before generation begins.
"""

# ── constants ─────────────────────────────────────────────────────────────────

MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 1200
TEMPERATURE_STORY = 0.8   # creative / varied
TEMPERATURE_JUDGE = 0.2   # consistent / analytical
MAX_REVISIONS = 2          # max times the judge can send the story back for revision

# ── low-level API call ────────────────────────────────────────────────────────

def call_model(messages: list, max_tokens: int = MAX_TOKENS, temperature: float = 0.7) -> str:
    """Send a list of chat messages to the model and return the reply text."""
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()  # type: ignore

# ── storyteller ───────────────────────────────────────────────────────────────

STORYTELLER_SYSTEM = """You are a warm, imaginative bedtime storyteller for children aged 5-10.

Rules you always follow:
- Use simple vocabulary a 5-year-old can understand, but keep it engaging for a 10-year-old.
- Every story has a clear three-part arc: a cozy Setup, a gentle Challenge, and a satisfying Resolution.
- Every story ends on a calm, sleepy, positive note — perfect for drifting off to sleep.
- Stories are 300-450 words — long enough to be satisfying, short enough for bedtime.
- No scary monsters, violence, or sad endings.
- Weave in a gentle moral lesson naturally (e.g., kindness, bravery, sharing) without being preachy.
- Use vivid but soothing sensory details (soft moonlight, warm blankets, firefly glow, etc.)."""


def generate_story(user_request: str, feedback: str = "") -> str:
    """Generate (or revise) a bedtime story based on the user request and optional judge feedback."""
    user_message = f"Please write a bedtime story about: {user_request}"
    if feedback:
        user_message += (
            f"\n\nA story quality reviewer gave this feedback on your last attempt — "
            f"please fix these issues:\n{feedback}"
        )
    messages = [
        {"role": "system", "content": STORYTELLER_SYSTEM},
        {"role": "user",   "content": user_message},
    ]
    return call_model(messages, temperature=TEMPERATURE_STORY)

# ── LLM judge ─────────────────────────────────────────────────────────────────

JUDGE_SYSTEM = """You are a strict but fair children's story quality judge.
Your job: evaluate a bedtime story for children aged 5-10 against five criteria.

Score each criterion 1-5, then give an overall PASS or FAIL.
PASS requires: every criterion scored 3 or above AND an overall average of 3.5 or above.

Criteria:
1. Age-appropriateness  — vocabulary, concepts, and themes suit ages 5-10.
2. Story arc            — clear setup, challenge, and resolution are all present.
3. Bedtime suitability  — calm, soothing tone; ends on a peaceful note.
4. Engagement           — imaginative, fun, and keeps the child's attention.
5. Gentle moral lesson  — a positive value is naturally embedded in the story.

Respond ONLY in this exact format (no extra text before or after):

SCORES:
1. Age-appropriateness: X/5
2. Story arc: X/5
3. Bedtime suitability: X/5
4. Engagement: X/5
5. Gentle moral lesson: X/5

VERDICT: PASS

FEEDBACK (only if FAIL — write bullet points of exactly what must be improved):
- ..."""


def judge_story(story: str) -> tuple:
    """
    Run the LLM judge on a story.
    Returns (passed: bool, feedback: str, raw_evaluation: str).
    """
    messages = [
        {"role": "system", "content": JUDGE_SYSTEM},
        {"role": "user",   "content": f"Please evaluate this bedtime story:\n\n{story}"},
    ]
    raw = call_model(messages, max_tokens=400, temperature=TEMPERATURE_JUDGE)

    passed = "VERDICT: PASS" in raw

    feedback = ""
    if not passed and "FEEDBACK" in raw:
        feedback = raw.split("FEEDBACK", 1)[1].strip()
        if feedback.startswith("(only if FAIL"):
            feedback = feedback.split(":", 1)[-1].strip()

    print("\n── Judge Evaluation ──────────────────────────────────")
    print(raw)
    print("─────────────────────────────────────────────────────\n")

    return passed, feedback, raw

# ── main pipeline ─────────────────────────────────────────────────────────────

example_requests = "A story about a girl named Alice and her best friend Bob, who happens to be a cat."


def main():
    print("🌙  Welcome to the Bedtime Story Generator  🌙")
    print("────────────────────────────────────────────────")
    user_input = input("What kind of story would you like tonight? → ").strip()
    if not user_input:
        user_input = example_requests

    story = ""
    feedback = ""
    judge_log = []   # collect all judge evaluations for the output file

    for attempt in range(1, MAX_REVISIONS + 2):   # up to MAX_REVISIONS + 1 total attempts
        print(f"\n✍️  Storyteller writing story (attempt {attempt} of {MAX_REVISIONS + 1})…")
        story = generate_story(user_input, feedback)

        print(f"\n🧑‍⚖️  Sending to judge…")
        passed, feedback, raw_evaluation = judge_story(story)
        judge_log.append((attempt, raw_evaluation, passed))

        if passed:
            print(f"✅  Judge approved the story on attempt {attempt}!\n")
            break
        elif attempt <= MAX_REVISIONS:
            print(f"❌  Judge requested revisions. Storyteller will try again…\n")
        else:
            print(f"⚠️  Max revisions reached. Presenting best available story.\n")

    print("════════════════════════════════════════════════")
    print("🌟  YOUR BEDTIME STORY  🌟")
    print("════════════════════════════════════════════════\n")
    print(story)
    print("\n════════════════════════════════════════════════")
    print("🌙  Sweet dreams!  🌙")

    # ── Save output to file ───────────────────────────────────
    output_filename = "story_output.txt"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("YOUR BEDTIME STORY\n")
        f.write("=" * 48 + "\n\n")
        f.write(f"Request: {user_input}\n\n")
        f.write("=" * 48 + "\n\n")
        f.write(story)
        f.write("\n\n" + "=" * 48 + "\n")
        f.write("Sweet dreams!\n\n")

        f.write("\n" + "=" * 48 + "\n")
        f.write("JUDGE EVALUATION LOG\n")
        f.write("=" * 48 + "\n\n")
        for attempt, raw_evaluation, passed in judge_log:
            f.write(f"── Attempt {attempt} ──────────────────────────────\n")
            f.write(raw_evaluation)
            f.write("\n")
            f.write(f"RESULT: {'✅ PASS' if passed else '❌ FAIL'}\n")
            f.write("-" * 48 + "\n\n")

    print(f"\n📄  Story saved to: {output_filename}")


if __name__ == "__main__":
    main()