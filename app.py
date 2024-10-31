from fastapi import FastAPI, Request, Response, HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.exc import OperationalError
from models.user import User, Base, Image
from schemas.user_schema import UserSchema, UserRequestBodyModel, UserUpdateRequestBodyModel
from database import get_database_connection, get_database_session, get_engine, DB_CONNECTION_STRING
import os
import uvicorn
import json
import logging
import bcrypt
import boto3
import uuid
import statsd
import time

session = boto3.Session()

# the main entrypoint to use FastAPI.
app = FastAPI()

# initialize statsd client
statsd_client = statsd.StatsClient('localhost', 8125)

# setting up the logger 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    try:
        engine = get_engine()
        if not database_exists(engine.url):
            create_database(engine.url)
            logger.info('Database created successfully!!')
        
        User.metadata.create_all(bind=get_engine())
        logger.info("Database tables created successfully!!")
    except OperationalError as e:
        logger.error(f"Database connection error during startup: {e}")

'''
Handle events on startup
'''
@app.on_event('startup')
async def startup():
    logger.info("Startup!!")

    try:
        engine = get_engine()
        if not database_exists(engine.url):
            create_database(engine.url)
            logger.info('Database created successfully!!')
        
        User.metadata.create_all(bind=get_engine())
        logger.info("Database tables created successfully!!")
    except OperationalError as e:
        logger.error(f"Database connection error during startup: {e}")

'''
Handle lifespan events like startup and shutdown
  startup: create the database and tables if not created 
  shutdown: do the operations when the server terminates
'''
# issue with below commented code in the droplet, the below block does not get triggered
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     logger.info("Startup!!")

#     try:
#         engine = get_engine()
#         if not database_exists(engine.url):
#             create_database(engine.url)
#             logger.info('Database created successfully!!')
        
#         User.metadata.create_all(bind=get_engine())
#         logger.info("Database tables created successfully!!")
#     except OperationalError as e:
#         logger.error(f"Database connection error during startup: {e}")
    
#     yield

#     logger.info("Shutdown!!")

security = HTTPBasic()

# setting up the headers
HEADERS = {
        "Cache-Control": 'no-cache, no-store, must-revalidate;',
        "Pragma": 'no-cache',
        "X-Content-Type-Options": 'nosniff'
    }

# middleware to track API calls and timing
@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    statsd_client.timing(f'api.{request.url.path}.time', process_time * 1000)
    statsd_client.incr(f'api.{request.url.path}.count')
    return response

# database query timing decorator
def time_database_query(func):
    def wrapper(*args, **kwargs):
        with statsd_client.timer('database.query.time'):
            return func(*args, **kwargs)
    return wrapper

# s3 call timing decorator
def time_s3_call(func):
    def wrapper(*args, **kwargs):
        with statsd_client.timer('aws.s3.call.time'):
            return func(*args, **kwargs)
    return wrapper

"""
Function: authenticate
Descr: This function authenticates the user based on the Basic Auth token passed to the server
params: credentials: HTTPBasicCredentials, db: Session
"""
def authenticate(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_database_session)):
    if not get_database_connection():
        logger.info(f"Database connection error... ")
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, headers=HEADERS)
    
    if not credentials:
        logger.info("Credentials not passed!!!")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    user_to_authenticate = credentials.username.strip()
    password_to_authenticate = credentials.password.strip()

    @time_database_query
    def get_user_from_db(db, user_to_authenticate):
        user = db.query(User).filter(User.email == user_to_authenticate).first()
        return user
    
    user = get_user_from_db(db, user_to_authenticate)

    if not user:
        logger.info("Invalid authentication credentials - email!")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials!",
            headers={'WWW-Authenticate': "Basic"}
        )

    dehashed_password = bcrypt.checkpw(password_to_authenticate.encode('utf-8'), user.password.encode('utf-8'))

    if not dehashed_password:
        logger.info("Invalud authentication credentials!")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials!",
            headers={'WWW-Authenticate': "Basic"}
        )

    return user.email

'''
API Endpoints
'''

"""
GET: /heatlhz
Healthcheck endpoint
"""
@app.get("/healthz")
async def healthcheck(request: Request, response: Response):
    # checks for the scenarios when there's a body or query params in the request
    if await request.body() or request.query_params:
        return Response(status_code=status.HTTP_400_BAD_REQUEST, headers=HEADERS)
    
    # checks if the database connection is up
    if not get_database_connection():
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, headers=HEADERS)
    
    return Response(status_code=status.HTTP_200_OK, headers=HEADERS)

"""
/healthz
POST, PUT, PATCH, DELETE, HEAD, OPTIONS 
Healthcheck 405: Method Not Allowed
"""
@app.post("/healthz")
@app.put("/healthz")
@app.patch("/healthz")
@app.delete("/healthz")
@app.head("/healthz")
@app.options("/healthz")
def healthcheck():
    # checks for the scenarios when the method type is not GET
    return Response(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, headers=HEADERS)

