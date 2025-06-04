# Schedulio – A Simple Calendar Chatbot

Schedulio is a lightweight meeting assistant that helps users schedule calendar events through natural language interaction.
It’s built with FastAPI and OpenAI, and allows users to book Google Calendar meetings using conversational prompts. It supports OAuth login, has a clean HTML/CSS UI, and integrates directly with the Google Calendar API.

## Features
- Chat-based interface powered by OpenAI (GPT-4o)
- Secure OAuth2 login with Google
- Real-time Google Calendar event creation
- FastAPI backend with Jinja2-powered HTML/CSS frontend
- Supports multiple test accounts for QA

## Tech Stack
- Python (FastAPI)
- OpenAI GPT-4o
- Google Calendar API
- HTML, CSS, JavaScript
- Jinja2 Templating
- OAuth2 (Google)

## Getting Started

1. Define your OAuth scopes in the [Google Cloud Console](https://console.cloud.google.com/) and download a valid `client_secret.json`.
2. Obtain your OpenAI API key and save it in a `.env` file. This is the recommended way to securely access OpenAI services.
3. (Optional but practical) Consider modifying the code based on open-source templates — it’s always smart to build on existing foundations.
4. Also, you can add a logo of your choice in index.html (line 13) to be on the top left corner of your web.

### Setup

```bash
git clone https://github.com/Serena-SA/Schedulio-a-simple-calendar-chatbot.git
cd Schedulio-a-simple-calendar-chatbot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Note: Honestly, I'm not expecting anyone to use this code, but I also wanted to practice Git and Github.
