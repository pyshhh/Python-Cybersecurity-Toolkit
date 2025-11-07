import sys
import socket
import ipaddress
import threading
from queue import Queue
from scapy.all import srp, Ether, ARP, conf

# --- Configuration ---
NUM_THREADS = 50  # Number of threads [cite: 337]
conf.verb = 0     # Silence Scapy
print_lock = threading.Lock()
results = []
ip_queue = Queue()

def get_hostname(ip):
    # Resolve hostname from IP [cite: 336, 343]
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except socket.herror:
        return "N/A" # Handle lookup failure

def scan_ip(ip):
    # Send ARP request to a single IP [cite: 334, 349]
    try:
        packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=str(ip))
        ans, _ = srp(packet, timeout=2, retry=1)
        
        if ans:
            # Device is active, get MAC and hostname [cite: 335, 350]
            mac = ans[0][1].hwsrc
            hostname = get_hostname(str(ip))
            
            with print_lock:
                results.append((str(ip), mac, hostname))
    except Exception as e:
        pass # Ignore errors

def worker():
    # Thread worker function
    while not ip_queue.empty():
        ip = ip_queue.get()
        if ip:
            scan_ip(ip)
            ip_queue.task_done()

def main():
    # Get network CIDR from user [cite: 332, 347]
    try:
        target_network = input("Enter network (e.g., 192.168.1.0/24): ")
        network = ipaddress.ip_network(target_network)
    except ValueError:
        print("Invalid CIDR format. Exiting.")
        sys.exit(1)

    print(f"[+] Scanning {network}...")

    # Populate queue with all host IPs [cite: 333, 348]
    for ip in network.hosts():
        ip_queue.put(ip)

    # Start threads [cite: 342, 351]
    for _ in range(NUM_THREADS):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()

    # Wait for queue to empty
    ip_queue.join()

    # Display results in a table [cite: 338, 352]
    print("\n--- Scan Results ---")
    print(f"{'IP Address':<18} {'MAC Address':<20} {'Hostname':<30}")
    print("-" * 68)
    
    # Sort results by IP
    results.sort(key=lambda x: ipaddress.ip_address(x[0]))
    
    for ip, mac, hostname in results:
        print(f"{ip:<18} {mac:<20} {hostname:<30}")

    print("\nScan complete.")

if __name__ == "__main__":
    main()