from sqlalchemy import create_engine
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response, HTTPException, status
import os
import uvicorn
import json
import logging

load_dotenv()

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

USER = os.getenv("PG_USER")
PASSWORD = os.getenv("PG_PASSWORD")
HOST = os.getenv("PG_HOST")
PORT = os.getenv("PG_PORT")
DATABASE = os.getenv("PG_DATABASE")

HEADERS = {
        "Cache-Control": 'no-cache, no-store, must-revalidate;',
        "Pragma": 'no-cache',
        "X-Content-Type-Options": 'nosniff'
    }

def get_database_connection() -> bool:
    CONNECTION_STRING = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'

    engine = create_engine(CONNECTION_STRING)

    try:
        with engine.connect() as conn:
            logger.info("Connection successful!")
            return True
    except Exception as e:
        logger.info(f"Error in database connection!  {e}")
        return False

@app.get("/healthz")
async def healthcheck(request: Request, response: Response):
    if await request.body() or request.query_params:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    if not get_database_connection():
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, headers=HEADERS)
    
    return Response(status_code=status.HTTP_200_OK, headers=HEADERS)
    
@app.post("/healthz")
@app.put("/healthz")
@app.patch("/healthz")
@app.delete("/healthz")
@app.head("/healthz")
@app.options("/healthz")
def healthcheck():
    return Response(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, headers=HEADERS)
    
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)