import io
import uuid
import os
from typing import BinaryIO, Optional
from datetime import timedelta
from minio import Minio
from minio.error import S3Error
from app.config import (
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_SECURE,
    MINIO_BUCKET_NAME,
)

class MinioClientWrapper:
    """Wrapper para gestionar la conexión y operaciones con MinIO S3."""

    def __init__(self):
        self.endpoint = MINIO_ENDPOINT
        self.secure = MINIO_SECURE
        self.default_bucket = MINIO_BUCKET_NAME
        self.client = Minio(
            endpoint=self.endpoint,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=self.secure,
        )

    def ensure_bucket_exists(self, bucket_name: Optional[str] = None) -> None:
        """Asegura que el bucket especificado exista, o lo crea si no existe."""
        target_bucket = bucket_name or self.default_bucket
        try:
            if not self.client.bucket_exists(target_bucket):
                self.client.make_bucket(target_bucket)
        except S3Error as err:
            raise RuntimeError(f"Error al verificar/crear bucket '{target_bucket}' en MinIO: {err}")

    def upload_file(
        self,
        file_data: bytes | BinaryIO,
        object_name: str,
        content_type: str = "image/jpeg",
        bucket_name: Optional[str] = None,
    ) -> str:
        """
        Sube un archivo a MinIO y retorna su URL accesible.
        Acepta datos en bytes o un stream binario.
        """
        target_bucket = bucket_name or self.default_bucket
        self.ensure_bucket_exists(target_bucket)

        if isinstance(file_data, bytes):
            stream = io.BytesIO(file_data)
            length = len(file_data)
        else:
            # Si es un stream de archivo (UploadFile.file)
            file_data.seek(0, os.SEEK_END)
            length = file_data.tell()
            file_data.seek(0)
            stream = file_data

        self.client.put_object(
            bucket_name=target_bucket,
            object_name=object_name,
            data=stream,
            length=length,
            content_type=content_type,
        )

        return self.get_object_url(object_name, bucket_name=target_bucket)

    def get_object_url(self, object_name: str, bucket_name: Optional[str] = None) -> str:
        """Construye la URL directa del objeto almacenado."""
        target_bucket = bucket_name or self.default_bucket
        protocol = "https" if self.secure else "http"
        return f"{protocol}://{self.endpoint}/{target_bucket}/{object_name}"

    def get_presigned_url(
        self,
        object_name: str,
        bucket_name: Optional[str] = None,
        expires: timedelta = timedelta(hours=24),
    ) -> str:
        """Genera una URL prefirmada temporal para visualización segura."""
        target_bucket = bucket_name or self.default_bucket
        return self.client.presigned_get_object(
            bucket_name=target_bucket,
            object_name=object_name,
            expires=expires,
        )

# Instancia global (singleton para inyección de dependencias)
minio_service = MinioClientWrapper()

def get_minio_client() -> MinioClientWrapper:
    """Dependencia de FastAPI para inyectar el cliente MinIO."""
    return minio_service
