from fastapi import FastAPI, Request, Response, HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from models.user import User, Base
from database import get_database_connection, get_database_session, get_engine
import os
import uvicorn
import json
import logging
import bcrypt
import secrets

# the main entrypoint to use FastAPI.
app = FastAPI()

# setting up the logger 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

User.metadata.create_all(bind=get_engine())

security = HTTPBasic()

def authenticate(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_database_session)):
    user_to_authenticate = credentials.username.strip()
    password_to_authenticate = credentials.password.strip()

    user = db.query(User).filter(User.email == user_to_authenticate).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials!",
            headers={'WWW-Authenticate': "Basic"}
        )

    dehashed_password = bcrypt.checkpw(password_to_authenticate.encode('utf-8'), user.password.encode('utf-8'))

    if not dehashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials!",
            headers={'WWW-Authenticate': "Basic"}
        )

    return user.email

class UserRequestBodyModel(BaseModel):
    email: EmailStr
    password: str
    firstname: str
    lastname: str

# setting up the headers
HEADERS = {
        "Cache-Control": 'no-cache, no-store, must-revalidate;',
        "Pragma": 'no-cache',
        "X-Content-Type-Options": 'nosniff'
    }

'''
API Endpoints
'''
@app.get("/healthz")
async def healthcheck(request: Request, response: Response):
    # checks for the scenarios when there's a body or query params in the request
    if await request.body() or request.query_params:
        return Response(status_code=status.HTTP_400_BAD_REQUEST, headers=HEADERS)
    
    # checks if the database connection is up
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
    # checks for the scenarios when the method type is not GET
    return Response(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, headers=HEADERS)

@app.post("/v1/user")
async def create_user(user: UserRequestBodyModel, db: Session = Depends(get_database_session)):

    try:
        if db.query(User).filter(User.email == user.email).first():
            logger.error(f"Database error... User already exists!!")
            return Response(status_code=status.HTTP_400_BAD_REQUEST, headers=HEADERS)
        
        hashed_password = bcrypt.hashpw(password=user.password.encode('utf-8'), salt=bcrypt.gensalt())

        new_user = User(
            email=user.email, 
            password=hashed_password.decode('utf-8'), 
            firstname=user.firstname, 
            lastname=user.lastname
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return_response = {
            "id": new_user.id,
            "firstname": new_user.firstname,
            "lastname": new_user.lastname,
            "email": new_user.email,
            "account_created": str(new_user.account_created),
            "account_updated": str(new_user.account_updated)
        }

        return Response(status_code=status.HTTP_201_CREATED, content=json.dumps(return_response), media_type="application/json")
    except Exception as e:
        logger.error(f"Database error... {e}")
        return Response(status_code=status.HTTP_400_BAD_REQUEST, headers=HEADERS)

@app.get("/v1/user/self", dependencies=[Depends(authenticate)])
async def get_user(request: Request, authenticated_email: str = Depends(authenticate), db: Session = Depends(get_database_session)):
    try:
        if request.headers.get("content-length") is not None or request.headers.get("content-type") is not None:
            return Response(status_code=status.HTTP_400_BAD_REQUEST)
        
        if request.get("body", None) is not None:
            body = await request.json()
        else:
            body = False

        if body:
            return Response(status_code=status.HTTP_400_BAD_REQUEST)

        user = db.query(User).filter(User.email == authenticated_email).first()

        return_response = {
            "id": user.id,
            "first_name": user.firstname,
            "last_name": user.lastname,
            "email": user.email,
            "account_created": str(user.account_created),
            "account_updated": str(user.account_updated)
        }

        return Response(status_code=status.HTTP_200_OK, content=json.dumps(return_response), media_type="application/json")
    except Exception as e:
        print(f"Server error... {e}")
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
        
class UserUpdateRequestBodyModel(BaseModel):
    first_name: str = None
    last_name: str = None
    password: str = None
    email: str = None

@app.put("/v1/user/self", dependencies=[Depends(authenticate)])
async def update_user(user_details: UserUpdateRequestBodyModel, authenticated_email: str = Depends(authenticate),  db: Session = Depends(get_database_session)):
    try:
        user = db.query(User).filter(User.email == authenticated_email).first()

        if authenticated_email != user_details.email:
            return Response(status_code=status.HTTP_400_BAD_REQUEST)

        if not user:
            return Response(status_code=status.HTTP_404_NOT_FOUND, headers=HEADERS)
        
        print(f"{user_details.first_name}, {user_details.last_name}, {user_details.email}, {user_details.password}")

        if user_details.first_name is not None:
            user.firstname = user_details.first_name
        
        if user_details.last_name is not None:
            user.lastname = user_details.last_name
        
        if user_details.password is not None:
            hashed_password = bcrypt.hashpw(password=user_details.password.encode('utf-8'), salt=bcrypt.gensalt())
            user.password = hashed_password.decode('utf-8')

        db.commit()
        db.refresh(user)

        print(user.firstname)

        return Response(status_code=status.HTTP_204_NO_CONTENT, headers=HEADERS)

    except Exception as e:
        logger.info(f"Database error... {e}")
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, headers=HEADERS)

@app.head("/users")
@app.delete("/users")
@app.options("/users")
@app.patch("/users")
def users():
    # checks for the scenarios when the method type is not POST or PUT
    return Response(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, headers=HEADERS)

# Code entrypoint
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)