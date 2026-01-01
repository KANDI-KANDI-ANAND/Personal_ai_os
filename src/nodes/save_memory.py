from ..memory.vectorstore import add_memory
from ..llm import get_llm

def save_memory_node(state):
    user_msg = state.messages[-1]["content"]
    
    # Extract the memory content from user message
    # Remove common prefixes
    memory_text = user_msg
    for prefix in ["remember that ", "save ", "note that ", "my ", "i "]:
        if memory_text.lower().startswith(prefix):
            memory_text = memory_text[len(prefix):].strip()
            break
    
    # If the message is about remembering something specific, extract it
    if "remember" in user_msg.lower() or "password" in user_msg.lower():
        # Look for patterns like "remember my X is Y" or "X is Y"
        if " is " in user_msg:
            memory_text = user_msg.split("remember ", 1)[-1] if "remember" in user_msg else user_msg
            memory_text = memory_text.split("and ", 1)[0].strip()  # Get only the memory part, not other actions
    
    memory_text = memory_text.strip()
    
    print(f"Attempting to save: '{memory_text}'")
    add_memory(memory_text)
    
    # Use LLM to generate natural confirmation
    prompt = f"""Generate a brief, natural confirmation response to: "{user_msg}"
    
Keep it to 1 sentence. Be friendly and conversational. 
Do NOT repeat what they said. Keep it short.

Response:"""
    
    llm_response = get_llm().invoke(prompt)
    response = llm_response.content.strip()
    
    state.messages.append({"role": "assistant", "content": response})
    return state