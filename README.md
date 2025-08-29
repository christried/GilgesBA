# AI Customer Support Chatbot (Bachelor Thesis Project)

**Important Note**: This project was developed as the practical component of my bachelor thesis, "Eigenständige Implementierung eines KI-basierten Chatbots mit Angular und Python". It serves as a proof-of-concept and is no longer actively maintained. The code is provided as-is for demonstration and academic purposes.

This repository contains the source code for an AI-powered customer support chatbot, featuring an Angular frontend and a Python (Flask) backend.

## 📝 Overview

The application provides a web-based chat interface where users can interact with an AI assistant. The assistant is powered by the OpenAI API and is designed to answer customer queries based on a provided knowledge base. If the AI cannot resolve an issue, the conversation can be escalated and a ticket is automatically created in Trello for a human agent.

## 🛠️ Tech Stack

**Frontend**: Angular, Angular Material, TypeScript
**Backend**: Python, Flask, SQLAlchemy
**AI & Services**: OpenAI API, Trello API

## 🚀 Getting Started

Follow these instructions to get a local copy up and running for development and testing.

### Prerequisites

Before you begin, ensure you have the following installed:

- [Node.js (v18 or newer)](https://nodejs.org/en)
- [Python (v3.8 or newer)](https://www.python.org/)
- [An OpenAI API Key](https://platform.openai.com/api-keys)
- [A Trello API Key, Token, and List ID](https://developer.atlassian.com/cloud/trello/guides/rest-api/api-introduction/)

1. Clone the Repository
   First, clone the project to your local machine:
   `git clone [https://github.com/christried/GilgesBA.git](https://github.com/christried/GilgesBA.git)`
   `cd GilgesBA`

2. Backend Setup (Flask)
   The backend powers the API and connects to the external services.

### Navigate to the backend directory

`cd backend`

### Create a Python virtual environment

`python -m venv venv`

### Activate the virtual environment

#### On Windows:

`venv\Scripts\activate`

#### On macOS/Linux:

`source venv/bin/activate`

### Create a .env file to store your API keys

touch .env

Now, open the newly created .env file in the backend directory and add your credentials. Do NOT ever commit this file.
.env
OPENAI_API_KEY="your-openai-api-key-here"
TRELLO_API_KEY="your-trello-api-key-here"
TRELLO_TOKEN="your-trello-token-here"
TRELLO_LIST_ID="your-trello-list-id-for-tickets"

3. Frontend Setup (Angular)
   The frontend contains the user interface for the chat.

### Navigate back to the project's root directory

`cd ..`

### Install the required npm packages

`npm install`

4. Running the Application
   You need to run both the backend and frontend servers at the same time in separate terminal windows.

Terminal 1: Start the Backend Server
`cd backend`

### Make sure your virtual environment is still active

`python app.py`

The Flask API should now be running on http://localhost:5000.

Terminal 2: Start the Frontend Server

### From the project's root directory

`ng serve`

The Angular app should now be running on http://localhost:4200.
Open your web browser and navigate to http://localhost:4200 to use the chatbot.

## 🔮 Possible Enhancements

- Direct Webshop Integration: Connect the chatbot to a live e-commerce platform to associate chat histories with customer accounts, enabling a more personalized and context-aware service.
- Live Chat Handover: Instead of escalating to email, implement a feature where a human agent can seamlessly take over the chat from the bot in real-time.
- Self-Hosted Language Model: Replace the external OpenAI API with a self-trained model to gain full control over data processing, potentially reduce costs, and better address GDPR concerns.
- Dynamic Knowledge Base: Enhance the "Knowledge Module" to connect to a dynamic database or pull information directly from Trello, allowing for more current and accurate responses.
- Advanced API Features: Implement native OpenAI API features that were not used in this project, such as image input processing and response streaming, to create a more interactive user experience.
