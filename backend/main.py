import qrcode
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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS S3 Configuration
s3 = boto3.client('s3')
bucket_name = "qr-codes-generator"

def create_bucket(bucket_name):
    try:
        # Check if the bucket already exists
        s3.head_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} already exists. Using the existing bucket.")
    except ClientError as e:
        # If a 404 error is thrown, the bucket does not exist
        if e.response['Error']['Code'] == '404':
            try:
                # Create a new bucket
                s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}  # Use your region
                )
                print(f"Bucket {bucket_name} created successfully.")
            except ClientError as create_error:
                print(f"Error creating bucket: {create_error}")
        else:
            print(f"Error accessing bucket: {e}")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for text, email, and URL input
class QRCodeData(BaseModel):
    data_type: str
    data: str

# Call this function when initializing your application
create_bucket(bucket_name)

# Endpoint for generating QR code from text, email, or URL
@app.post("/generate-qr/")
async def generate_qr(data: QRCodeData):
    try:
        # Initialize QR code generation
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data.data)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill='black', back_color='white')
        buf = io.BytesIO()
        img.save(buf, "PNG")  # Save the image in PNG format
        buf.seek(0)
        
        # Convert image to base64
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        
        return JSONResponse(content={"image_data": img_base64}, status_code=200)
    except Exception as e:
        # Log the error and return an appropriate response
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Endpoint for generating QR code from images
@app.post("/generate-qr-image/")
async def generate_qr_image(file: UploadFile):
    try:
        # Check if the uploaded file is an image
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Invalid file type")

        # Read the file contents
        contents = await file.read()

        # Generate a unique file name for the S3 bucket
        file_name = f"uploaded_images/{file.filename}"

        # Upload the image to S3
        s3.put_object(
                Bucket=bucket_name, 
                Key=file_name, 
                Body=contents, 
                ContentType=file.content_type
        )

        # Generate the public URL for the uploaded image
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"

        
        # Generate a QR code for the URL
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(s3_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, "PNG")  
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        return JSONResponse(content={"image_data": img_base64}, status_code=200)
    
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)