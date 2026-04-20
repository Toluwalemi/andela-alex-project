from pathlib import Path

from google.cloud import storage

from app.core.config import settings


class StorageService:
    def store_upload(self, filename: str, content: bytes) -> str:
        safe_name = filename.replace("/", "_")
        if settings.gcs_bucket_name:
            client = storage.Client()
            bucket = client.bucket(settings.gcs_bucket_name)
            blob = bucket.blob(f"uploads/{safe_name}")
            blob.upload_from_string(content, content_type="text/csv")
            return f"gs://{settings.gcs_bucket_name}/{blob.name}"

        local_uploads = Path("uploads")
        local_uploads.mkdir(exist_ok=True)
        destination = local_uploads / safe_name
        destination.write_bytes(content)
        return str(destination)


storage_service = StorageService()
