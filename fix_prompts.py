with open("backend/services/gemini_service.py", "r") as f:
    content = f.read()

# Fix diagnose
old_diagnose_prompt = """            prompt = f\"\"\"
You are an expert agricultural plant pathologist. Analyze the provided image of a crop.

[OBSERVED FROM IMAGE]
Analyze the visual symptoms carefully.
Crop Type (if provided): {crop_type or 'Unknown'}

[REFERENCE KNOWLEDGE]
{grounding_context}

[ENVIRONMENTAL CONTEXT]
Location: Lat {location_context.get('lat')}, Lng {location_context.get('lng')}
State: {location_context.get('state')}
\"\"\""""

new_diagnose_prompt = """            system_instruction = "You are an expert agricultural plant pathologist. Analyze the provided image of a crop."
            prompt = f\"\"\"
[OBSERVED FROM IMAGE]
Analyze the visual symptoms carefully.
Crop Type (if provided): {crop_type or 'Unknown'}

[REFERENCE KNOWLEDGE]
{grounding_context}

[ENVIRONMENTAL CONTEXT]
Location: Lat {location_context.get('lat')}, Lng {location_context.get('lng')}
State: {location_context.get('state')}
\"\"\""""

content = content.replace(old_diagnose_prompt, new_diagnose_prompt)
content = content.replace(
    "response_mime_type=\"application/json\",\n                error_message",
    "response_mime_type=\"application/json\",\n                system_instruction=system_instruction,\n                error_message"
)

# Fix advisory
old_advisory_prompt = """            prompt = f\"\"\"
            You are an expert agricultural advisor. Provide detailed, actionable advice for the following query.
            Query: {query}
            Context (Weather, soil, etc.): {context}
            
            Provide the advisory clearly and concisely.
            \"\"\""""

new_advisory_prompt = """            system_instruction = "You are an expert agricultural advisor. Provide detailed, actionable advice. Provide the advisory clearly and concisely."
            prompt = f\"\"\"
            Query: {query}
            Context (Weather, soil, etc.): {context}
            \"\"\""""

content = content.replace(old_advisory_prompt, new_advisory_prompt)
content = content.replace(
    "model=settings.GEMINI_ADVISORY_MODEL,\n                error_message",
    "model=settings.GEMINI_ADVISORY_MODEL,\n                system_instruction=system_instruction,\n                error_message"
)

with open("backend/services/gemini_service.py", "w") as f:
    f.write(content)
