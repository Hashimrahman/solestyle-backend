from django.test import TestCase

# Create your tests here.
import boto3
from decouple import config

# Replace these with your actual credentials
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_BUCKET_NAME = 'solestylebucket'
AWS_REGION_NAME = 'ap-south-1'

# Initialize the S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION_NAME
)

# Test upload to the bucket
try:
    # Path to a local file for testing
    test_file = "test1.txt"
    with open(test_file, "w") as f:
        f.write("This is a test file for S3 connection testing.")

    # Upload the file to S3
    s3.upload_file(test_file, AWS_BUCKET_NAME, "test-folder/test1.txt")
    print("File uploaded successfully!")

except Exception as e:
    print(f"Error uploading file: {e}")