"""
POST: /v2/user
Create a user
"""
@app.post("/v2/user", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(request: Request, user: UserRequestBodyModel, db: Session = Depends(get_database_session)):

    if request.query_params:
        logger.info("query params not allowed...")
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    try:
        if not get_database_connection():
            return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, headers=HEADERS)

        if db.query(User).filter(User.email == user.email).first():
            logger.error(f"Database error... User already exists!!")
            return Response(status_code=status.HTTP_400_BAD_REQUEST, headers=HEADERS)
        
        hashed_password = bcrypt.hashpw(password=user.password.encode('utf-8'), salt=bcrypt.gensalt())

        new_user = User(
            email=user.email.strip(), 
            password=hashed_password.decode('utf-8'), 
            first_name=user.first_name.strip(), 
            last_name=user.last_name.strip()
        )
        
        @time_database_query
        def create_user_in_db(db, new_user): 
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
        
        create_user_in_db(db, new_user)

        return new_user
    except Exception as e:
        logger.error(f"Database error... {e}")
        return Response(status_code=status.HTTP_400_BAD_REQUEST, headers=HEADERS)

"""
GET /v1/user/self
Get User based on authentication
"""
@app.get("/v2/user/self", dependencies=[Depends(authenticate)], response_model=UserSchema)
async def get_user(request: Request, authenticated_email: str = Depends(authenticate), db: Session = Depends(get_database_session)):
    try:
        if not get_database_connection():
            return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, headers=HEADERS)
        
        if request.query_params:
            logger.info("query params not allowed...")
            return Response(status_code=status.HTTP_400_BAD_REQUEST)

        if request.headers.get("content-length") is not None or request.headers.get("content-type") is not None:
            logger.info("request body is not allowed...")
            return Response(status_code=status.HTTP_400_BAD_REQUEST)
        
        if request.get("body", None) is not None:
            body = await request.json()
        else:
            body = False

        if body:
            return Response(status_code=status.HTTP_400_BAD_REQUEST)

        @time_database_query
        def get_user_from_db(db, authenticated_email):
            user = db.query(User).filter(User.email == authenticated_email).first()
            return user

        user = get_user_from_db(db, authenticated_email)

        return user
    except Exception as e:
        print(f"Server error... {e}")
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

"""
PUT: /v2/user/self
Update user based on authentication
"""
@app.put("/v2/user/self", dependencies=[Depends(authenticate)])
async def update_user(request: Request, user_details: UserUpdateRequestBodyModel, authenticated_email: str = Depends(authenticate),  db: Session = Depends(get_database_session)):

    if request.query_params:
        logger.info("query params not allowed...")
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    try:
        @time_database_query
        def get_user_from_db(db, authenticated_email):
            user = db.query(User).filter(User.email == authenticated_email).first()
            return user

        user = get_user_from_db(db, authenticated_email)

        if authenticated_email != user_details.email:
            logger.info("Updates to email are not allowed...")
            return Response(status_code=status.HTTP_400_BAD_REQUEST)

        if not user:
            logger.info("User not found...")
            return Response(status_code=status.HTTP_404_NOT_FOUND, headers=HEADERS)

        if user_details.first_name is not None:
            user.first_name = user_details.first_name
            logger.info("Updated the first name...")
        
        if user_details.last_name is not None:
            user.last_name = user_details.last_name
            logger.info("Updated the last name...")
        
        if user_details.password is not None:
            hashed_password = bcrypt.hashpw(password=user_details.password.encode('utf-8'), salt=bcrypt.gensalt())
            user.password = hashed_password.decode('utf-8')
            logger.info("Updated the password...")

        @time_database_query
        def update_user_in_db(db, user):
            db.commit()
            db.refresh(user)
        
        update_user_in_db(db, user)

        return Response(status_code=status.HTTP_204_NO_CONTENT, headers=HEADERS)

    except Exception as e:
        logger.info(f"Database error... {e}")
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, headers=HEADERS)

"""
HEAD, DELETE, OPTIONS, PATCH: 405 method not allowed
"""
@app.head("/v2/user/self")
@app.delete("/v2/user/self")
@app.options("/v2/user/self")
@app.patch("/v2/user/self")
def users():
    # checks for the scenarios when the method type is not POST or PUT
    return Response(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, headers=HEADERS)

