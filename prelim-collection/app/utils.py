import os
import uuid
import boto3
import json
from werkzeug.utils import secure_filename
from typing import Dict
import logging

S3_BUCKET = 'dpfkresponses'  # Replace with your S3 bucket name
S3_REGION = 'us-east-2'       # e.g., 'us-east-1'

# Function to save the uploaded video locally
def save_video_locally(file, question_number):
    save_path = f'uploads/question{question_number}'
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # Secure the file name and save it locally
    filename = secure_filename(file.filename)
    file_path = os.path.join(save_path, filename)
    file.save(file_path)

    return file_path

# Function to upload the file to S3 under a specific user's "directory"
def upload_demo_to_s3(data: Dict[str, str], folder_name):

    s3_client = boto3.client('s3', region_name=S3_REGION)

    demographic_json = json.dumps(data)
    # Create a unique filename
    filename = 'demographics.json'

    # Upload the demographic data to S3
    s3_key = f"{folder_name}/{filename}"

    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=s3_key,
        Body=demographic_json,
        ContentType='application/json'
    )

    logging.info(f"Uploaded demographics data to s3://{S3_BUCKET}/{s3_key}")


def check_folder_exists(folder_name):
    s3_client = boto3.client('s3', region_name=S3_REGION)

    response = s3_client.list_objects_v2(
        Bucket=S3_BUCKET,
        Prefix=f"{folder_name}/",
        MaxKeys=1
    )
    # Check if 'Contents' key is in the response
    if 'Contents' in response:
        return True
    else:
        return False


def generate_unique_folder_name(first_name, last_name, max_attempts=10):
    for attempt in range(max_attempts):
        # Generate a random UUID
        random_id = str(uuid.uuid4())
        # Limit first and last names to the first 10 letters
        if len(first_name) > 10:
            first_name_part = first_name[:10]
        else: 
            first_name_part = first_name
        
        if len(last_name) > 10:
            last_name_part = last_name[:10]
        else:
            last_name_part = last_name
        # Concatenate the random ID and name parts
        folder_name = f"{random_id}_{first_name_part}{last_name_part}"
        # Check if folder exists
        if not check_folder_exists(folder_name):
            return folder_name
        else:
            logging.warning(f"Folder name collision detected: {folder_name}. Retrying...")
    # If we reach here, it means all attempts failed
    raise Exception(f"Failed to generate a unique folder name after {max_attempts} attempts.")


def upload_video_to_s3(video_file, folder_name, question_number):
    """
    Uploads a video file to S3 under the specified folder and question number.

    :param video_file: File object representing the video file.
    :param folder_name: String representing the participant's folder name.
    :param question_number: Integer or string representing the question number.
    :return: True if upload is successful, False otherwise.
    """
    s3_client = boto3.client('s3', region_name=S3_REGION)

    try:
        # Read the video file content
        video_content = video_file.read()

        # Create a unique filename for the video
        filename = secure_filename(f'question_{question_number}_recording.webm')

        # Construct the S3 key (path)
        s3_key = f"{folder_name}/{filename}"

        # Upload the video to S3
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=video_content,
            ContentType='video/webm'
        )
        logging.info(f"Uploaded video to s3://{S3_BUCKET}/{s3_key}")
        return True
    except Exception as e:
        logging.error(f"Error uploading video to S3: {e}", exc_info=True)
        return False