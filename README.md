# Python Cybersecurity Toolkit

**Warning: This repository is for educational purposes ONLY. Do not use these tools on any network or system without explicit, written permission. Unauthorized access or scanning is illegal and unethical.**

This repository contains a collection of cybersecurity tools written in Python. Each project is designed to demonstrate fundamental concepts in network security, penetration testing, and cryptography.

---

## Projects Included

This toolkit is divided into several independent modules:

### 1. Network Scanner
* **File:** `Network_Scanner/network_scanner.py`
* **Description:** Discovers active devices on a local network by sending ARP requests.
* **Usage:** `python network_scanner.py` (May require admin/sudo privileges)

### 2. Port Scanner
* **File:** `Port_Scanner/port_scanner.py`
* **Description:** A multi-threaded TCP port scanner that identifies open ports and grabs service banners from a target IP.
* **Usage:** `python port_scanner.py`

### 3. Subdomain Enumerator
* **File:** `Subdomain_Enumeration/subdomain_scanner.py`
* **Description:** A multi-threaded tool to discover active subdomains of a target domain using a wordlist.
* **Usage:** `python subdomain_scanner.py -d <domain> -w <wordlist> -o <output_file>`

### 4. Password Cracker
* **File:** `Password_Cracker/password_cracker.py`
* **Description:** Performs a multi-threaded dictionary attack against a given hash (e.g., MD5, SHA-256).
* **Usage:** `python password_cracker.py -H <hash> -t <type> -w <wordlist>`

### 5. PDF Cracker
* **File:** `PDF_Cracker/pdf_cracker.py`
* **Description:** A multi-threaded dictionary attack tool to find the password of an encrypted PDF file.
* **Usage:** `python pdf_cracker.py -p <pdf_file> -w <wordlist>`

### 6. PDF Protection Tool
* **File:** `PDF_Protection/pdf_protector.py`
* [cite_start]**Description:** Adds password protection (encryption) to an existing PDF file[cite: 66, 71].
* **Usage:** `python pdf_protector.py -i <input_pdf> -o <output_pdf> -p <password>`

---

## Getting Started

### Prerequisites

Before running any scripts, you must install the required Python libraries.

```bash
# For Network Scanner
pip install scapy

# For PDF Cracker
pip install pikepdf tqdm

# For PDF Protection Tool
pip install pypdf

# For Subdomain Enumerator
pip install requests

# Other scripts use built-in libraries