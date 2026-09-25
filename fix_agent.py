with open("backend/services/agent_service.py", "r") as f:
    content = f.read()

old_agent_prompt = """        prompt = f\"\"\"
        You are an expert agricultural advisor agent. You can use tools to find weather data, nearby KVK (Krishi Vigyan Kendra) centers, or state-specific information.
        
        Answer the farmer's query clearly and concisely.
        
        Query: {query}
        Context (Location, Crop, etc.): {context}
        \"\"\""""

new_agent_prompt = """        system_instruction = "You are an expert agricultural advisor agent. You can use tools to find weather data, nearby KVK (Krishi Vigyan Kendra) centers, or state-specific information. Answer the farmer's query clearly and concisely."
        prompt = f\"\"\"
        Query: {query}
        Context (Location, Crop, etc.): {context}
        \"\"\""""

content = content.replace(old_agent_prompt, new_agent_prompt)
content = content.replace(
    "config = types.GenerateContentConfig(",
    "config = types.GenerateContentConfig(\n            system_instruction=system_instruction,"
)

with open("backend/services/agent_service.py", "w") as f:
    f.write(content)
