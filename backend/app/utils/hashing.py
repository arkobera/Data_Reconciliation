import hashlib

def hash_record(row, keys):
    record_str = "|".join(str(row.get(key)) for key in keys)
    return hashlib.md5(record_str.encode()).hexdigest()
