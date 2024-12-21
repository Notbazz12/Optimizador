import os
import hashlib
import shutil

def analyze_storage():
    total, used, free = shutil.disk_usage("/")
    return {
        'total': total // (2**30),  # Convert bytes to GB
        'used': used // (2**30),
        'free': free // (2**30)
    }

def find_large_files(directory, size_threshold_mb=100):
    size_threshold_bytes = size_threshold_mb * 1024 * 1024
    for root, _, files in os.walk(directory):
        for file in files:
            try:
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                if file_size > size_threshold_bytes:
                    yield file_path, file_size / (1024 * 1024)
            except OSError:
                continue

def hash_file(file_path, chunk_size=4096):
    hasher = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
    except OSError:
        return None
    return hasher.hexdigest()

def find_duplicate_files(directory):
    files_by_size = {}
    for root, _, files in os.walk(directory):
        for file in files:
            try:
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                if file_size in files_by_size:
                    files_by_size[file_size].append(file_path)
                else:
                    files_by_size[file_size] = [file_path]
            except OSError:
                continue

    duplicates = []
    for file_list in files_by_size.values():
        if len(file_list) < 2:
            continue
        hashes = {}
        for file_path in file_list:
            file_hash = hash_file(file_path)
            if file_hash:
                if file_hash in hashes:
                    duplicates.append((hashes[file_hash], file_path))
                else:
                    hashes[file_hash] = file_path
    return duplicates