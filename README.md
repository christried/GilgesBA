# AI Customer Support Chat App

![Project Status](https://img.shields.io/badge/status-in%20development-yellow)

A modern web application that provides AI-powered customer support chat functionality built with Angular and Flask.

## 📝 Overview

This project consists of a responsive chat interface that allows customers to get immediate support through an AI assistant. The application includes features like chat history, the ability to contact real staff members, and feedback submission.

## 🛠️ Tech Stack

### Frontend

- **Angular** with Material UI components
- **Signal-based state management** for reactive UI updates
- **Responsive design** for all device types (WiP!)

### Backend

- **Flask** REST API
- **OpenAI API** integration using GPT-4o mini for AI responses
- **Cross-Origin Resource Sharing (CORS)** support (WiP!)

## 🔍 Key Features

- Real-time chat interface with the AI assistant
- Health monitoring endpoint
- Responsive UI with Material design

## 🚀 Getting Started

### Prerequisites

- Node.js 16+ and npm
- Python 3.8+
- OpenAI API key

### Installation

1. **Clone the repository**

   ```bash
   git clone [https://github.com/christried/ChatBotBA]
   cd [ChatBotBA]
   ```

2. **Set up the backend**

   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt

   # Create a .env file with your OpenAI API key
   echo "OPENAI_API_KEY=your-api-key-here" > .env

   # Start the Flask server
   python app.py
   ```

3. **Set up the frontend**

   ```bash
   cd ..
   npm install
   ng serve
   ```

4. **Open the application**

   Navigate to `http://localhost:4200` in your browser

## 📸 Screenshots

[Coming soon]

## 🔮 Future Enhancements

- User authentication
- Chat conversation persistence
- Option to contact human staff when needed
- Chat history and context preservation
- Enhanced analytics for customer support insights
- Improved AI model with custom training

---

> ⚠️ **Note**: This project is in early development stage and everything is subject to change.
