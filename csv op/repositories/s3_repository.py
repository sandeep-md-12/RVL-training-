from botocore.exceptions import ClientError
from utils.s3_client import s3_client, BUCKET_NAME, S3_FOLDER, PRESIGNED_URL_EXPIRY


class S3Repository:
    def upload(self, file_bytes: bytes, s3_key: str, content_type: str) -> None:
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=file_bytes,
            ContentType=content_type,
        )

    def generate_presigned_url(self, s3_key: str) -> str:
        print(f"Generating presigned URL for key: {s3_key}")
        return s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET_NAME, "Key": self.build_s3_key(s3_key)},
            ExpiresIn=PRESIGNED_URL_EXPIRY,
        )

    def download(self, s3_key: str) -> tuple[bytes, str]:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=self.build_s3_key(s3_key))
        content_type = response["ContentType"]
        file_bytes = response["Body"].read()
        return file_bytes, content_type

    def file_exists(self, s3_key: str) -> bool:
        try:
            print(f"Checking existence of key: {s3_key}")
            s3_client.head_object(Bucket=BUCKET_NAME, Key=self.build_s3_key(s3_key))
            return True
        except ClientError:
            return False

    def build_s3_key(self, filename: str) -> str:
        return f"{S3_FOLDER}/{filename}"
