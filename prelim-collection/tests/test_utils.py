import pytest
from unittest.mock import patch, mock_open, MagicMock
import os
import boto3
from app.utils import save_video_locally  # Replace 'your_module' with the actual module name

# Test save_video_locally function
@patch('os.makedirs')
@patch('os.path.exists', return_value=False)  # Simulate directory doesn't exist
@patch('builtins.open', new_callable=mock_open)
@patch('werkzeug.utils.secure_filename', return_value='safe_filename.mp4')
def test_save_video_locally_creates_directory_and_saves_file(mock_secure_filename, mock_open, mock_exists, mock_makedirs):
    mock_file = MagicMock()
    mock_file.filename = 'unsafe_filename.mp4'

    file_path = save_video_locally(mock_file, 1)

    # Ensure directory is created
    mock_makedirs.assert_called_once_with('uploads/question1')

    # Ensure file was saved to correct location
    mock_open.assert_called_once_with('uploads/question1/safe_filename.mp4', 'wb')
    mock_file.save.assert_called_once()

    # Assert the returned file path
    assert file_path == 'uploads/question1/safe_filename.mp4'


@patch('os.path.exists', return_value=True)  # Simulate directory exists
@patch('builtins.open', new_callable=mock_open)
@patch('werkzeug.utils.secure_filename', return_value='safe_filename.mp4')
def test_save_video_locally_saves_to_existing_directory(mock_secure_filename, mock_open, mock_exists):
    mock_file = MagicMock()
    mock_file.filename = 'unsafe_filename.mp4'

    file_path = save_video_locally(mock_file, 1)

    # Ensure directory is not created since it exists
    assert not os.makedirs.called

    # Ensure file was saved to correct location
    mock_open.assert_called_once_with('uploads/question1/safe_filename.mp4', 'wb')
    mock_file.save.assert_called_once()

    # Assert the returned file path
    assert file_path == 'uploads/question1/safe_filename.mp4'


# Test upload_to_s3 function
@patch('boto3.client')
def test_upload_to_s3_success(mock_boto_client):
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3

    file_path = 'uploads/question1/safe_filename.mp4'
    s3_prefix = 'John_Doe_123456'
    question_number = 1
    bucket_name = 'test_bucket'

    # Call the function
    result = upload_to_s3(file_path, s3_prefix, question_number, bucket_name)

    # Ensure upload_file was called with correct parameters
    mock_s3.upload_file.assert_called_once_with(
        file_path,
        bucket_name,
        f"{s3_prefix}/question{question_number}/safe_filename.mp4"
    )

    # Assert the function returned True
    assert result is True


@patch('boto3.client')
def test_upload_to_s3_failure(mock_boto_client):
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3

    # Simulate an exception when calling upload_file
    mock_s3.upload_file.side_effect = Exception('S3 upload failed')

    file_path = 'uploads/question1/safe_filename.mp4'
    s3_prefix = 'John_Doe_123456'
    question_number = 1
    bucket_name = 'test_bucket'

    # Call the function
    result = upload_to_s3(file_path, s3_prefix, question_number, bucket_name)

    # Ensure upload_file was called
    mock_s3.upload_file.assert_called_once()

    # Assert the function returned False due to the exception
    assert result is False