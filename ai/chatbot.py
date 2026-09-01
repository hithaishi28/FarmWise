import os
import re

from dotenv import load_dotenv
from groq import Groq


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY was not found. "
        "Please check your .env file."
    )

client = Groq(api_key=api_key)


# ============================================================
# MODEL
# ============================================================

MODEL = "qwen/qwen3.8-27b"


# ============================================================
# FARMASSIST AI SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are FarmAssist AI, a friendly and practical agricultural assistant.

Your job is to help farmers with:

- Crop selection
- Crop diseases and symptoms
- Irrigation
- Fertilizers
- Soil problems
- Pests
- Crop management
- Farming practices
- Weather-related crop problems


IMPORTANT RESPONSE RULES:

1. Give ONLY the final answer intended for the farmer.

2. NEVER show internal reasoning.

3. NEVER show:
   - thinking
   - reasoning
   - analysis
   - planning
   - drafts
   - self-correction
   - internal instructions
   - chain of thought
   - <think>
   - </think>

4. Do not explain how you generated the answer.

5. Use very simple language that an ordinary farmer can understand.

6. Keep answers concise and practical.

7. Avoid large tables.

8. Do not use complicated scientific terminology unless necessary.
   If you use a technical term, explain it simply.

9. Never give a definite disease diagnosis without enough information.

10. If there are several possible causes, mention the most likely causes first.

11. Give practical actions the farmer can take.

12. If pesticides, fungicides, fertilizers, or other chemicals are mentioned,
    tell the farmer to follow the product label and use appropriate protection.

13. Ask only 1 to 3 useful follow-up questions.

14. Do not repeat the farmer's question unnecessarily.

15. Do not include a long introduction.

16. Do not include a conclusion that repeats the entire answer.

17. Return ONLY the answer for the farmer.


USE THIS STRUCTURE WHEN IT FITS THE QUESTION:

🌱 What might be happening

Give a short and simple explanation.


🔎 Possible reasons

• Reason 1
• Reason 2
• Reason 3


✅ What to do now

1. Simple practical action
2. Simple practical action
3. Simple practical action


⚠️ Watch for

• Warning sign
• Warning sign


❓ Tell me this

1. Useful question
2. Useful question
3. Useful question


