from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
import datetime
import uuid
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
import json
from flask_mail import Mail, Message as MailMessage
import sqlite3
from trello_integration import TrelloIntegration

# Load environment variables from .env file
load_dotenv()
# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Get the OpenAI API key from environment variables and set up OpenAI client
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(
  api_key=api_key,
)

# Get the absolute path of the current directory (where app.py is located) to create the database file in the same directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'messages.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Define Message model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.String(36), nullable=False)  # Use UUID
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    openai_thread_id = db.Column(db.String(100), nullable=True)


class TrelloTracking(db.Model):
    """Track which conversations have been saved to Trello"""
    conversation_id = db.Column(db.String(36), primary_key=True)
    trello_card_id = db.Column(db.String(100), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
# Helper functions for Trello tracking

def is_conversation_saved_to_trello(conversation_id):
    """Check if a conversation has already been saved to Trello"""
    tracking = TrelloTracking.query.filter_by(conversation_id=conversation_id).first()
    return tracking is not None

def mark_conversation_as_saved(conversation_id, trello_card_id):
    """Mark a conversation as saved to Trello"""
    tracking = TrelloTracking(
        conversation_id=conversation_id,
        trello_card_id=trello_card_id
    )
    db.session.add(tracking)
    db.session.commit()

# Initialize database
with app.app_context():
    db.create_all()

# Create a vector store to upload and store all files
vector_store = client.vector_stores.create(        # Create vector store
    name="Support Knowledge Base",
)

# Convert product data XLSX to JSON for Assistant compatibility
xlsx_path = os.path.join(BASE_DIR, "../docs/Kontext/product_data.xlsx")
json_path = os.path.join(BASE_DIR, "../docs/Kontext/product_data.json")

try:
    df = pd.read_excel(xlsx_path)
    df = df.fillna("")  # Replace NaNs with empty strings for JSON compatibility
    json_data = df.to_dict(orient="records")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    print(f"Converted Excel to JSON: {json_path}")
except Exception as e:
    print(f"Failed to convert Excel to JSON: {e}")

# List of file paths to upload
file_paths = [
    os.path.join(BASE_DIR, "../docs/Kontext/faq.pdf"),
    os.path.join(BASE_DIR, "../docs/Kontext/shipping_and_returns.pdf"),
    json_path,
    os.path.join(BASE_DIR, "../docs/Kontext/ci_and_communication_guidelines.pdf"),
]

# Upload each file to the vector store (could use batch-uploads but for simplicity we upload one by one)
for file_path in file_paths:
    try:
        client.vector_stores.files.upload_and_poll(
            vector_store_id=vector_store.id,
            file=open(file_path, "rb"),
        )
        print(f"Successfully uploaded: {file_path}")
    except Exception as e:
        print(f"Error uploading {file_path}: {e}")

client.vector_stores.update(
    vector_store_id=vector_store.id,
    expires_after={
        "anchor": "last_active_at",
        "days": 7
    }
)

# Create an Assistant with the uploaded file
assistant = client.beta.assistants.create(
    instructions=(
        "You are a helpful customer support assistant for IMPACTFUL Drinks GmbH and before answering, you will always look at the provided documents." 
        "Be concise, friendly, and helpful. If the Customer contacts you in German, always default to a respectful 'Du'"
        "IMPORTANT: You will always use the provided documents to answer user inquiries as per the following guidelines:"
        "Make double sure that you communicate with the user according to the communication guidelines document"
        "Use the uploaded FAQ document to provide accurate information about the company's policies and procedures."
        "Use the product data to answer questions about products. "
        "Use the shipping and returns document to answer questions about shipping and returns. "
        "You are only allowed to help the customer with inquiries related to the company and its products and will always refer back to this, if anything else is asked."
        "You can only communicate in either English or German, depending on what language the customer is choosing, but it is always possible for you to switch languages when the customer demands it"
        "All of the information you provide should be in your own words but you cannot provide any personal opinions or make assumptions."
        "ESCALATION GUIDELINE: You must keep track of your own attempts to answer a user's question. If you fail to provide a helpful and relevant answer in two consecutive turns for the same user query, you MUST call the `open_real_person_dialog` function. Do not attempt to answer a third time. A failure is when the user indicates that your answer was not helpful, or asks the same question again."
    ),
    name="Happy Customer Support Assistant",
    tools=[
        {"type": "file_search"},
        {
            "type": "function",
            "function": {
                "name": "open_real_person_dialog",
                "description": "Opens a dialog for the user to enter their email to speak with a human agent. Call this function after failing to provide a satisfactory answer twice.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    ],
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    model="gpt-4.1-nano"
)

# Flask mail config
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD') 
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

def get_db_connection():
    conn = sqlite3.connect('messages.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle incoming chat messages and generate AI responses using Assistants API"""
    try:
        data = request.json
        user_message = data.get('message', '')
        conversation_id = data.get('conversation_id')
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        # Get or create thread_id associated with this conversation
        thread_id = None
        
        # Create new conversation if none exists
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            # Create a new thread with OpenAI
            thread = client.beta.threads.create()
            thread_id = thread.id
        else:
            # Find existing thread_id from database
            existing_msg = Message.query.filter_by(conversation_id=conversation_id).first()
            if existing_msg and existing_msg.openai_thread_id:
                thread_id = existing_msg.openai_thread_id
            else:
                # Create a new thread if we can't find one
                thread = client.beta.threads.create()
                thread_id = thread.id
        
        # Store user message in database
        new_user_message = Message(
            conversation_id=conversation_id,
            role="user",
            content=user_message,
            openai_thread_id=thread_id
        )
        db.session.add(new_user_message)
        db.session.commit()

        # Add the user message to the thread
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message,
        )

        # Run the assistant on the thread
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant.id,
            additional_instructions=None,             
        )   

        # Wait for the run to complete
        while run.status in ["queued", "in_progress"]:
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )

        # If run requires action, handle the tool call
        if run.status == "requires_action":
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            if tool_calls and tool_calls[0].function.name == "open_real_person_dialog":
                # Don't submit any tool output, just tell the frontend to open the dialog
                return jsonify({
                    "action": "open_real_person_dialog",
                    "conversation_id": conversation_id
                })
        
        # If run completed successfully, get the assistant's response
        if run.status == "completed":
            # Get the messages from the thread
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            
            # Get the last assistant message
            assistant_messages = [msg for msg in messages.data if msg.role == "assistant"]
            if assistant_messages:
                latest_message = assistant_messages[0]
                assistant_message_content = latest_message.content[0].text.value
                
                # Store assistant message in database
                new_assistant_message = Message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=assistant_message_content,
                    openai_thread_id=thread_id
                )
                db.session.add(new_assistant_message)
                db.session.commit()
                
                return jsonify({
                    "message": assistant_message_content,
                    "conversation_id": conversation_id
                })
            else:
                return jsonify({"error": "No response from assistant"}), 500
        else:
            return jsonify({"error": f"Run failed with status: {run.status}"}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@app.route('/api/messages', methods=['GET'])
def get_messages():
    """Fetch all stored messages"""
    messages = Message.query.order_by(Message.timestamp.desc()).all()
    return jsonify([
        {"id": msg.id, "user_message": msg.user_message, "assistant_message": msg.assistant_message, "timestamp": msg.timestamp}
        for msg in messages
    ])


@app.route('/api/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Fetch all messages in a specific conversation"""
    messages = Message.query.filter_by(conversation_id=conversation_id)\
                          .order_by(Message.timestamp).all()
    return jsonify([
        {
            "id": msg.id, 
            "role": msg.role, 
            "content": msg.content, 
            "timestamp": msg.timestamp.isoformat()
        }
        for msg in messages
    ])


# Initialize Trello integration
trello = TrelloIntegration()

# endpoint to finalize a conversation and save it to Trello
@app.route('/api/conversations/<conversation_id>/finalize', methods=['POST'])
def finalize_conversation(conversation_id):
    """Finalize a conversation and save it to Trello"""
    try:
        # Check if already saved to Trello
        if is_conversation_saved_to_trello(conversation_id):
            return jsonify({
                "status": "success",
                "message": "Conversation already saved to Trello"
            })
    
        # Get all messages for this conversation
        messages = Message.query.filter_by(conversation_id=conversation_id)\
                         .order_by(Message.timestamp).all()
        
        # Convert to format expected by Trello integration
        formatted_messages = [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp
            }
            for msg in messages
        ]
        
        # Create a Trello card for this conversation
        card_data = trello.create_card_from_conversation(conversation_id, formatted_messages)
        
        if card_data:
            # Mark conversation as saved
            mark_conversation_as_saved(conversation_id, card_data.get("id"))
            
            return jsonify({
                "status": "success",
                "message": "Conversation saved to Trello",
                "card_id": card_data.get("id"),
                "card_url": card_data.get("shortUrl")
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to save conversation to Trello"
            }), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sync/trello', methods=['POST'])
def sync_conversations_to_trello():
    """Synchronize all unsaved conversations to Trello"""
    try:
        # Get all unique conversation IDs from the database
        conversations = db.session.query(Message.conversation_id).distinct().all()
        conversation_ids = [conv[0] for conv in conversations]
        
        # Track results
        results = {
            "total": len(conversation_ids),
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "details": []
        }
        
        # Process each conversation
        for conv_id in conversation_ids:
            # Check if this conversation has already been processed
            if is_conversation_saved_to_trello(conv_id):
                results["skipped"] += 1
                results["details"].append({
                    "conversation_id": conv_id,
                    "status": "skipped",
                    "reason": "Already saved to Trello"
                })
                continue
                
            # Get all messages for this conversation
            messages = Message.query.filter_by(conversation_id=conv_id)\
                          .order_by(Message.timestamp).all()
            
            if not messages:
                results["skipped"] += 1
                results["details"].append({
                    "conversation_id": conv_id,
                    "status": "skipped",
                    "reason": "No messages found"
                })
                continue
                
            # Format messages for Trello
            formatted_messages = [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp
                }
                for msg in messages
            ]
            
            # Create a Trello card
            card_data = trello.create_card_from_conversation(conv_id, formatted_messages)
            
            if card_data:
                # Mark conversation as saved
                mark_conversation_as_saved(conv_id, card_data.get("id"))
                results["success"] += 1
                results["details"].append({
                    "conversation_id": conv_id,
                    "status": "success",
                    "card_id": card_data.get("id"),
                    "card_url": card_data.get("shortUrl")
                })
            else:
                results["failed"] += 1
                results["details"].append({
                    "conversation_id": conv_id,
                    "status": "failed",
                    "reason": "Trello API error"
                })
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/api/escalate', methods=['POST'])
def escalate():
    data = request.json
    user_message = data.get('message', 'No message provided')
    conversation_id = data.get('conversation_id', 'N/A')
    email = data.get('email', 'No email provided')

    # --- Trello-Integration ---
    try:
        conn = get_db_connection()
        # get conversation messages
        messages_from_db = conn.execute(
            'SELECT role, content FROM message WHERE conversation_id = ? ORDER BY timestamp',
            (conversation_id,)
        ).fetchall()
        conn.close()

        # convert DB-Rows to the required dictionary format
        conversation_history = [{"role": msg['role'], "content": msg['content']} for msg in messages_from_db]

        # Add the user's last escalating message
        conversation_history.append({"role": "user", "content": user_message})

        # Create the Trello card
        trello = TrelloIntegration()
        if trello.api_key:  # Check if Trello is configured
            trello.create_card_from_conversation(conversation_id, conversation_history)
        else:
            print("Trello is not configured, skipping card creation.")

    except Exception as e:
        print(f"Error with Trello integration: {e}")

    try:
        msg = MailMessage(
            'Chat Escalation',
            sender=os.getenv('MAIL_USERNAME'),
            recipients=['gilges.dominik@gmail.com']
        )
        msg.body = f"An escalation has been requested.\n\nEmail: {email}\nConversation ID: {conversation_id}\nLast Message: {user_message}\n\nA Trello card with the complete history has been created."
        mail.send(msg)
        return jsonify({"status": "Escalation successful"})

    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({"status": "Escalation failed"}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple endpoint to verify the API is running"""
    return jsonify({
        "status": "ok",
        "version": "0.0.1",
        "timestamp": datetime.datetime.now().isoformat()
    })


# run local server
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)