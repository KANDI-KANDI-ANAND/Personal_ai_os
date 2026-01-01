import os
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import asyncio

# Get from https://my.telegram.org/apps
API_ID = int(os.getenv("TELEGRAM_API_ID", "36333390"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "f6f304bf09bf2e8bc2b7855723f10c80")
PHONE_NUMBER = os.getenv("TELEGRAM_PHONE_NUMBER", "+918688061476")

SESSION_NAME = "personal_ai_os"


async def get_telegram_client():
    """Get authenticated Telegram client"""
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    
    if not client.is_connected():
        await client.connect()
        
        if not await client.is_user_authorized():
            await client.send_code_request(PHONE_NUMBER)
            
            try:
                await client.sign_in(PHONE_NUMBER, input('Enter verification code: '))
            except SessionPasswordNeededError:
                await client.sign_in(password=input('Enter 2FA password: '))
    
    return client


async def send_telegram_message(contact_name: str, message: str):
    """Send message to contact via personal Telegram account"""
    try:
        client = await get_telegram_client()
        
        contact_name_clean = contact_name.lower().strip()
        # Remove emojis and special chars for matching
        contact_name_clean = ''.join(c for c in contact_name_clean if c.isalnum() or c == ' ')
        
        entity = None
        found_contact = None
        exact_match = False
        
        # Find contact by name (exact match first, then fuzzy)
        async for dialog in client.iter_dialogs():
            dialog_name_lower = dialog.name.lower().strip()
            dialog_name_clean = ''.join(c for c in dialog_name_lower if c.isalnum() or c == ' ')
            
            # Exact match - contact name matches exactly
            if dialog_name_lower == contact_name_clean or dialog_name_clean == contact_name_clean:
                entity = dialog.entity
                found_contact = dialog.name
                exact_match = True
                print(f"✅ Found exact match: {found_contact}")
                break
        
        # If no exact match, try partial match - but only if contact name is in dialog name
        if not exact_match:
            async for dialog in client.iter_dialogs():
                dialog_name_lower = dialog.name.lower().strip()
                
                # Only match if the search term is a meaningful substring
                # e.g., "arvi" in "• Arvi 💝" but NOT "arvi" in "Telegram_Notify_bot"
                if len(contact_name_clean) >= 3:  # Minimum 3 characters for partial match
                    if contact_name_clean in dialog_name_lower:
                        entity = dialog.entity
                        found_contact = dialog.name
                        print(f"✅ Found partial match: {found_contact}")
                        break
        
        if not entity or not found_contact:
            print(f"❌ Could not find Telegram contact '{contact_name}'")
            return f"❌ Could not find Telegram contact '{contact_name}'"
        
        # Send message
        await client.send_message(entity, message)
        
        print(f"✓ Message sent to {found_contact}")
        return f"✓ Message sent to {found_contact} via Telegram"
        
    except Exception as e:
        print(f"❌ Error sending message: {str(e)}")
        return f"❌ Error: {str(e)}"
    finally:
        if client.is_connected():
            await client.disconnect()


def send_message_sync(contact_name: str, message: str):
    """Synchronous wrapper"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(send_telegram_message(contact_name, message))
        loop.close()
        return result
    except Exception as e:
        return f"❌ Error: {str(e)}"


async def get_telegram_contacts_list():
    """Get list of all Telegram contacts"""
    try:
        client = await get_telegram_client()
        contacts = []
        
        async for dialog in client.iter_dialogs():
            # Only get direct contacts, not groups or bots
            if dialog.is_user:
                contacts.append(dialog.name)
        
        await client.disconnect()
        return contacts
        
    except Exception as e:
        print(f"❌ Error getting contacts: {str(e)}")
        return []


def get_all_telegram_contacts():
    """Synchronous wrapper to get contacts"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        contacts = loop.run_until_complete(get_telegram_contacts_list())
        loop.close()
        return contacts
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []