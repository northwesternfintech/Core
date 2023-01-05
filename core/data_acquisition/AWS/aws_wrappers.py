from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError
import os

"""
Controller for uploading files to and deleting files from AWS
"""
class AWSController:

    def __init__(self):
        load_dotenv()
        aws_access_key = str(os.getenv("AWS_ACCESS_KEY_ID"))
        aws_secret_key = str(os.getenv("AWS_SECRET_ACCESS_KEY"))
        aws_bucket_region = str(os.getenv("AWS_BUCKET_REGION"))

        self.s3_client = boto3.client("s3", 
                region_name=aws_bucket_region, 
                aws_access_key_id=aws_access_key, 
                aws_secret_access_key=aws_secret_key)

    """
    <summary>Uploads a given file-like object to AWS S3 from memory</summary>
    <param name="file_obj">The file-like object to upload (must be in binary mode)</param>
    <param name="bucket_name">The name of the bucket to upload the file to</param>
    <param name="AWS_key">The name of the key to upload to on AWS</param>
    <returns>True if file was uploaded, else False</returns>
    """
    def upload_file_from_memory(self, file_obj, bucket_name, AWS_key):
        try:
            self.s3_client.upload_fileobj(
                file_obj,
                bucket_name,
                AWS_key
            )
        except ClientError:
            return False
        return True


    """
    <summary>Uploads a given file to AWS S3 from the disk</summary>
    <param name="filepath">The path of the file to upload</param>
    <param name="bucket_name">The name of the bucket to upload the file to</param>
    <param name="AWS_key">The name of the key to upload to on AWS</param>
    <returns>True if file was uploaded, else False</returns>
    """
    def upload_file_from_disk(self, filepath, bucket_name, AWS_key):
        try:
            self.s3_client.upload_file(
                filepath,
                bucket_name,
                AWS_key
            )
        except ClientError:
            return False
        return True

    """
    <summary> Deletes a given file in AWS S3 </summary>
    <param name="filename">The name of the file to delete on aws</param>
    <param name="bucket_name">The name of the bucket to delete the file from</param>
    <returns></returns>
    """
    def delete_file(self, filename, bucket_name): 
        self.s3_client.delete_object(Bucket=bucket_name, Key=filename)