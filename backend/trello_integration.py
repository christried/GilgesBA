import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class TrelloIntegration:
    """
    Class to handle Trello API integration for saving chat conversations as cards.
    """
    
    def __init__(self):
        """Initialize Trello API credentials from environment variables."""
        self.api_key = os.getenv('TRELLO_API_KEY')
        self.token = os.getenv('TRELLO_TOKEN')
        self.list_id = os.getenv('TRELLO_LIST_ID')
        
        # Validate if required credentials are available
        if not all([self.api_key, self.token, self.list_id]):
            print("Warning: Trello API credentials not fully configured.")
    
    def create_card_from_conversation(self, conversation_id, messages):
        """
        Create a Trello card from a conversation.
        
        Args:
            conversation_id (str): The unique ID of the conversation
            messages (list): List of message objects from the conversation
        
        Returns:
            dict: The response JSON if successful, None otherwise
        """
        if not all([self.api_key, self.token, self.list_id]):
            print("Error: Trello API credentials not configured.")
            return None
        
        # Format the conversation for the card description
        formatted_conversation = self._format_conversation_summary(messages)
        
        # Create a card name with date and conversation ID
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        card_name = f"Conversation {conversation_id[:8]} - {date_str}"
        
        # Create card payload
        url = "https://api.trello.com/1/cards"
        query = {
            'idList': self.list_id,
            'name': card_name,
            'desc': formatted_conversation[:16000],  # Trello has a description length limit and this avoids errors exceeding it
            'key': self.api_key,
            'token': self.token
        }
        
        try:
            # POST request to create the card
            response = requests.post(url, params=query)
            
            # Check if the card was created successfully
            if response.status_code == 200:
                print(f"Card created successfully for conversation {conversation_id}")
                card_data = response.json()            
                return card_data
            else:
                print(f"Failed to create card. Status: {response.status_code}, Response: {response.text}")
                return None
        except Exception as e:
            print(f"Error creating Trello card: {e}")
            return None
    
    def _add_conversation_as_attachment(self, card_id, conversation_id, messages):
        """
        Add the full conversation as a text file attachment to the card.
        
        Args:
            card_id (str): The Trello card ID
            conversation_id (str): The conversation ID
            messages (list): List of message objects from the conversation
        
        Returns:
            dict: The response JSON if successful, None otherwise
        """
        # Create a temporary file with the conversation
        file_name = f"conversation_{conversation_id}.txt"
        file_path = os.path.join(os.path.dirname(__file__), file_name)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self._format_full_conversation(messages))
            
            # Prepare the file upload
            url = f"https://api.trello.com/1/cards/{card_id}/attachments"
            params = {
                'key': self.api_key,
                'token': self.token,
                'name': f"Full Conversation {conversation_id}"
            }
            
            files = {
                'file': (file_name, open(file_path, 'rb'), 'text/plain')
            }
            
            # POST request to upload attachment
            response = requests.post(url, params=params, files=files)
            
            # Close and remove the temporary file
            files['file'][1].close()
            os.remove(file_path)
            
            if response.status_code == 200:
                print(f"Attachment added successfully to card {card_id}")
                return response.json()
            else:
                print(f"Failed to add attachment. Status: {response.status_code}, Response: {response.text}")
                return None
        except Exception as e:
            print(f"Error adding attachment to Trello card: {e}")
            # Make sure to clean up the temporary file if it exists
            if os.path.exists(file_path):
                os.remove(file_path)
            return None
    
    def _format_conversation_summary(self, messages):
        """
        Format conversation for card description (shortened version).
        
        Args:
            messages (list): List of message objects from the conversation
        
        Returns:
            str: A formatted string representing the conversation summary
        """
        # Get first and last few messages for summary
        total_messages = len(messages)
        
        if total_messages <= 6:
            # If there are 6 or fewer messages, include them all
            selected_messages = messages
        else:
            # Otherwise take first 3 and last 3
            selected_messages = messages[:3] + [{"role": "system", "content": "...(conversation continued)..."}, *messages[-3:]]
        
        # Format the conversation
        summary = f"## Conversation Summary\n\n"
        summary += f"Total messages: {total_messages}\n\n"
        
        for idx, msg in enumerate(selected_messages):
            role = msg.get("role")
            content = msg.get("content")
            
            if role == "user":
                summary += f"**Customer:** {content}\n\n"
            elif role == "assistant":
                summary += f"**AI Assistant:** {content}\n\n"
            else:
                summary += f"{content}\n\n"
                
        return summary
    
    def _format_full_conversation(self, messages):
        """
        Format the full conversation for text file attachment.
        
        Args:
            messages (list): List of message objects from the conversation
        
        Returns:
            str: A formatted string representing the complete conversation
        """
        full_text = f"FULL CONVERSATION TRANSCRIPT\n"
        full_text += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for idx, msg in enumerate(messages):
            role = msg.get("role")
            content = msg.get("content")
            timestamp = msg.get("timestamp", "")
            
            if isinstance(timestamp, datetime):
                time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            else:
                time_str = str(timestamp)
                
            full_text += f"[{time_str}] "
            
            if role == "user":
                full_text += f"CUSTOMER: {content}\n\n"
            elif role == "assistant":
                full_text += f"SUPPORT: {content}\n\n"
            else:
                full_text += f"{content}\n\n"
                
        return full_text