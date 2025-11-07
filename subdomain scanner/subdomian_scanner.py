import requests
import threading
import sys
import argparse
from queue import Queue
import time

# --- Configuration ---
NUM_THREADS = 50
http_queue = Queue()
write_lock = threading.Lock()
discovered_subdomains = []
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

def check_subdomain(domain):
    # Worker function
    while not http_queue.empty():
        try:
            subdomain = http_queue.get(timeout=0.1)
        except Queue.empty:
            continue

        # Construct URL [cite: 199, 200]
        url = f"http://{subdomain}.{domain}"
        
        try:
            # Make request [cite: 199]
            requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=3)
        except requests.ConnectionError:
            pass # Connection failed, subdomain likely inactive
        else:
            # Connection successful [cite: 201]
            print(f"[+] Discovered: {url}")
            with write_lock:
                discovered_subdomains.append(url)
        finally:
            http_queue.task_done()

def main():
    # Setup command-line arguments
    parser = argparse.ArgumentParser(description="Multi-threaded subdomain enumerator.")
    parser.add_argument("-d", "--domain", required=True, help="The target domain (e.g., google.com).")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to the subdomain wordlist.")
    parser.add_argument("-o", "--output", help="Optional output file to save results.")
    
    args = parser.parse_args()
    
    print(f"[+] Starting scan on: {args.domain}")
    start_time = time.time()

    # Start threads [cite: 211]
    for _ in range(NUM_THREADS):
        t = threading.Thread(target=check_subdomain, args=(args.domain,))
        t.daemon = True
        t.start()

    # Load wordlist into queue [cite: 209]
    try:
        with open(args.wordlist, 'r') as f:
            for line in f:
                http_queue.put(line.strip())
    except FileNotFoundError:
        print(f"Error: Wordlist file not found at '{args.wordlist}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading wordlist: {e}")
        sys.exit(1)

    # Wait for queue to finish
    http_queue.join()
    
    end_time = time.time()

    # Save results to file [cite: 202, 212]
    if args.output:
        with write_lock: # Ensure threads are done writing [cite: 203]
            with open(args.output, 'w') as f:
                for url in discovered_subdomains:
                    f.write(url + "\n")
        print(f"\n[+] Results saved to: {args.output}")

    print(f"\nScan complete. Time taken: {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()