from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.database.session import get_db, init_db
from src.database import crud
from src.services.parser import parse_capture_text

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Mindwater API is running", "environment": "production"}

class CaptureRequest(BaseModel):
    text: str
    source: str = "api"

@app.on_event("startup")
def startup_event():
    init_db()

@app.post("/capture")
def capture_item(request: CaptureRequest, db: Session = Depends(get_db)):
    # Parse the text (for future structured use, though spec says save raw text)
    parsed = parse_capture_text(request.text)
    
    # Save to Inbox table
    inbox_item = crud.create_inbox_item(db, raw_text=request.text, source_tag=request.source)
    
    return {
        "status": "success",
        "item": {
            "id": inbox_item.id,
            "raw_text": inbox_item.raw_text,
            "source": inbox_item.source_tag,
            "timestamp": inbox_item.timestamp
        }
    }
