import requests
from tqdm import tqdm
import sys

from qcTrader.utils.logger import setup_logger

def download_file(url, dest_path):
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        with open(dest_path, 'wb') as file, tqdm(
            desc=dest_path,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    bar.update(len(chunk))
    except requests.RequestException as e:
        logger = setup_logger()
        logger.error(f"Failed to download {url}: {e}")
        sys.exit(1)