IMPORTANT:
Return ONLY the final farmer-friendly answer.
"""


# ============================================================
# CLEAN AI RESPONSE
# ============================================================

def clean_response(text):
    """
    Removes unwanted reasoning, thinking blocks,
    markdown artifacts and other model-generated content.
    """

    if not text:
        return "Sorry, I could not generate a response."


    # --------------------------------------------------------
    # Remove <think>...</think> blocks
    # --------------------------------------------------------

    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE
    )


    # --------------------------------------------------------
    # Remove unclosed <think> blocks
    # --------------------------------------------------------

    text = re.sub(
        r"<think>.*$",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE
    )


    # --------------------------------------------------------
    # Remove common reasoning sections
    # --------------------------------------------------------

    reasoning_patterns = [

        r"Here's a thinking process:.*?(?=🌱 What might be happening)",
        r"Here is a thinking process:.*?(?=🌱 What might be happening)",

        r"Here's my thinking:.*?(?=🌱 What might be happening)",
        r"Here is my thinking:.*?(?=🌱 What might be happening)",

        r"Let's think.*?(?=🌱 What might be happening)",

        r"Analysis:.*?(?=🌱 What might be happening)",

        r"Reasoning:.*?(?=🌱 What might be happening)",

        r"Self-Correction.*?(?=🌱 What might be happening)",

        r"Self-Correction/Refinement.*?(?=🌱 What might be happening)",

        r"Check Against Constraints:.*?(?=🌱 What might be happening)",

        r"Determine Content.*?(?=🌱 What might be happening)",

        r"Draft.*?(?=🌱 What might be happening)",

        r"Output Generation.*?(?=🌱 What might be happening)",
    ]


    for pattern in reasoning_patterns:

        text = re.sub(
            pattern,
            "",
            text,
            flags=re.DOTALL | re.IGNORECASE
        )


    # --------------------------------------------------------
    # If a proper FarmAssist section exists,
    # remove everything before it.
    # --------------------------------------------------------

    markers = [
        "🌱 What might be happening",
        "🔎 Possible reasons",
        "✅ What to do now",
        "⚠️ Watch for",
        "❓ Tell me this"
    ]

    positions = []

    for marker in markers:

        position = text.find(marker)

        if position != -1:
            positions.append(position)


    if positions:

        first_position = min(positions)

        text = text[first_position:]


    # --------------------------------------------------------
    # Remove obvious internal-thinking lines
    # --------------------------------------------------------

    unwanted_lines = [
        "Proceed.",
        "Proceed",
        "All constraints met.",
        "Ready.",
        "Output matches response.",
        "Output matches the draft.",
        "[Output Generation]",
        "[Output generation]",
        "[Self-Correction/Refinement during drafting]",
        "[Self-Correction/Verification during drafting]"
    ]

    for line in unwanted_lines:

        text = text.replace(line, "")


    # --------------------------------------------------------
    # Remove markdown bold
    # --------------------------------------------------------

    text = text.replace("**", "")
    text = text.replace("__", "")


    # --------------------------------------------------------
    # Remove horizontal markdown separators
    # --------------------------------------------------------

    text = re.sub(
        r"^\s*---+\s*$",
        "",
        text,
        flags=re.MULTILINE
    )


    # --------------------------------------------------------
    # Convert markdown bullets to simple bullets
    # --------------------------------------------------------

    text = re.sub(
        r"^\s*[-*]\s+",
        "• ",
        text,
        flags=re.MULTILINE
    )


    # --------------------------------------------------------
    # Remove excessive blank lines
    # --------------------------------------------------------

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )


    # --------------------------------------------------------
    # Remove spaces at beginning/end
    # --------------------------------------------------------

    text = text.strip()


    # --------------------------------------------------------
    # Safety fallback
    # --------------------------------------------------------

    if not text:

        return (
            "I couldn't generate a useful answer right now. "
            "Please try your farming question again."
        )


    return text


# ============================================================
# ASK FARMASSIST AI
# ============================================================

def ask_ai(question):

    if not question or not question.strip():

        return "Please enter a farming question."


    try:

        response = client.chat.completions.create(

            model=MODEL,

            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": question.strip()
                }
            ],

            temperature=0.2,

            max_tokens=600
        )


        # ----------------------------------------------------
        # Get model response
        # ----------------------------------------------------

        answer = response.choices[0].message.content


        # ----------------------------------------------------
        # Clean response
        # ----------------------------------------------------

        answer = clean_response(answer)


        return answer


    except Exception as e:

        print("\nAI Error:", e)

        return (
            "Sorry, I couldn't process your farming question "
            "right now. Please try again."
        )


# ============================================================
# TERMINAL TEST MODE
# ============================================================

if __name__ == "__main__":

    print()
    print("🌾 FarmAssist AI is running!")
    print("Type your farming question.")
    print("Type 'exit' to stop.")
    print()


    while True:

        try:

            question = input("🌾 You: ").strip()


            # ------------------------------------------------
            # Exit
            # ------------------------------------------------

            if question.lower() == "exit":

                print()
                print("🌱 FarmAssist AI: Happy farming! 🌾")
                break


            # ------------------------------------------------
            # Empty input
            # ------------------------------------------------

            if not question:

                print("Please enter a farming question.")
                print()
                continue


            # ------------------------------------------------
            # Ask AI
            # ------------------------------------------------

            print()
            print("🌱 FarmAssist AI:")
            print()


            answer = ask_ai(question)

            print(answer)

            print()


        except KeyboardInterrupt:

            print()
            print()
            print("🌱 FarmAssist AI: Happy farming! 🌾")
            break


        except Exception as e:

            print()
            print("Error:", e)
            print()