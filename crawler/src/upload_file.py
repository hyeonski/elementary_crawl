import os

from google.cloud import storage


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './google_credentials.json'

def upload_blob_from_bytes(bucket_name:str, data: bytes, destination_blob_name: str):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_string(data, content_type='application/octect-stream')

    print(f'File uploaded to {destination_blob_name}')


def upload_attachment_from_bytes(data: bytes, dest_blob_dir_name: str, dest_blob_name: str):
    """
    Uploads an attachment file to the bucket.
    Returns the public url of the file.
    """
    bucket_name = os.environ['GCS_BUCKET']
    dest_blob_path = os.path.join('attachment', dest_blob_dir_name, dest_blob_name)
    upload_blob_from_bytes(
        bucket_name=bucket_name,
        data=data,
        destination_blob_name=dest_blob_path
    )
    return f'https://storage.googleapis.com/{bucket_name}/{dest_blob_path}'

def upload_image_from_bytes(data: bytes, dest_blob_name: str):
    """
    Uploads an image file to the bucket.
    Returns the public url of the file.
    """
    bucket_name = os.environ['GCS_BUCKET']
    dest_blob_path = os.path.join('image', dest_blob_name)
    upload_blob_from_bytes(
        bucket_name=bucket_name,
        data=data,
        destination_blob_name=dest_blob_path
    )
    return f'https://storage.googleapis.com/{bucket_name}/{dest_blob_path}'
