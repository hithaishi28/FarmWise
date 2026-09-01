
import pandas as pd
import streamlit as st


# ============================================================
# AI INTEGRATION
# ============================================================

try:
    from ai.chatbot import ask_ai as _ai_response
except ImportError:
    _ai_response = None


try:
    from ai.recommendations import get_crop_recommendation as _crop_recommendation
except ImportError:
    _crop_recommendation = None


# ============================================================
# WEATHER INTEGRATION
# Person 3's actual weather backend
# ============================================================

try:
    from weather.weather_api import get_weather_data as _fetch_weather_data
except ImportError:
    _fetch_weather_data = None


# ============================================================
# MARKET INTEGRATION
# ============================================================

try:
    from data.market import fetch_market_prices as _fetch_market_prices
except ImportError:
    _fetch_market_prices = None


# ============================================================
# DATABASE INTEGRATION
# ============================================================

try:
    from database.db import add_product as _db_add_product
    from database.db import create_order as _db_create_order
    from database.db import get_products as _db_get_products
    from database.db import get_user as _db_get_user
except ImportError:
    _db_add_product = None
    _db_create_order = None
    _db_get_products = None
    _db_get_user = None


# ============================================================
# INTEGRATION STATUS
# ============================================================

def integration_status() -> dict[str, bool]:
    """Return which teammate integrations are available."""

    return {
        "AI Engine": _ai_response is not None and _crop_recommendation is not None,
        "Weather API": _fetch_weather_data is not None,
        "Market API": _fetch_market_prices is not None,
        "Database": _db_get_products is not None and _db_add_product is not None,
        "Orders": _db_create_order is not None,
        "User DB": _db_get_user is not None,
    }


def render_integration_badges() -> None:
    """Show compact integration status badges for development."""

    with st.sidebar.expander("Developer Integrations", expanded=False):

        for service, connected in integration_status().items():

            if connected:
                st.success(f"{service}: Connected")
            else:
                st.warning(f"{service}: Mock")


# ============================================================
# AI CHATBOT
# ============================================================

def get_ai_response(prompt: str) -> str:
    """Route chat prompts to Person 2's AI module."""

    if _ai_response is not None:

        try:
            response = _ai_response(prompt)

            if isinstance(response, dict):
                return str(
                    response.get("answer")
                    or response.get("response")
                    or response
                )

            return str(response)

        except Exception as error:
            st.warning(
                f"AI Engine failed, using mock response: {error}"
            )

    return (
        "Mock AI: Check soil moisture, inspect leaves for pests, "
        "and align irrigation with the latest weather forecast "
        "before taking action."
    )


# ============================================================
# CROP RECOMMENDATION
# ============================================================

def get_crop_recommendation(inputs: dict[str, float]) -> dict[str, str]:
    """Route soil/weather inputs to Person 2's recommendation module."""

    if _crop_recommendation is not None:

        try:

            result = _crop_recommendation(
                nitrogen=inputs["nitrogen"],
                phosphorus=inputs["phosphorus"],
                potassium=inputs["potassium"],
                rainfall=inputs["rainfall"],
                temperature=inputs["temperature"],
                ph=inputs["ph"],
            )

        except TypeError:

            try:
                result = _crop_recommendation(inputs)

            except Exception as error:

                st.warning(
                    f"Crop model failed, using mock result: {error}"
                )

                result = None

        except Exception as error:

            st.warning(
                f"Crop model failed, using mock result: {error}"
            )

            result = None

        if isinstance(result, dict):

            return {
                "crop": str(
                    result.get("crop")
                    or result.get("recommended_crop")
                    or "Unknown"
                ),

                "confidence": str(
                    result.get("confidence")
                    or result.get("score")
                    or "Model"
                ),

                "reason": str(
                    result.get("reason")
                    or result.get("explanation")
                    or "Generated by AI model."
                ),

                "next_step": str(
                    result.get("next_step")
                    or "Validate with local field conditions."
                ),
            }

        if result:

            return {
                "crop": str(result),
                "confidence": "Model",
                "reason": (
                    "Generated by Person 2's recommendation module."
                ),
                "next_step": (
                    "Validate with local field conditions."
                ),
            }

    return {
        "crop": "Rice" if inputs["rainfall"] >= 650 else "Millet",
        "confidence": "Mock",
        "reason": (
            "Mock rule: higher rainfall favors rice, "
            "lower rainfall favors millet."
        ),
        "next_step": (
            "Replace this fallback with Person 2's trained model."
        ),
    }


# ============================================================
# WEATHER API
# ============================================================

