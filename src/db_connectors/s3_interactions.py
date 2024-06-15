import boto3
import logging
import os

def upload_log_to_s3(log_filename, log_folder, bucket_name):
    s3_client = boto3.client('s3')
    log_filepath = os.path.join(log_folder, log_filename)
    # Write to s3 and remove file locally
    try:
        with open(log_filepath, 'rb') as log_file:
            s3_client.put_object(Bucket=bucket_name, Key=log_filepath, Body=log_file)
        logging.info(f"Uploaded {log_filepath} to S3")
        os.remove(log_filepath)
    except Exception as e:
        logging.info(f"Failed to upload {log_filepath} to S3: {e}")
        
def upload_content_to_s3(content, filename, content_folder, bucket_name):
    s3_client = boto3.client('s3')
    file_path = os.path.join(content_folder, filename)
    try:
      s3_client.put_object(Bucket=bucket_name, Key=file_path, Body=content)
      logging.info(f"Uploaded content to S3 to file {filename}")
    except Exception as e:
      logging.info(f"Failed to upload content to {file_path} to S3: {e}")
