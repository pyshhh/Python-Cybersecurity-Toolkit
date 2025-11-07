import socket
import sys
import threading
from queue import Queue
from datetime import datetime

# --- Configuration ---
NUM_THREADS = 100
print_lock = threading.Lock()
port_queue = Queue()
open_ports = []

def get_service_banner(s):
    # Try to grab a service banner
    try:
        s.settimeout(0.5) # Short timeout
        banner = s.recv(1024).decode().strip()
        return banner if banner else "N/A"
    except (socket.timeout, ConnectionResetError, UnicodeDecodeError):
        return "N/A" # No banner received

def scan_port(target_ip):
    # Scan a single port
    while not port_queue.empty():
        port = port_queue.get()
        try:
            # Create new socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5) # Connection timeout
                
                # Attempt connection
                result = s.connect_ex((target_ip, port))
                
                if result == 0:
                    # Port is open
                    banner = get_service_banner(s)
                    with print_lock:
                        open_ports.append((port, banner))

        except (socket.gaierror, socket.error):
            pass # Handle errors silently
        finally:
            port_queue.task_done() # Mark port as done

def main():
    # Get target IP
    try:
        target_host = input("Enter target IP address: ")
        target_ip = socket.gethostbyname(target_host)
    except socket.gaierror:
        print(f"Error: Cannot resolve hostname '{target_host}'")
        sys.exit(1)

    # Get port range
    try:
        port_range_str = input("Enter port range (e.g., 1-1024): ")
        start_port, end_port = map(int, port_range_str.split('-'))
        if start_port > end_port or start_port < 1:
            raise ValueError
    except ValueError:
        print("Invalid port range. Use format: 1-1024. Exiting.")
        sys.exit(1)

    print(f"\n[+] Scanning {target_ip} from port {start_port} to {end_port}...")
    scan_start_time = datetime.now()

    # Populate queue with ports
    for port in range(start_port, end_port + 1):
        port_queue.put(port)

    # Start threads
    for _ in range(NUM_THREADS):
        t = threading.Thread(target=scan_port, args=(target_ip,))
        t.daemon = True
        t.start()

    # Wait for queue to empty
    port_queue.join()

    # Calculate scan time
    scan_end_time = datetime.now()
    total_time = scan_end_time - scan_start_time

    # Display results
    print("\n--- Scan Results ---")
    print(f"{'Port':<10} {'Banner / Service'}")
    print("-" * 40)
    
    # Sort results
    open_ports.sort(key=lambda x: x[0])
    
    if not open_ports:
        print("No open ports found.")
    else:
        for port, banner in open_ports:
            print(f"{port:<10} {banner}")

    print(f"\nScan completed in: {total_time}")

if __name__ == "__main__":
    main()