from ..llm import get_llm

def conversation_node(state):
    user_msg = state.messages[-1]["content"]

    prompt = f"""You are a friendly, helpful personal assistant. Have a natural conversation.
    Keep responses concise (2-3 sentences max) unless asked for more detail.

    User: {user_msg}
    """

    response = get_llm().invoke(prompt)
    content = response.content.strip()
    state.messages.append({"role": "assistant", "content": content})
    return state