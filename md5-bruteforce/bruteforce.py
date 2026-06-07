import hashlib
import time
md5_hash = hashlib.md5("999999".encode()).hexdigest()

def guess_password(hash=md5_hash):
    start_num = 000000
    starting_time = time.time() 
    while start_num <= 999999:
        if hashlib.md5(str(start_num).encode()).hexdigest() == md5_hash:
            time_taken = time.time() - starting_time
            print(f"Time taken: {time_taken} seconds")
            print(f"Password found: {str(start_num)}")
            return str(start_num)
        start_num += 1
guess_password(md5_hash)
