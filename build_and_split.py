import subprocess
import os
import sys

def build_package():
    """Build the source distribution and wheel."""
    subprocess.check_call([sys.executable, 'setup.py', 'sdist', 'bdist_wheel'])

def split_file(file_path, chunk_size):
    """Split a large file into smaller chunks."""
    with open(file_path, 'rb') as f:
        chunk_number = 0
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            chunk_filename = f"{file_path}.part{chunk_number:03}"
            with open(chunk_filename, 'wb') as chunk_file:
                chunk_file.write(chunk)
            chunk_number += 1

def clean_build_artifacts():
    """Clean up the build artifacts before rebuilding."""
    if os.path.exists('build'):
        subprocess.check_call(['rmdir', '/S', '/Q', 'build'], shell=True)
    if os.path.exists('dist'):
        subprocess.check_call(['rmdir', '/S', '/Q', 'dist'], shell=True)
    for egg_info in os.listdir('.'):
        if egg_info.endswith('.egg-info'):
            subprocess.check_call(['rmdir', '/S', '/Q', egg_info], shell=True)

def main():
    """Main function to clean, build, and split the package."""
    clean_build_artifacts()
    build_package()

    # Locate the generated tar.gz file
    dist_dir = 'dist'
    chunk_size = 100 * 1024 * 1024  # 100 MB
    for filename in os.listdir(dist_dir):
        if filename.endswith('.tar.gz'):
            tar_file = os.path.join(dist_dir, filename)
            # Split the tar.gz file into smaller chunks
            split_file(tar_file, chunk_size)

if __name__ == '__main__':
    main()
