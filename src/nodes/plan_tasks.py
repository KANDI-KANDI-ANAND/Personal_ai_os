from ..llm import get_llm

def plan_tasks_node(state):
    user_msg = state.messages[-1]["content"]

    prompt = f"""You are a helpful planning assistant. The user said: "{user_msg}"

If they're asking for a plan or schedule a day or week, create a brief, clear step-by-step plan (5-7 steps max).
If they're asking something else related to planning/scheduling, help them.
Keep response concise and practical.

User request: {user_msg}"""

    response = get_llm().invoke(prompt)
    content = response.content.strip()
    state.messages.append({"role": "assistant", "content": content})
    return state