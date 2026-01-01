from langgraph.graph import StateGraph, END

from .state import AgentState
from .nodes.router import router_node
from .nodes.recall_memory import recall_memory_node
from .nodes.save_memory import save_memory_node
from .nodes.check_memory import check_memory_node
from .nodes.plan_tasks import plan_tasks_node
from .nodes.conversation import conversation_node
from .nodes.update_memory import update_memory_node
from .nodes.calendar_action import calendar_action_node
from .nodes.delete_calendar import delete_calendar_node
from .nodes.update_calendar import update_calendar_node
from .nodes.reminder_action import reminder_action_node
from .nodes.send_email import send_email_node
from .nodes.send_message_node import send_message_node
from .nodes.plan_steps import plan_steps_node
from .nodes.execute_steps import execute_steps_node
def build_graph():

    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("router", router_node)
    graph.add_node("check_memory", check_memory_node)
    graph.add_node("plan_tasks", plan_tasks_node)
    graph.add_node("save_memory", save_memory_node)
    graph.add_node("recall_memory", recall_memory_node)
    graph.add_node("conversation", conversation_node)
    graph.add_node("update_memory", update_memory_node)
    graph.add_node("calendar_action", calendar_action_node)
    graph.add_node("delete_calendar", delete_calendar_node)
    graph.add_node("update_calendar", update_calendar_node)
    graph.add_node("reminder_action", reminder_action_node)
    graph.add_node("send_email", send_email_node)
    graph.add_node("send_message", send_message_node)
    graph.add_node("plan_steps", plan_steps_node)
    graph.add_node("execute_steps", execute_steps_node)
    # Set entry point
    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        lambda state: "plan_steps" if state.intent in [
            "calendar", "delete_calendar", "update_calendar", "set_reminder",
            "send_message", "send_email", "plan_tasks",
            "save_memory", "recall_memory", "update_memory"
        ] else "conversation",
        {
            "plan_steps": "plan_steps",
            "conversation": "conversation"
        }
    )

    graph.add_edge("plan_steps", "execute_steps")

    
    # Connect edges
    graph.add_conditional_edges(
        "execute_steps",
        lambda state: state.intent if state.intent else "exit", 
        {
            "save_memory": "save_memory",
            "recall_memory": "recall_memory",
            "plan_tasks": "plan_tasks",
            "update_memory": "update_memory",
            "calendar": "calendar_action",
            "delete_calendar": "delete_calendar",
            "update_calendar": "update_calendar",
            "set_reminder": "reminder_action",
            "send_email": "send_email",
            "send_message": "send_message",
            "exit": END
        }
    )

    graph.add_edge("calendar_action", "execute_steps")
    graph.add_edge("delete_calendar", "execute_steps")
    graph.add_edge("update_calendar", "execute_steps")
    graph.add_edge("reminder_action", "execute_steps")
    graph.add_edge("send_email", "execute_steps")
    graph.add_edge("send_message", "execute_steps")
    graph.add_edge("plan_tasks", "execute_steps")
    graph.add_edge("save_memory", "execute_steps")
    graph.add_edge("recall_memory", "execute_steps")
    graph.add_edge("update_memory", "execute_steps")
    graph.add_edge("conversation", END)

    
    # Compile graph
    return graph.compile()
