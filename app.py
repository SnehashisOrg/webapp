from sqlalchemy import create_engine
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response, HTTPException, status
import os
import uvicorn
import json

load_dotenv()

app = FastAPI()

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
            print("Connection Successful!")
            return True
    except Exception as e:
        print(e)
        raise e

@app.get("/healthz")
async def healthcheck(request: Request, response: Response):
    print("DEBUG: ", request.body())
    if await request.body():
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    try:
        if get_database_connection():
            return Response(status_code=status.HTTP_200_OK, headers=HEADERS)
    except Exception as e:
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, headers=HEADERS)
    
@app.post("/healthz")
def healthcheck():
    return Response(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, headers=HEADERS)

@app.put("/healthz")
def healthcheck():
    return Response(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, headers=HEADERS)

@app.patch("/healthz")
def healthcheck():
    return Response(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, headers=HEADERS)

@app.delete("/healthz")
def healthcheck():
    return Response(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, headers=HEADERS)

@app.head("/healthz")
def healthcheck():
    return Response(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, headers=HEADERS)

@app.options("/healthz")
def healthcheck():
    return Response(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, headers=HEADERS)
    
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)