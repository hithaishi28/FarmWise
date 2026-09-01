from .chatbot import ask_ai


def recommend_crops(
    soil_type,
    temperature,
    rainfall,
    season,
    water_availability
):
    prompt = f"""
I need crop recommendations for a farmer.

Farm conditions:

Soil type: {soil_type}
Average temperature: {temperature} °C
Rainfall: {rainfall}
Season: {season}
Water availability: {water_availability}

Recommend 3 suitable crops.

For each crop, explain:
1. Why it is suitable
2. Basic growing requirements
3. One important precaution

Keep the answer simple and practical for a farmer.

Do not assume information that was not provided.
"""

    return ask_ai(prompt)