from ..tools import update_calendar_event
from ..llm import get_llm
import json
from datetime import datetime, timedelta

def get_date_from_user_term(term: str, reference_date: datetime = None) -> str:
    """Calculate actual date from user's relative term like 'tomorrow', 'next monday', etc."""
    if reference_date is None:
        reference_date = datetime.now()
    
    term_lower = term.lower().strip()
    
    # Today
    if term_lower == "today":
        return reference_date.strftime('%d-%m-%Y')
    
    # Tomorrow
    if term_lower == "tomorrow":
        return (reference_date + timedelta(days=1)).strftime('%d-%m-%Y')
    
    # Day after tomorrow
    if term_lower in ["day after tomorrow", "day after tommorrow"]:
        return (reference_date + timedelta(days=2)).strftime('%d-%m-%Y')
    
    # Next [day of week]
    days_map = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6
    }
    
    if "next " in term_lower:
        day_name = term_lower.replace("next ", "").strip()
        if day_name in days_map:
            target_day = days_map[day_name]
            current_day = reference_date.weekday()
            
            # Calculate days until target day
            days_ahead = target_day - current_day
            
            # If day is today or in the past this week, go to next week
            if days_ahead <= 0:
                days_ahead += 7
            
            result_date = reference_date + timedelta(days=days_ahead)
            return result_date.strftime('%d-%m-%Y')
    
    # If can't parse, return today's date
    return reference_date.strftime('%d-%m-%Y')


def update_calendar_node(state):
    user_msg = state.messages[-1]["content"]

    today = datetime.now()
    today_date_str = today.strftime('%d-%m-%Y')
    today_weekday = today.strftime('%A')

    prompt = f"""Extract event reschedule details from this message:

User message: "{user_msg}"

CURRENT DATE AND TIME INFO:
- Today's date: {today_date_str}
- Today is: {today_weekday}

You MUST return ONLY a JSON object:
{{"title": "event title", "new_date_term": "date term", "new_time": "HH:MM"}}

IMPORTANT:
- title: Extract as "Meeting with [Contact Name]" format
- new_date_term: Return EXACTLY what user said (e.g., "next monday", "tomorrow", "next friday")
  DO NOT calculate the actual date, just extract the term
- new_time: Convert to HH:MM 24-hour format
- Return ONLY ONE event
- Return ONLY the JSON object, nothing else

Example outputs:
{{"title": "Meeting with Arvi", "new_date_term": "next monday", "new_time": "10:00"}}
{{"title": "Meeting with Swetha", "new_date_term": "tomorrow", "new_time": "17:00"}}
{{"title": "Meeting with Brother", "new_date_term": "next friday", "new_time": "10:00"}}

Return ONLY JSON:"""

    response = get_llm().invoke(prompt)
    data = response.content.strip()

    try:
        start_idx = data.find('{')
        end_idx = data.rfind('}') + 1
        json_str = data[start_idx:end_idx]
        
        details = json.loads(json_str)
        
        if "title" not in details or "new_date_term" not in details or "new_time" not in details:
            state.messages.append({
                "role": "assistant",
                "content": "I couldn't extract all reschedule details. Please provide event name, new date, and new time."
            })
            return state
        
        # Normalize title to "Meeting with [Name]" format
        title = details["title"].strip()
        for prefix in ["meeting with ", "appointment with ", "event with ", "call with ", "reschedule ", "move "]:
            if title.lower().startswith(prefix):
                title = title[len(prefix):]
                break
        
        if not title.lower().startswith("meeting with "):
            title = f"Meeting with {title}"
        
        # Calculate actual date using Python, not LLM
        actual_date = get_date_from_user_term(details["new_date_term"])
        
        result = update_calendar_event(
            title,
            actual_date,
            details["new_time"]
        )
        
        state.messages.append({
            "role": "assistant",
            "content": result
        })

    except (json.JSONDecodeError, ValueError, KeyError) as e:
        state.messages.append({
            "role": "assistant",
            "content": "I couldn't parse the reschedule details. Please try again."
        })

    return state