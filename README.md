#  Autonomous AI Agent

A simple backend-based AI agent built with **FastAPI** that can intelligently decide whether to use tools or respond directly to user tasks.

---

## 🚀 Overview

This project demonstrates a basic **agent architecture** where:

* Simple tasks are handled using rule-based logic
* Complex tasks are handled using a local LLM
* Results are stored and tracked in a database

---

## 🧰 Tech Stack

* ⚡ FastAPI
* 🐍 Python
* 🗄️ SQLAlchemy + MySQL
* 🧠 Ollama (Local LLM)

---

## ✨ Key Features

* 🔹 Tool-based execution system
* 🔹 Fast rule-based routing (no LLM for simple tasks)
* 🔹 LLM-based decision making
* 🔹 Task history storage
* 🔹 Clean API design
* 🔹 Basic conversation support

---

## 🧠 System Flow

```
User Request
     ↓
FastAPI Endpoint
     ↓
Agent Processing
     ↓
 ┌───────────────┬────────────────┐
 │ Fast Routing  │ LLM Decision   │
 └───────────────┴────────────────┘
           ↓
     Tool Execution
           ↓
     Store in Database
           ↓
        Response
```

---

## 🛠️ Tools Available

| Tool        | Description               |
| ----------- | ------------------------- |
| Calculator  | Solves math expressions   |
| Summarizer  | Summarizes text (5 lines) |
| Planner     | Generates simple steps    |
| Word Count  | Counts words in text      |
| Vowel Count | Counts vowels             |
| Digit Count | Counts digits             |

---

## 📁 Project Structure

```id="v7r5r1"
backend/
│
├── main.py              # FastAPI entry point
├── agent/               # Core agent logic
├── database/            # Models & DB setup
├── tools/               # Tool implementations
├── frontend/            # UI files
└── schemas/             # Request/response models
```

---

## ▶️ Run Locally

### 1. Install dependencies

```id="0y3rjq"
pip install -r requirements.txt
```

### 2. Start server

```id="4rb9co"
uvicorn main:app --reload
```

### 3. Open in browser

```id="k1o4mh"
http://127.0.0.1:8000
```

---

## 📌 API Example

### 🔹 POST `/run-agent`

**Request**

```id="m2h7oq"
{
  "task": "calculate 10 + 5"
}
```

**Response**

```id="6e6g6k"
{
  "task": "calculate 10 + 5",
  "plan": ["Fast route → calculator"],
  "observations": ["15"],
  "result": "15"
}
```

---

## 🗄️ Database

Stores:

* Task
* Plan
* Observations
* Result
* Timestamp

---

## ⚠️ Notes

* LLM runs locally using **Ollama**
* No internet required for inference
* Works best with configured local model

---

## 👨‍💻 Author

**Kinchit Gupta**
