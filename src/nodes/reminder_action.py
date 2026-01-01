from ..tools import update_calendar_reminder
from ..llm import get_llm
import json

def reminder_action_node(state):
    user_msg = state.messages[-1]["content"]
    
    prompt = f"""Extract reminder details from this message:

User message: "{user_msg}"

You MUST return ONLY a JSON object:
{{"title": "event title (include contact name if mentioned)", "reminder_minutes": number}}

IMPORTANT:
- title should match the event in calendar
- If calendar has "Meeting with Arvi", don't just say "Arvi"
- If user says "swetha meeting", try "Meeting with Swetha" or just "Swetha"
- If user says "brother", try "Meeting with Brother" or just "Brother"
- Extract what matches the calendar event

Examples:
- User says "remind me 1 hour before the swetha meeting" → Try both "Meeting with Swetha" and "Swetha"
- User says "remind me 30 minutes before my meeting with john" → {{"title": "Meeting with John", "reminder_minutes": 30}}
- User says "set 10 minute alarm for dentist" → {{"title": "dentist", "reminder_minutes": 10}}

Common reminder times:
- 5 minutes = 5
- 15 minutes = 15
- 30 minutes = 30
- 1 hour = 60
- 2 hours = 120

Return ONLY JSON:"""

    response = get_llm().invoke(prompt)
    data = response.content.strip()
    
    try:
        start_idx = data.find('{')
        end_idx = data.rfind('}') + 1
        json_str = data[start_idx:end_idx]
        
        details = json.loads(json_str)
        reminder_minutes = details.get("reminder_minutes") or 30
        title = details.get("title", "").strip()
        
        if not title:
            state.messages.append({
                "role": "assistant",
                "content": "I need a clearer event title to set a reminder."
            })
            return state
                
        result = update_calendar_reminder(
            title,
            int(reminder_minutes)
        )
        
        
        state.messages.append({
            "role": "assistant",
            "content": result
        })

    except (json.JSONDecodeError, ValueError, KeyError) as e:
        state.messages.append({
            "role": "assistant",
            "content": "I couldn't parse the reminder details. Please try again."
        })

    return state