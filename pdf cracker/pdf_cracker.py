import pikepdf
import tqdm
import argparse
import sys
import threading
from queue import Queue
import time

# --- Configuration ---
NUM_THREADS = 20
task_queue = Queue()
password_found_event = threading.Event()
found_password = [None] # Mutable for threads
ENCODING = 'latin-1' # Common for wordlists

def crack_pdf(pdf_file, pbar):
    # Worker function to test passwords
    while not password_found_event.is_set():
        try:
            # Get password from queue
            password = task_queue.get(timeout=0.1)
        except Queue.empty:
            continue # Queue empty

        password = password.strip()
        
        try:
            # Attempt to open PDF
            with pikepdf.open(pdf_file, password=password):
                # Success
                password_found_event.set()
                found_password[0] = password
                
        except pikepdf.PasswordError:
            pass # Wrong password, continue
        except Exception as e:
            # Other errors (e.g., file corrupt)
            print(f"\n[!] Error opening PDF: {e}")
            pass
        finally:
            pbar.update(1) # Update progress bar
            task_queue.task_done()

def main():
    # Setup command-line arguments
    parser = argparse.ArgumentParser(description="Multi-threaded PDF password cracker.")
    parser.add_argument("-p", "--pdf", required=True, help="Path to the protected PDF file.")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to the wordlist file.")
    
    args = parser.parse_args()

    # Get wordlist line count for progress bar
    try:
        with open(args.wordlist, 'r', encoding=ENCODING) as f:
            total_passwords = sum(1 for line in f)
        if total_passwords == 0:
            print("Error: Wordlist is empty.")
            sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Wordlist file not found at '{args.wordlist}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading wordlist: {e}")
        sys.exit(1)

    # Check if PDF is actually encrypted
    try:
        with pikepdf.open(args.pdf) as pdf:
            print("Error: PDF file is not password-protected.")
            sys.exit(1)
    except pikepdf.PasswordError:
        print(f"[+] PDF is encrypted. Starting attack...") # Good, it's protected
    except FileNotFoundError:
        print(f"Error: PDF file not found at '{args.pdf}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error opening PDF: {e}")
        sys.exit(1)

    # Init progress bar
    pbar = tqdm.tqdm(total=total_passwords, desc="Cracking PDF", unit="pass")

    # Start threads
    for _ in range(NUM_THREADS):
        t = threading.Thread(target=crack_pdf, args=(args.pdf, pbar))
        t.daemon = True
        t.start()

    # Load wordlist into queue
    with open(args.wordlist, 'r', encoding=ENCODING) as f:
        for line in f:
            if password_found_event.is_set():
                break # Stop loading
            task_queue.put(line)

    # Wait for queue to finish
    task_queue.join()
    
    # Wait for any lingering threads
    while threading.active_count() > 1 and not password_found_event.is_set():
        time.sleep(0.1)

    pbar.close()

    # Display result
    print("\n--- Results ---")
    if password_found_event.is_set():
        print(f"Success! Password found: {found_password[0]}")
    else:
        print("Failed. Password not found in wordlist.")

if __name__ == "__main__":
    main()