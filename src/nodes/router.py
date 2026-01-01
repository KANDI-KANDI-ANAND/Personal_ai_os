from ..llm import get_llm

def router_node(state):
    user_msg = state.messages[-1]["content"]
    
    # Quick check for scheduling/planning vs specific calendar event
    user_msg_lower = user_msg.lower()
    
    # Check for reschedule/update keywords FIRST
    reschedule_keywords = ["reschedule", "move", "postpone", "shift to", "change the time", "update the time"]
    if any(keyword in user_msg_lower for keyword in reschedule_keywords):
        state.intent = "update_calendar"
        print(f"🎯 Detected Intent: update_calendar")
        return state
    
    # Check for delete/cancel keywords
    delete_keywords = ["delete", "cancel", "remove event", "remove the event", "remove meeting"]
    if any(keyword in user_msg_lower for keyword in delete_keywords):
        state.intent = "delete_calendar"
        print(f"🎯 Detected Intent: delete_calendar")
        return state
    
    # If user asks to plan/schedule without mentioning specific person/time, it's plan_tasks
    planning_keywords = ["plan my", "schedule for", "create a schedule", "organize my", "routine"]
    calendar_keywords = ["meeting with", "appointment with", "event with", "at ", "am", "pm"]
    
    has_planning = any(keyword in user_msg_lower for keyword in planning_keywords)
    has_calendar = any(keyword in user_msg_lower for keyword in calendar_keywords)
    
    # If user says BOTH "plan" AND "add meeting", detect as calendar (plan_steps will add plan_tasks)
    if has_planning and has_calendar:
        state.intent = "calendar"
        print(f"🎯 Detected Intent: calendar")
        return state
    
    # If has planning keywords but NO specific person/time, it's planning not calendar
    if has_planning and not has_calendar:
        state.intent = "plan_tasks"
        print(f"🎯 Detected Intent: plan_tasks")
        return state

    prompt = f"""You are an intelligent intent classifier. Analyze what the user wants and respond with ONLY the intent category.

USER MESSAGE: "{user_msg}"

INTENT CATEGORIES:

1. save_memory: User is SHARING/SAVING information about themselves
   - Examples: "my name is anand", "i sleep at 9pm", "note that i wake up at 5am"

2. recall_memory: User is ASKING about information they previously shared
   - Examples: "what is my name?", "when do i sleep?", "what time do i wake up?"

3. update_memory: User is UPDATING previously shared information
   - Examples: "my name is not anand, it's K.Anand", "i sleep at 9pm not 10pm"

4. conversation: User wants CASUAL CHAT or general conversation
   - Examples: "hello", "how are you?", "tell me a joke", "what's your opinion?"

5. calendar: User wants to ADD/CREATE a calendar event (with specific person/time)
   - Key phrases: "add meeting", "schedule", "create event", "book", "appointment"
   - Examples: "add meeting with arvi tomorrow at 10am", "schedule a call with john"
   - MUST have: specific person AND specific time

6. delete_calendar: User wants to DELETE a calendar event
   - Key phrases: "delete", "cancel", "remove event"
   - Examples: "delete my meeting", "cancel the appointment"

7. update_calendar: User wants to RESCHEDULE/CHANGE event time
   - Key phrases: "reschedule", "change time", "move to", "postpone"
   - Examples: "reschedule meeting to 5pm", "move appointment to next week"

8. set_reminder: User wants to SET/CHANGE event reminder
   - Key phrases: "remind me", "set reminder", "give warning"
   - Examples: "remind me 30 minutes before", "set 15 minute alarm"

9. send_message: User wants to SEND a message via Telegram
   - Key phrases: "send message", "notify", "tell", "message to", "telegram"
   - Examples: "send message to arvi saying hello", "notify brother about meeting"

10. send_email: User wants to SEND an email
    - Key phrases: "send email", "send mail to"
    - Examples: "send email to john", "send email to dad@gmail.com"

11. plan_tasks: User wants to PLAN/ORGANIZE day/week/schedule
    - Key phrases: "plan my", "schedule for", "create a schedule", "organize"
    - Examples: "plan my day for tomorrow", "create a routine", "schedule my week"
    - NOTE: This is for GENERAL planning, NOT adding specific calendar events

12. exit: User wants to END conversation
    - Examples: "bye", "quit", "goodbye", "exit"

IMPORTANT:
- Focus on INTENT, not exact keywords
- CALENDAR vs PLAN_TASKS: If user specifies WHO and WHEN → CALENDAR. If user asks for general planning → PLAN_TASKS
- If unsure, think about what action the user is requesting
- Return ONLY the intent word (lowercase): save_memory, recall_memory, update_memory, conversation, calendar, delete_calendar, update_calendar, set_reminder, send_message, send_email, plan_tasks, or exit

Response (ONLY the intent):"""

    response = get_llm().invoke(prompt)
    intent = response.content.strip().lower()
    
    valid_intents = [
        "save_memory", "recall_memory", "update_memory", 
        "conversation", "calendar", "delete_calendar", "update_calendar", 
        "set_reminder", "send_message", "send_email", "plan_tasks", "exit"
    ]
    
    # If invalid intent, default to conversation
    if intent not in valid_intents:
        intent = "conversation"
    
    state.intent = intent
    print(f"🎯 Detected Intent: {intent}")
    return state