def fetch_weather_data(location: str) -> dict:
    """
    Get real weather data from Person 3's weather API
    and convert it into the format expected by the UI.
    """

    if _fetch_weather_data is not None:

        try:

            # Call Person 3's function:
            # weather.weather_api.get_weather_data()
            api_data = _fetch_weather_data(location)

            # Check for API error
            if not api_data or "error" in api_data:

                error_message = (
                    api_data.get("error", "Unknown weather API error")
                    if api_data
                    else "No weather data received"
                )

                st.error(f"Weather API error: {error_message}")

                return {}

            # ------------------------------------------------
            # CURRENT WEATHER
            # ------------------------------------------------

            current = api_data["current"]

            current_weather = {
                "location": current["city"],

                "condition": current["description"].title(),

                "temperature_c": current["temperature"],

                "feels_like_c": current["feels_like"],

                "humidity": f"{current['humidity']}%",

                "wind": f"{current['wind_speed']} m/s",

                # OpenWeather current-weather endpoint
                # does not provide rain probability.
                "rain_chance": "N/A",

                "farm_note_key": "farm_note",
            }

            # ------------------------------------------------
            # FORECAST
            # ------------------------------------------------

            forecast = []

            for item in api_data["forecast"][:5]:

                forecast.append(
                    {
                        "day": item["datetime"],

                        "condition": item["description"].title(),

                        "high_c": item["temperature"],

                        "low_c": item["temperature"],

                        "rain_chance": (
                            f"{item['rain_probability']:.0f}%"
                        ),
                    }
                )

            # ------------------------------------------------
            # CHART DATA
            # ------------------------------------------------

            chart_data = pd.DataFrame(
                {
                    "Temperature (C)": [
                        item["temperature"]
                        for item in api_data["forecast"][:8]
                    ],

                    "Rain Chance (%)": [
                        item["rain_probability"]
                        for item in api_data["forecast"][:8]
                    ],
                }
            )

            # ------------------------------------------------
            # RETURN DATA IN UI FORMAT
            # ------------------------------------------------

            return {
                "current": current_weather,
                "forecast": forecast,
                "hourly": chart_data,
            }

        except Exception as error:

            st.error(
                f"Weather API failed: {error}"
            )

            return {}

    # --------------------------------------------------------
    # Backend not connected
    # --------------------------------------------------------

    st.warning(
        "Weather API is not connected."
    )

    return {}


# ============================================================
# MARKET API
# ============================================================

def fetch_market_prices(
    location: str
) -> dict[str, pd.DataFrame | list[str]]:

    """Route market requests to Person 3's market API module."""

    if _fetch_market_prices is not None:

        try:
            return _fetch_market_prices(location)

        except Exception as error:

            st.warning(
                f"Market API failed, using mock data: {error}"
            )

    prices = pd.DataFrame(
        [
            {
                "Commodity": "Tomato",
                "Category": "Vegetables",
                "Market": f"{location} Mandi",
                "Min Price": 2100,
                "Max Price": 2700,
                "Modal Price": 2450,
                "Trend": "Up",
            },

            {
                "Commodity": "Onion",
                "Category": "Vegetables",
                "Market": "Nashik Mandi",
                "Min Price": 1600,
                "Max Price": 2200,
                "Modal Price": 1900,
                "Trend": "Stable",
            },

            {
                "Commodity": "Wheat",
                "Category": "Grains",
                "Market": "Indore Mandi",
                "Min Price": 2350,
                "Max Price": 2580,
                "Modal Price": 2460,
                "Trend": "Up",
            },

            {
                "Commodity": "Soybean",
                "Category": "Pulses",
                "Market": "Ujjain Mandi",
                "Min Price": 4100,
                "Max Price": 4620,
                "Modal Price": 4380,
                "Trend": "Down",
            },
        ]
    )

    trends = pd.DataFrame(
        {
            "Date": pd.date_range(
                "2025-09-01",
                periods=366,
                freq="D"
            ),

            "Tomato": [
                1800 + (day * 5) + ((day % 14) * 18)
                for day in range(366)
            ],

            "Onion": [
                1700 + (day % 45) * 7 + ((day % 9) * 12)
                for day in range(366)
            ],

            "Wheat": [
                2250 + (day * 2) + ((day % 21) * 5)
                for day in range(366)
            ],

            "Soybean": [
                4700 - (day * 1.2) + ((day % 18) * 14)
                for day in range(366)
            ],
        }
    ).set_index("Date")

    return {
        "categories": [
            "All",
            "Vegetables",
            "Fruits",
            "Grains",
            "Pulses",
        ],
        "prices": prices,
        "trends": trends,
    }


# ============================================================
# DATABASE / MARKETPLACE
# ============================================================

def _session_products() -> list[dict]:

    if "mock_products" not in st.session_state:
        st.session_state.mock_products = []

    return st.session_state.mock_products


def get_products() -> list[dict]:
    """Read products from Person 4's database module."""

    if _db_get_products is not None:

        try:

            products = _db_get_products()

            return list(products or [])

        except Exception as error:

            st.warning(
                f"Database product read failed, using mock data: {error}"
            )

    return _session_products()


def add_product(product: dict) -> bool:
    """Write products through Person 4's database module."""

    if _db_add_product is not None:

        try:

            _db_add_product(product)

            return True

        except TypeError:

            try:

                _db_add_product(**product)

                return True

            except Exception as error:

                st.error(
                    f"Database product save failed: {error}"
                )

        except Exception as error:

            st.error(
                f"Database product save failed: {error}"
            )

    _session_products().append(product)

    return False


def create_order(items: list[dict]) -> bool:
    """Create an order through Person 4's database module."""

    if _db_create_order is not None:

        try:

            _db_create_order(items)

            return True

        except Exception as error:

            st.error(
                f"Database order create failed: {error}"
            )

    if "mock_orders" not in st.session_state:
        st.session_state.mock_orders = []

    st.session_state.mock_orders.append(
        {
            "items": items
        }
    )

    return False


def get_user() -> dict[str, str]:
    """Read active user from Person 4's database module."""

    if _db_get_user is not None:

        try:

            user = _db_get_user()

            if isinstance(user, dict):
                return user

        except Exception as error:

            st.warning(
                f"User DB failed, using mock user: {error}"
            )

    return {
        "name": "Person 1",
        "role": "UI / Lead Developer",
    }