###########################################################
################# Image upload routes #####################
###########################################################
"""
POST: /v2/user/self/pic
Update user based on authentication
"""
@app.post("/v2/user/self/pic", dependencies=[Depends(authenticate)])
async def upload_profile_pic(
    request: Request,
    authenticated_email: str = Depends(authenticate),
    db: Session = Depends(get_database_session)
):
    # Read binary data from the request body
    body = await request.body()

    try:
        user = db.query(User).filter(User.email == authenticated_email).first()

        existing_image = db.query(Image).filter(Image.user_id == user.id).first()

        if existing_image:
            return Response(status_code=status.HTTP_400_BAD_REQUEST, content=json.dumps({'message': 'User already has a profile picture. Delete the existing image before uploading a new one.'}))

    except Exception as e:
        logger.info(f"Database error... {e}")
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, headers=HEADERS)


    # print("DEBUG body: ", type(body), body)
    # as the body is of type binary bytes we cannot see the filename as metadata
    # but we can do that with the help of UploadFile class where we upload from Postman
    # as form-data
    
    # Validate content type (assuming it's sent as a header)
    content_type = request.headers.get('Content-Type')
    if content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG, JPG, and PNG are allowed.")

    # Generate a unique filename
    file_extension = content_type.split("/")[-1]
    unique_filename = f"profile-pic-{uuid.uuid4()}.{file_extension}"

    # generate a key - create a folder by the userid-firstname/filename
    s3_file_key = f'{user.id}-{user.first_name}-{user.last_name}/{unique_filename}'

    print(file_extension)
    print(content_type.split("/"))

    # upload to s3 bucket
    s3 = session.client("s3")
    bucket_name = os.getenv("APP_S3_BUCKET_NAME")

    try:
        s3_response = s3.put_object(Bucket=bucket_name, Key=s3_file_key, Body=body, ContentType=content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload the file to S3 bucket: {str(e)}")
    
    image_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_file_key}"
    try:

        new_image = Image(
            id = str(uuid.uuid4()),
            file_name = s3_file_key,
            url = image_url,
            user_id = user.id
        )

        db.add(new_image)
        db.commit()

        return {
            "file_name": unique_filename,
            "id": new_image.id,
            "url": image_url,
            "upload_date": new_image.upload_date,
            "user_id": user.id
        }

    except Exception as e:
        logger.info(f"Database error... {e}")
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, headers=HEADERS)

"""
GET: /v2/user/self/pic
Get user's image 
"""
@app.get("/v2/user/self/pic", dependencies=[Depends(authenticate)])
async def upload_profile_pic(
    authenticated_email: str = Depends(authenticate),
    db: Session = Depends(get_database_session)
):
    try:
        user = db.query(User).filter(User.email == authenticated_email).first()

        image = db.query(Image).filter(Image.user_id == user.id).first()

        if not image:
            raise HTTPException(status_code=404, detail="Profile Image not found!")
    
        return {
            "file_name": image.file_name,
            "id": image.id,
            "url": image.url,
            "upload_date": image.upload_date,
            "user_id": image.user_id
        }
    except HTTPException as he:
        logger.info(f"Image not found: {he}")
        return Response(status_code=status.HTTP_404_NOT_FOUND, headers=HEADERS)
    except Exception as e:
        logger.info(f"Database error... {e}")
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, headers=HEADERS)

"""
DELETE: /v2/user/self/pic
Delete user's image 
"""
@app.delete("/v2/user/self/pic", dependencies=[Depends(authenticate)], status_code=204)
async def upload_profile_pic(
    authenticated_email: str = Depends(authenticate),
    db: Session = Depends(get_database_session)
): 
    try:
        user = db.query(User).filter(User.email == authenticated_email).first()

        image = db.query(Image).filter(Image.user_id == user.id).first()

        if not image:
            raise HTTPException(status_code=404, detail="Image not found!")

        # delete the image from the S3 bucket
        s3 = session.client('s3')
        bucket_name = os.getenv("APP_S3_BUCKET_NAME")

        try:
            logger.info(f"Image to be deleted: {image.file_name}")
            s3.delete_object(Bucket=bucket_name, Key=image.file_name)
            logger.info("Image deletion from S3 is successful..")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete from the S3 bucket: {str(e)}")
        
        db.delete(image)
        logger.info("Image deletion from DB is successful..")
        db.commit()

    except HTTPException as he:
        if he.status_code == 404:
            print(f"Image not found error... {he}")
            return Response(status_code=status.HTTP_404_NOT_FOUND, headers=HEADERS)
        elif he.status_code == 500:
            logger.info(f"Failed to delete from the S3 bucket: {str(he)}")
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, headers=HEADERS)
    except Exception as e:
        logger.info(f"Server: unexpected error!!: {e}")
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, headers=HEADERS)
"""
Methods not allowed for uploading image
HEAD, PUT, OPTIONS, PATCH: 405 method not allowed
"""
@app.head("/v2/user/self/pic")
@app.put("/v2/user/self/pic")
@app.options("/v2/user/self/pic")
@app.patch("/v2/user/self/pic")
def users():
    return Response(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, headers=HEADERS)

# Code entrypoint
if __name__ == "__main__":
    init_database()
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)