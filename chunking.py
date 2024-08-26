import os

def split_file(file_path, chunk_size):
    """Split a large file into smaller chunks."""
    file_size = os.path.getsize(file_path)
    total_chunks = (file_size + chunk_size - 1) // chunk_size  # Calculate total number of chunks

    with open(file_path, 'rb') as f:
        chunk_number = 1
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            chunk_filename = f"{file_path}.part{chunk_number:02}of{total_chunks:02}"
            with open(chunk_filename, 'wb') as chunk_file:
                chunk_file.write(chunk)
            print(f"Created chunk: {chunk_filename}")
            chunk_number += 1
split_file('./dist/qctrader-1.1.6.dev2.tar.gz', chunk_size=100*1024*1024)  # 100 MB chunks