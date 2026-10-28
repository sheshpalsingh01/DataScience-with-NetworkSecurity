import os
from pathlib import Path
from urllib.parse import urlparse

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from networksecurity.logging.logger import logger


class S3Sync:
    def __init__(self):
        endpoint_url = (
            os.getenv("FLOCI_S3_ENDPOINT_URL")
            or os.getenv("AWS_ENDPOINT_URL_S3")
            or os.getenv("AWS_ENDPOINT_URL")
        )
        client_options = {
            "region_name": os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
            "config": Config(
                s3={"addressing_style": "path"} if endpoint_url else {}
            ),
        }
        if endpoint_url:
            client_options["endpoint_url"] = endpoint_url
            client_options["aws_access_key_id"] = os.getenv("AWS_ACCESS_KEY_ID", "test")
            client_options["aws_secret_access_key"] = os.getenv(
                "AWS_SECRET_ACCESS_KEY", "test"
            )

        self.s3_client = boto3.client("s3", **client_options)

    def _ensure_bucket_exists(self, bucket_name: str) -> None:
        try:
            self.s3_client.head_bucket(Bucket=bucket_name)
        except ClientError as error:
            status_code = error.response.get("ResponseMetadata", {}).get(
                "HTTPStatusCode"
            )
            error_code = error.response.get("Error", {}).get("Code")
            if status_code != 404 and error_code not in {
                "404",
                "NoSuchBucket",
                "NotFound",
            }:
                raise

            create_options = {"Bucket": bucket_name}
            region = self.s3_client.meta.region_name
            if region != "us-east-1":
                create_options["CreateBucketConfiguration"] = {
                    "LocationConstraint": region
                }
            self.s3_client.create_bucket(**create_options)
            logger.info("Created S3 bucket %s", bucket_name)

    def sync_folder_to_s3(self, folder: str, aws_bucket_url: str) -> None:
        source_dir = Path(folder)
        if not source_dir.is_dir():
            raise FileNotFoundError(f"S3 sync source directory does not exist: {folder}")

        destination = urlparse(aws_bucket_url)
        if destination.scheme != "s3" or not destination.netloc:
            raise ValueError(f"Expected an S3 URL, got: {aws_bucket_url}")

        files = sorted(path for path in source_dir.rglob("*") if path.is_file())
        if not files:
            raise ValueError(f"S3 sync source directory contains no files: {folder}")

        bucket_name = destination.netloc
        prefix = destination.path.strip("/")
        self._ensure_bucket_exists(bucket_name)

        for file_path in files:
            relative_path = file_path.relative_to(source_dir).as_posix()
            object_key = "/".join(
                part for part in (prefix, relative_path) if part
            )
            self.s3_client.upload_file(str(file_path), bucket_name, object_key)

        logger.info(
            "Uploaded %d files from %s to %s",
            len(files),
            source_dir,
            aws_bucket_url,
        )

    def download_file(self, bucket_name: str, object_key: str, destination: str) -> None:
        destination_path = Path(destination)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        self.s3_client.download_file(
            bucket_name,
            object_key,
            str(destination_path),
        )
        logger.info(
            "Downloaded s3://%s/%s to %s",
            bucket_name,
            object_key,
            destination_path,
        )
