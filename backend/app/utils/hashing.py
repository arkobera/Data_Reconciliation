import hashlib

def hash_record(row):
    record_str = f"{row['amount']}_{row.get('txn_date', row.get('settle_date'))}"
    return hashlib.md5(record_str.encode()).hexdigest()