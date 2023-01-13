from dotenv import load_dotenv
import boto3
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
    <summary> Uploads a given file to aws s3 from memory</summary>
    <param name="file_upload">The file to upload</param>
    <param name="filename">The name of the uploaded file on aws</param>
    <param name="bucket_name">The name of the bucket to upload the file to</param>
    <returns></returns>
    """
    def upload_csv(self, file_upload, filename, bucket_name):
        self.s3_client.put_object(
                Bucket = bucket_name,
                Key = filename,
                Body = file_upload
            )

    """
    <summary> Deletes a given file in AWS S3 </summary>
    <param name="filename">The name of the file to delete on aws</param>
    <param name="bucket_name">The name of the bucket to delete the file from</param>
    <returns></returns>
    """
    def delete_file(self, filename, bucket_name): 
        self.s3_client.delete_object(Bucket=bucket_name, Key=filename)