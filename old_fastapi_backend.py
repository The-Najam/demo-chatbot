from fastapi import FastAPI
from src.pipeline import full_pipeline
from model.schemas import chatRequest
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from config.logger import logger
from model.schemas import emailform
from src.database import database_connection, notifier, table_creation
import time


app = FastAPI()

@app.get("/")
def serve_ui():
    return FileResponse("index.html")



origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
def get_response(request: chatRequest):
    try:
        result = full_pipeline(request.query, request.history)
        logger.info("Successfully Get Result")
        show_form = "For further details on assistance, please contact the team." in result
        return {"response": result, "show_form": show_form}
    except Exception as e:
        logger.info("Failed To get result %s", e)


    
@app.post("/leads")
def form_data(form: emailform):
    db_connection, cursor = database_connection()
    table_creation(db_connection, cursor)
    try:
        timestamp = int(time.time())
        cursor.execute("""INSERT INTO LEADS (name, email, question, message, timestamp) VALUES(?,?,?,?,?)""",
            (
                form.name,
                form.email,
                form.question,
                form.message,
                timestamp  
            ))
        db_connection.commit()
        db_connection.close()
        name = form.name
        email = form.email
        question = form.question
        message = form.message
        notifier(name,email,question,message)
        return {"Response" : "Response Submitted"}
    except Exception as e:
        logger.error(f"Lead submission failed: {e}")
        return {"Response": "error"}
    


