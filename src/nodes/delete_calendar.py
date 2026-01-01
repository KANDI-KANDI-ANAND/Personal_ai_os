from ..tools import delete_calendar_event
from ..llm import get_llm
import json

def delete_calendar_node(state):
    user_msg = state.messages[-1]["content"]

    prompt = f"""Extract the event details to delete from this message:

User message: "{user_msg}"

You MUST return ONLY a JSON object:
{{"title": "event title to delete"}}

Examples:
- User says "delete my meeting with john" → {{"title": "meeting with john"}}
- User says "cancel the dentist appointment" → {{"title": "dentist appointment"}}
- User says "remove the standup" → {{"title": "standup"}}

Return ONLY JSON:"""

    response = get_llm().invoke(prompt)
    data = response.content.strip()

    try:
        start_idx = data.find('{')
        end_idx = data.rfind('}') + 1
        json_str = data[start_idx:end_idx]
        
        details = json.loads(json_str)
        result = delete_calendar_event(details["title"])
        
        state.messages.append({
            "role": "assistant",
            "content": result
        })

    except (json.JSONDecodeError, ValueError, KeyError):
        state.messages.append({
            "role": "assistant",
            "content": "I couldn't parse the event to delete. Please try again with a clearer request."
        })

    return state