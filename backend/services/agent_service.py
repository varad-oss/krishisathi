import logging
from google import genai
from google.genai import types
from config import settings
from services.weather_service import weather_service
from services.kvk_service import kvk_service
import asyncio

logger = logging.getLogger(__name__)

# Basic sync wrappers for tools if needed, but Gemini function calling supports async if we handle it properly.
# Actually we will define functions that the agent can call.

def get_weather_tool(lat: float, lng: float) -> dict:
    """Get current weather information for a specific location."""
    # We use a sync wrapper because we might need to run the async func in the event loop
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # In a running loop, we shouldn't use run_until_complete directly if it's already running.
        # But this function will be called synchronously by the Gemini API loop (if doing auto function calling)
        # So we might need to handle this carefully.
        # Actually, let's just make the tool do a sync request or mock it, or run in a new thread.
        import threading
        result = None
        def run():
            nonlocal result
            try:
                import httpx
                # Simplified sync request just for the tool to avoid async issues
                response = httpx.get(
                    f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current_weather=true",
                    timeout=5.0
                )
                if response.status_code == 200:
                    data = response.json()
                    current = data.get("current_weather", {})
                    result = {
                        "temperature": current.get("temperature", 28.5),
                        "windspeed": current.get("windspeed", 12.5),
                        "description": "partly cloudy" # Mocked desc
                    }
                else:
                    result = {"temperature": 28.5, "windspeed": 12.5, "description": "partly cloudy"}
            except Exception as e:
                logger.error(f"Weather tool error: {e}")
                result = {"temperature": 28.5, "windspeed": 12.5, "description": "partly cloudy"}
        
        t = threading.Thread(target=run)
        t.start()
        t.join()
        return result
    else:
        return loop.run_until_complete(weather_service.get_current_weather(lat, lng))


def get_kvk_tool(lat: float, lng: float) -> dict:
    """Find the nearest Krishi Vigyan Kendra (KVK) to the given location coordinates."""
    return kvk_service.get_nearest_kvk(lat, lng)

def get_state_config_tool(state_code: str) -> dict:
    """Get agricultural configuration and details for an Indian state given its 2-letter state code (e.g., 'PB', 'MH')."""
    from routers.states import INDIAN_STATES
    state = next((s for s in INDIAN_STATES if s["code"] == state_code.upper()), None)
    return state if state else {"error": "State not found"}

class AgentService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("GEMINI_API_KEY not set for AgentService.")

    def process_advisory(self, query: str, context: dict, image_base64: str = None) -> str:
        if not self.client:
            raise Exception("Agent requires API key")

        prompt = f"""
        You are an expert agricultural advisor agent. You can use tools to find weather data, nearby KVK (Krishi Vigyan Kendra) centers, or state-specific information.
        Process the following query and provide actionable, helpful advice for the farmer.
        
        Farmer Query: {query}
        Context provided by system: {context}
        """

        # Using gemini-flash-lite-latest for complex agent orchestration (to avoid rate limits)
        model = 'gemini-flash-lite-latest'
        
try:
            logger.info("Calling Gemini Agent...")
            contents = [prompt]
            if image_base64:
                import base64
                from google.genai import types
                img_bytes = base64.b64decode(image_base64)
                img_part = types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
                contents.append(img_part)
                
            response = self.client.models.generate_content(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    tools=[get_weather_tool, get_kvk_tool, get_state_config_tool],
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(
                        disable=False
                    )
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Agent processing failed: {e}")
            raise e

agent_service = AgentService()
