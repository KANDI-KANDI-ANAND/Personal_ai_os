from ..tools import send_message, get_all_telegram_contacts
from ..llm import get_llm
import json
import re

def send_message_node(state):
    user_msg = state.messages[-1]["content"]
    contacts_list = get_all_telegram_contacts()
    
    if not contacts_list:
        print(f"❌ No Telegram contacts available")
        return state
    
    contacts_str = "\n".join(contacts_list)
    
    # Get conversation history to understand context
    conversation_history = "\n".join([
        f"{msg['role']}: {msg['content'][:100]}" 
        for msg in state.messages if msg['role'] in ['user', 'assistant']
    ])
    
    prompt = f"""Extract contact name and message content from user request.

CONVERSATION HISTORY:
{conversation_history}

AVAILABLE CONTACTS:
{contacts_str}

CURRENT USER REQUEST:
"{user_msg}"

EXTRACTION RULES:
1. Identify the person's name mentioned (e.g., arvi, brother, swetha, venu)
   - Could be explicit: "send message to arvi"
   - Could be pronoun: "notify him" (refer to previously mentioned name)
2. Match EXACTLY to contact from list above (case-insensitive)
3. Extract the message content - understand full context:
   - If single intent (only send message): extract what user wants to say
   - If multi-intent (meeting + notify): create message based on the action (e.g., meeting details)
4. Use conversation history to understand pronouns and context

CONTACT MATCHING:
- "arvi" → "• Arvi 💝"
- "brother" → "• Brother ❤️‍🔥"
- "venu" → "Venu Boda 2"
- "swetha" → "Swetha"
- "surekha" → "Surekha"
- Check emojis and special characters carefully

MESSAGE CREATION:
- Single intent "send message to X saying Y" → Use Y as message
- Multi-intent "add meeting with X at time and notify" → Create and send message to X about meeting + time 
- Single intent "message X about topic" → Create message about that topic
- Multi-intent "add event... remind me... notify X" → Message should reference the event

PRONOUN HANDLING:
- "him/her/them" refers to the name mentioned earlier in SAME request
- Example: "add meeting with arvi at 7am and notify him" → him = arvi

CRITICAL RULES:
- Return ONLY valid JSON
- Recipient MUST be from contacts list
- Message must be natural and based on actual context
- Do NOT invent contact names
- Do NOT return error messages

CRITICAL: Return ONLY pure JSON on ONE LINE, absolutely no explanation, no markdown, no backticks, no extra text before or after:
{{"recipient":"contact_name","message":"what_to_say"}}

EXAMPLES:

Single Intent:
"send message to arvi saying hello"
→ {{"recipient": "• Arvi 💝", "message": "Hello! How are you?"}}

"message swetha about the project"
→ {{"recipient": "Swetha", "message": "Hi Swetha, let's discuss the project status"}}

Multi-Intent:
"add meeting with arvi tomorrow at 10am and remind me and notify him"
→ {{"recipient": "• Arvi 💝", "message": "We have a meeting tomorrow at 10am"}}

"add event with brother at 5pm and send him message"
→ {{"recipient": "• Brother ❤️‍🔥", "message": "We have an event tomorrow at 5pm"}}

"plan my day and send updates to swetha"
→ {{"recipient": "Swetha", "message": "Here's my plan for today"}}

Return ONLY JSON:"""

    response = get_llm().invoke(prompt)
    data = response.content.strip()


    try:
        # Extract JSON
        start_idx = data.find('{')
        end_idx = data.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            print(f"❌ No JSON found in response")
            return state
            
        json_str = data[start_idx:end_idx]
        details = json.loads(json_str)
        
        recipient = details.get("recipient", "").strip()
        message = details.get("message", "").strip()
        
        print(f"DEBUG: Extracted recipient='{recipient}', message='{message}'")
        
        # Validate recipient
        if not recipient or len(recipient) < 2:
            print(f"❌ Invalid recipient: {recipient}")
            return state
        
        # Validate message
        if not message or len(message) < 2:
            print(f"❌ Invalid message: {message}")
            return state
        
        # Check for error messages
        error_keywords = ["could not", "cannot", "error", "not found", "unable", "i don't"]
        if any(keyword in message.lower() for keyword in error_keywords):
            print(f"❌ Message contains error: {message}")
            return state
        
        # Find exact match in contacts
        matched_contact = None
        for contact in contacts_list:
            if contact.lower() == recipient.lower():
                matched_contact = contact
                break
        
        # If no exact match, try substring match
        if not matched_contact:
            for contact in contacts_list:
                if recipient.lower() in contact.lower():
                    matched_contact = contact
                    break
        
        if not matched_contact:
            print(f"❌ Contact '{recipient}' not found in list")
            return state
        
        recipient = matched_contact
        print(f"✅ Sending message to '{recipient}': {message}")
        
        # Send message
        result = send_message(
            recipient_name=recipient,
            message=message
        )
        
        state.messages.append({
            "role": "assistant",
            "content": result
        })

    except (json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"❌ Parse error: {str(e)}")
        return state

    return state