from ..memory.vectorstore import search_memory
from ..llm import get_llm

def recall_memory_node(state):
    user_query = state.messages[-1]["content"]
    print(f"\n=== Recall Memory ===")
    
    
    results = search_memory(user_query)
    
    if not results["documents"] or not results["documents"][0] or len(results["documents"][0]) == 0:
        response = "I don't have any memory about that yet."
    else:
        # Get memories
        memories = results["documents"][0]
        
        
        memories_text = "\n".join([f"- {m}" for m in memories])
        
        # Use LLM to generate natural response
        prompt = f"""You are a helpful personal assistant. The user asked: "{user_query}"

Your memories about this:
{memories_text}

Answer their question naturally in 1-2 sentences. Be direct and conversational.
Always use "your" or "you" when referring to the user, never "my" or "I" when answering about them.
Don't say "I remember" or "Based on my memory". Just answer naturally.
The key addition is: `Always use "your" or "you" when referring to the user, never "my" or "I" when answering about them.`

Answer:"""
        llm_response = get_llm().invoke(prompt)
        response = llm_response.content.strip()
    
    state.messages.append({"role": "assistant", "content": response})
    return state