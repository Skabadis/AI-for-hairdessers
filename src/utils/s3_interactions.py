import boto3
import logging

def upload_log_to_s3(log_filename, bucket_name='aiforcardealers'):
    s3_client = boto3.client('s3')
    try:
        with open(log_filename, 'rb') as log_file:
            s3_client.put_object(Bucket=bucket_name, Key=log_filename, Body=log_file)
        logging.info(f"Uploaded {log_filename} to S3")
    except Exception as e:
        logging.info(f"Failed to upload {log_filename} to S3: {e}")