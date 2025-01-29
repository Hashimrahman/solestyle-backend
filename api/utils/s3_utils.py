import boto3
from botocore.exceptions import NoCredentialsError

from decouple import config

# Initialize S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=config("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"),
    region_name=config("AWS_S3_REGION_NAME"),
)


def upload_image_to_s3(image_file, image_name):
    try:
        s3 = boto3.client(
            "s3",
            region_name=config("AWS_S3_REGION_NAME"),
            aws_access_key_id=config("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"),
        )
        # URL encode the image name
        encoded_image_name = image_name

        print(f"Uploading {image_name} to S3...")
        s3.upload_fileobj(
            image_file,
            config("AWS_STORAGE_BUCKET_NAME"),
            encoded_image_name,
            ExtraArgs={"ContentType": image_file.content_type},
        )
        print(f"Upload successful for {image_name}")

        image_url = f"https://{config('AWS_STORAGE_BUCKET_NAME')}.s3.{config('AWS_S3_REGION_NAME')}.amazonaws.com/{image_name}"
        print("url",image_url)
        return image_url
    except NoCredentialsError:
        print("No AWS credentials found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
