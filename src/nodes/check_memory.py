from ..llm import get_llm
from ..memory.vectorstore import search_memory

def check_memory_node(state):
    user_query = state.messages[-1]["content"]
    results = search_memory(user_query)
    
    if results["documents"] and results["documents"][0]:
        state.memory_results = results["documents"][0]
        state.found_memory = True
        print("Memory found")
    else:
        state.found_memory = False  
        print("Not found") 
    
    return state
