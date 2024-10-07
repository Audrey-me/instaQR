import uvicorn
import io
import os
import base64
import logging
import boto3
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, Form, HTTPException
from botocore.exceptions import NoCredentialsError, ClientError
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS S3 Configuration
s3 = boto3.client('s3')
bucket_name = "qr-codes-generator"

def create_bucket(bucket_name):
    try:
        s3.head_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} already exists. Using the existing bucket.")
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            try:
                s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
                )
                print(f"Bucket {bucket_name} created successfully.")
            except ClientError as create_error:
                print(f"Error creating bucket: {create_error}")
        else:
            print(f"Error accessing bucket: {e}")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Prometheus metrics initialization (directly in the app initialization)
instrumentator = Instrumentator().instrument(app).expose(app, endpoint="/metrics")


# Call this function when initializing your application
create_bucket(bucket_name)

# Use the instrumentator to track metrics
@app.on_event("startup")
async def startup():
    # Optional: log to confirm initialization
    logger.info("Application has started")
    
# Pydantic model for text, email, and URL input
class QRCodeData(BaseModel):
    data_type: str
    data: str

# Endpoint for generating QR code from text, email, or URL
@app.post("/generate-qr/")
async def generate_qr(data: QRCodeData):
    try:
        # QR code generation logic here...

        return JSONResponse(content={"image_data": img_base64}, status_code=200)
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Endpoint for generating QR code from images
@app.post("/generate-qr-image/")
async def generate_qr_image(file: UploadFile):
    try:
        # Image processing logic here...

        return JSONResponse(content={"image_data": img_base64}, status_code=200)
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

