from .chatbot import ask_ai


def analyze_crop_issue(crop, symptoms):
    prompt = f"""
A farmer needs help identifying a possible problem with their crop.

Crop: {crop}

Observed symptoms:
{symptoms}

Analyze this carefully.

Provide:

1. Possible causes or diseases
2. Why each possibility may match the symptoms
3. What the farmer should check next
4. Practical steps the farmer can take
5. What the farmer should avoid doing

Important:
- Do not claim that a disease is definitely present.
- Clearly say that this is a possible diagnosis.
- Ask for additional information if the symptoms are not enough.
- Give simple, practical advice suitable for a farmer.
"""

    return ask_ai(prompt)