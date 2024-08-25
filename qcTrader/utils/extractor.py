import zipfile
import tarfile
import os
import sys

from qcTrader.utils.logger import setup_logger

def extract_archive(archive_path, extract_to):
    try:
        if archive_path.endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        elif archive_path.endswith(('.tar.gz', '.tgz')):
            with tarfile.open(archive_path, 'r:gz') as tar_ref:
                tar_ref.extractall(extract_to)
        else:
            raise ValueError("Unsupported archive format")
    except (zipfile.BadZipFile, tarfile.TarError, ValueError) as e:
        logger = setup_logger()
        logger.error(f"Failed to extract {archive_path}: {e}")
        sys.exit(1)
