from ..tools import add_calendar_event
from ..memory.vectorstore import add_memory
from ..llm import get_llm
import json
from datetime import datetime, timedelta
import re

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


def calendar_action_node(state):
    user_msg = state.messages[-1]["content"]

    msg_for_extraction = user_msg
    for keyword in ["plan my day", "plan my", "schedule for", "organize"]:
        if keyword in msg_for_extraction.lower():
            if " and " in msg_for_extraction.lower():
                msg_for_extraction = msg_for_extraction.split(" and ", 1)[-1]

    today = datetime.now()
    today_date_str = today.strftime('%d-%m-%Y')
    today_weekday = today.strftime('%A')

    prompt = f"""
Extract only one calendar event details from this user message:

User message: "{msg_for_extraction}"

CURRENT DATE AND TIME INFO:
- Today's date: {today_date_str}
- Today is: {today_weekday}

You MUST return ONLY a JSON object with these fields:
- "title": The event name/title (string)
- "date_term": The date term from user (e.g., "tomorrow", "next monday", "today", "day after tomorrow")
- "time": The time in HH:MM 24-hour format

IMPORTANT:
- Return ONLY ONE event
- Normalize title to "Meeting with [Name]" format
- date_term: Return EXACTLY what the user said for the date (don't calculate, just extract the term)
- time: Convert to HH:MM 24-hour format
- DO NOT add any explanation, notes, or extra text
- Return ONLY the JSON object, nothing else

Example outputs:
{{"title": "Meeting with Arvi", "date_term": "tomorrow", "time": "10:00"}}
{{"title": "Meeting with Swetha", "date_term": "next monday", "time": "14:00"}}
{{"title": "Meeting with Brother", "date_term": "next friday", "time": "10:00"}}

Return ONLY JSON object:
"""

    response = get_llm().invoke(prompt)
    data = response.content.strip()

    try:
        start_idx = data.find('{')
        end_idx = data.rfind('}') + 1
        if start_idx != -1 and end_idx > start_idx:
            json_str = data[start_idx:end_idx]
        else:
            json_str = data

        details = json.loads(json_str)

        if isinstance(details, list):
            state.messages.append({
                "role": "assistant",
                "content": "I need to extract ONE event. Please be more specific."
            })
            return state

        if "title" not in details or "date_term" not in details or "time" not in details:
            state.messages.append({
                "role": "assistant",
                "content": "I couldn't extract complete event details. Please provide title, date, and time."
            })
            return state

        # Calculate actual date using Python, not LLM
        actual_date = get_date_from_user_term(details["date_term"])

        result = add_calendar_event(
            title=details["title"],
            date=actual_date,
            time=details["time"]
        )

        if not result.startswith("❌"):
            memory_text = f"I have a {details['title']} on {actual_date} at {details['time']}"
            add_memory(memory_text)

        state.messages.append({
            "role": "assistant",
            "content": result
        })

    except json.JSONDecodeError:
        state.messages.append({
            "role": "assistant",
            "content": f"I couldn't parse the event details. Please try again with a clearer request."
        })
    except ValueError as e:
        state.messages.append({
            "role": "assistant",
            "content": f"Invalid date or time format. Please use DD-MM-YYYY for date and HH:MM for time."
        })
    except KeyError as e:
        state.messages.append({
            "role": "assistant",
            "content": f"Missing event information. Please provide all details."
        })

    return state