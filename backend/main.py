from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime

from agent.agent_core import run_agent
from database.db import engine, SessionLocal
from database.models import Base, AgentRun

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Autonomous AI Agent")

# -----------------------
# CORS
# -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Serve Frontend
# -----------------------
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/", response_class=HTMLResponse)
def serve_home():
    return FileResponse("frontend/index.html")


@app.get("/history", response_class=HTMLResponse)
def serve_history():
    return FileResponse("frontend/history.html")


# -----------------------
# DB Dependency
# -----------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------
# Request Model
# -----------------------
class TaskRequest(BaseModel):
    task: str


# -----------------------
# Run Agent
# -----------------------
@app.post("/run-agent")
def run_agent_api(request: TaskRequest, db: Session = Depends(get_db)):

    output = run_agent(request.task)

    plan = output.get("plan", "")
    observations = output.get("observations", [])
    result = output.get("result", "")

    db_entry = AgentRun(
        task=request.task,
        plan=str(plan),
        observations=str(observations),
        result=str(result),
        created_at=datetime.utcnow()
    )

    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)

    return {
        "task": request.task,
        "plan": plan,
        "observations": observations,
        "result": result,
    }


# -----------------------
# Get History
# -----------------------
@app.get("/agent-runs")
def get_all_runs(db: Session = Depends(get_db)):
    runs = db.query(AgentRun).all()

    return [
        {
            "id": run.id,
            "task": run.task,
            "result": run.result,
            "created_at": run.created_at,
        }
        for run in runs
    ]
@app.delete("/clear-history")
def clear_history(db: Session = Depends(get_db)):
    db.query(AgentRun).delete()
    db.commit()
    return {"message": "All history cleared"}
