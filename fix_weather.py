import re

with open("backend/routers/diagnose.py", "r") as f:
    c = f.read()

old_weather_call = """    weather = await weather_service.get_current_weather(latitude, longitude)
    context = {
        "location": {"lat": latitude, "lng": longitude},
        "weather": weather
    }"""

new_weather_call = """    try:
        weather = await weather_service.get_current_weather(latitude, longitude)
        weather["weather_available"] = True
    except ServiceUnavailableException:
        weather = {"weather_available": False}

    context = {
        "location": {"lat": latitude, "lng": longitude},
        "weather": weather
    }"""

c = c.replace(old_weather_call, new_weather_call)

with open("backend/routers/diagnose.py", "w") as f:
    f.write(c)

with open("backend/services/gemini_service.py", "r") as f:
    gc = f.read()

old_prompt_weather = "ENVIRONMENTAL CONTEXT:"
new_prompt_weather = "ENVIRONMENTAL CONTEXT:\n(If weather_available is false, do not invent weather. State that environmental data is unavailable.)"

gc = gc.replace(old_prompt_weather, new_prompt_weather)

with open("backend/services/gemini_service.py", "w") as f:
    f.write(gc)
