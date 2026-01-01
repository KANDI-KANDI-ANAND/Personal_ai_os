from ..tool.email_tool import send_email
from ..llm import get_llm
import re

def send_email_node(state):
    user_msg = state.messages[-1]["content"]

    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    email_match = re.search(email_pattern, user_msg)
    
    if not email_match:
        state.messages.append({
            "role": "assistant",
            "content": "Please provide a valid email address."
        })
        return state
    
    to_email = email_match.group(0)

    prompt = f"""
Extract email details from the user message.
Understand the user messsage and find the body content which the user want to send in the email.
Just create short subject about the body content.
User message:
"{user_msg}"
Email address is: {to_email}
dont extract the exact user message.

Understand what the user wants to say and create:
1. A SHORT subject line (3-5 words)
2. A brief body content (2-3 sentences)

Just create short subject about the content.
Don't extract the exact user message.

Return in this exact format:
TO: <email>
SUBJECT: <short subject>
BODY: <email body>
"""

    llm = get_llm()
    response = llm.invoke(prompt).content.strip()

    subject_match = re.search(r"SUBJECT:\s*(.*?)(?=BODY:|$)", response, re.DOTALL)
    body_match = re.search(r"BODY:\s*(.*?)$", response, re.DOTALL)

    if not (subject_match and body_match):
        state.messages.append({
            "role": "assistant",
            "content": "I couldn't extract the email details clearly. Please rephrase."
        })
        return state

    subject = subject_match.group(1).strip()
    body = body_match.group(1).strip()

    send_email(to_email, subject, body)

    state.messages.append({
        "role": "assistant",
        "content": f"I’ve sent the email to {to_email}."
    })

    return state
