import re
from langdetect import detect, DetectorFactory
import socket

def clean_text(content):
    # Step 1: Remove HTML tags
    content = re.sub(r'<[^>]+>', '', content)
    
    # Step 2: Replace newlines (\n) and tabs (\t) with spaces
    content = content.replace('\n', ' ').replace('\t', ' ')
    
    # Step 3: Replace multiple spaces with a single space
    content = re.sub(r'\s+', ' ', content)
    
    # Step 4: Remove leading/trailing whitespace
    content = content.strip()
    
    return content

def detect_lang(content):
    
    DetectorFactory.seed = 0
    if content != "":
        
        language = detect(content)
        return language
    else:
        return "en"
    
    
def extract_ip_or_default(path):
    # Regular expression to match an IP address
    ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    
    # Search for IP address in the input string
    match = re.search(ip_pattern, path)
    
    if match:
        return match.group(0)  # Return the found IP address
    else:
        return "127.0.0.1"  # Default to 127.0.0.1 if no IP address is found

# def get_local_ip():
#     try:
#         # Get the local hostname
#         hostname = socket.gethostname()
#         # Get the IP address corresponding to the hostname
#         local_ip = socket.gethostbyname(hostname)
#         return local_ip
#     except socket.error as e:
#         return f"Error: {e}"


def get_local_ip():
    try:
        # Create a socket and connect to an external address (e.g., Google's public DNS server)
        # This doesn't actually establish a connection but helps determine the real local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except socket.error as e:
        return f"Error: {e}"


    
# print(detect_lang(""))
# print(str(get_local_ip()))