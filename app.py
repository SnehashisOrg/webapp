from sqlalchemy import create_engine
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response, HTTPException, status
import os
import uvicorn
import json

load_dotenv()

app = FastAPI()

user = os.getenv("PG_USER")
password = os.getenv("PG_PASSWORD")
host = os.getenv("PG_HOST")
port = os.getenv("PG_PORT")
database = os.getenv("PG_DATABASE")

def get_database_connection() -> bool:
    CONNECTION_STRING = f'postgresql://{user}:{password}@{host}:{port}/{database}'

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
    headers = {
        "Cache-Control": 'no-cache, no-store, must-revalidate;',
        "Pragma": 'no-cache',
        "X-Content-Type-Options": 'nosniff'
    }
    try:
        if get_database_connection():
            return Response(status_code=status.HTTP_200_OK, headers=headers)
    except Exception as e:
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, headers=headers)
    
@app.post("/healthz")
def healthcheck():
    return Response(status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

@app.put("/healthz")
def healthcheck():
    return Response(status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

@app.patch("/healthz")
def healthcheck():
    return Response(status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

@app.delete("/healthz")
def healthcheck():
    return Response(status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

@app.head("/healthz")
def healthcheck():
    return Response(status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

@app.options("/healthz")
def healthcheck():
    return Response(status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
    
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)