from ..llm import get_llm

def plan_steps_node(state):
    user_msg = state.messages[-1]["content"]
    intent = state.intent  # Use intent from router

    # Map intent to its primary step
    intent_to_steps_map = {
        "calendar": ["calendar"],
        "delete_calendar": ["delete_calendar"],
        "update_calendar": ["update_calendar"],
        "set_reminder": ["set_reminder"],
        "send_message": ["send_message"],
        "send_email": ["send_email"],
        "plan_tasks": ["plan_tasks"],
        "save_memory": ["save_memory"],
        "recall_memory": ["recall_memory"],
        "update_memory": ["update_memory"],
    }
    
    # Get base step from intent
    base_steps = intent_to_steps_map.get(intent, [])
    
    if not base_steps:
        state.steps = []
        state.current_step = 0
        print(f"🧠 PLAN: []")
        return state
    
    # For single-step intents, just use base step
    if intent in ["delete_calendar", "recall_memory", "update_calendar"]:
        state.steps = base_steps
        state.current_step = 0
        print(f"🧠 PLAN: {state.steps}")
        return state
    
    # For multi-step capable intents, check if message mentions additional actions
    steps = base_steps.copy()
    user_msg_lower = user_msg.lower()
    
    # Only add extra steps if explicitly mentioned AND relevant to base intent
    if intent == "calendar":
        # Calendar can have additional steps
        if "remind" in user_msg_lower:
            steps.append("set_reminder")
        if "notify" in user_msg_lower or "message" in user_msg_lower or "telegram" in user_msg_lower:
            steps.append("send_message")
        if "email" in user_msg_lower or "send email" in user_msg_lower:
            steps.append("send_email")
    
    elif intent == "send_message":
        if "when" in user_msg_lower or "tell me" in user_msg_lower or "remind me" in user_msg_lower:
            steps.append("recall_memory")
    
    elif intent == "send_email":
        if "remember" in user_msg_lower or "save" in user_msg_lower:
            steps.append("save_memory")

    elif intent == "plan_tasks":
        if "email" in user_msg_lower or "send" in user_msg_lower:
            steps.append("send_email")
        if "meeting" in user_msg_lower or "add meeting" in user_msg_lower or "meeting with" in user_msg_lower:
            steps.append("calendar")

    # ONLY add plan_tasks if user EXPLICITLY says "plan my day/week" AND "calendar" intent
    # Do NOT add it just because "schedule" appears in the message
    if intent == "calendar" and ("plan my day" in user_msg_lower or "plan my week" in user_msg_lower or "plan my" in user_msg_lower) and "plan_tasks" not in steps:
        # Add plan_tasks at the beginning
        steps.insert(0, "plan_tasks")

    
    state.steps = steps
    state.current_step = 0

    print(f"🧠 PLAN: {state.steps}")
    return state