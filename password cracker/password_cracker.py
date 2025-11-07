import hashlib
import threading
import argparse
import sys
from queue import Queue
import time

# --- Configuration ---
NUM_THREADS = 50
task_queue = Queue()
password_found_event = threading.Event()
found_password = [None] # Use list for mutable-in-thread
print_lock = threading.Lock()
ENCODING = 'latin-1' # Common for wordlists

def crack_password(target_hash, hash_type):
    # Worker function to crack hashes
    while not password_found_event.is_set():
        try:
            # Get word from queue
            word = task_queue.get(timeout=0.1)
        except Queue.empty:
            continue # Queue empty

        # Clean word
        word = word.strip()
        
        # Hash word
        hash_obj = hashlib.new(hash_type)
        hash_obj.update(word.encode(ENCODING))
        hashed_word = hash_obj.hexdigest()

        # Compare hashes
        if hashed_word == target_hash:
            # Password found
            password_found_event.set()
            found_password[0] = word
        
        task_queue.task_done()

def main():
    # Setup command-line arguments
    parser = argparse.ArgumentParser(description="Multi-threaded hash cracker.")
    parser.add_argument("-H", "--hash", required=True, help="The target hash to crack.")
    parser.add_argument("-t", "--type", required=True, help="Hash algorithm (e.g., md5, sha256).")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to the wordlist file.")
    
    args = parser.parse_args()

    # Validate hash algorithm
    if args.type not in hashlib.algorithms_available:
        print(f"Error: Hash type '{args.type}' is not available.")
        print(f"Available types: {hashlib.algorithms_available}")
        sys.exit(1)

    print(f"[+] Cracking hash: {args.hash} ({args.type})")
    print(f"[+] Using wordlist: {args.wordlist}")
    start_time = time.time()

    # Start threads
    for _ in range(NUM_THREADS):
        t = threading.Thread(target=crack_password, args=(args.hash, args.type))
        t.daemon = True
        t.start()

    # Load wordlist into queue
    try:
        with open(args.wordlist, 'r', encoding=ENCODING) as f:
            for line in f:
                if password_found_event.is_set():
                    break # Stop loading if found
                task_queue.put(line)
    except FileNotFoundError:
        print(f"Error: Wordlist file not found at '{args.wordlist}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading wordlist: {e}")
        sys.exit(1)

    # Wait for queue to finish
    task_queue.join()
    
    # Wait for any lingering threads
    while threading.active_count() > 1 and not password_found_event.is_set():
        time.sleep(0.1)

    end_time = time.time()

    # Display result
    print("\n--- Results ---")
    if password_found_event.is_set():
        print(f"Success! Password found: {found_password[0]}")
    else:
        print("Failed. Password not found in wordlist.")
    
    print(f"Time taken: {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()