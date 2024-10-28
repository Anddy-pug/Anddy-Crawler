import hashlib

def compute_checksum(file_path, algorithm='md5'):
    hash_func = getattr(hashlib, algorithm)()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()

checksum = compute_checksum(r'D:\PUG\1.jpg')
print(f'SHA-256 checksum: {checksum}')
