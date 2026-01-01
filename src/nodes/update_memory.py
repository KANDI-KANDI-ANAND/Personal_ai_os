from ..memory.vectorstore import search_memory, delete_memory_by_text, add_memory
from ..llm import get_llm

def update_memory_node(state):
    user_msg = state.messages[-1]["content"]

    """
    Example user messages:
    - "update my wake up time to 6am"
    - "change my habit to reading daily"
    """

    # Ask LLM to extract old vs new info
    prompt = f"""
You are extracting memory updates.

From the user message below, identify:
1. The OLD information (what should be replaced)
2. The NEW information (what should be saved)

User message:
"{user_msg}"

Respond in JSON ONLY:
{{
  "old": "...",
  "new": "..."
}}
"""

    response = get_llm().invoke(prompt)
    content = response.content.strip()

    try:
        import json
        data = json.loads(content)
        old_text = data.get("old", "").strip()
        new_text = data.get("new", "").strip()
    except Exception:
        state.messages.append({
            "role": "assistant",
            "content": "I couldn't clearly understand what you want to update."
        })
        return state

    if not old_text or not new_text:
        state.messages.append({
            "role": "assistant",
            "content": "Please clearly say what you want to change and the new value."
        })
        return state

    # Try deleting old memory
    deleted = delete_memory_by_text(old_text)

    # Always add new memory
    add_memory(new_text)

    # Confirmation
    confirm_prompt = f"""
Generate a short confirmation that the user's information was updated successfully.
Keep it to one sentence.
"""

    confirm = get_llm().invoke(confirm_prompt).content.strip()
    state.messages.append({"role": "assistant", "content": confirm})

    return state
