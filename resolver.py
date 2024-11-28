import socket
import sys
import time

# Global cache to store DNS records with expiration times
cache = {}

def cache_response(domain):
    """Check if the domain is in cache; return cached response or 'non-existent domain'."""
    cache_clean() # Clean expired entries before checking the cache
    # Check for an exact match in the cache
    entry = cache.get(domain)
    if entry:
        return f"{domain},{entry[0]},{entry[1]}"

    # Check for suffix matches (NS records) in the cache
    for key, entry in cache.items():
        if domain.endswith(key):
            if entry[1] == "NS":
                return f"{key},{entry[0]},{entry[1]}"
    # No matching record found in the cache
    return "non-existent domain"

def cache_clean():
    """Remove expired entries from the cache."""
    expired_keys = [key for key, entry in cache.items() if time.time() > entry[2]]
    for key in expired_keys:
        del cache[key]

def is_valid_domain(domain):
    # Validate the domain format.
    if domain == "non-existent domain":
        return False
    return "." in domain and "," not in domain

def add_to_cache(input_record, cache_time):
    # Add a DNS record to the cache with an expiration time.
    domain, ip, record_type = input_record.split(',')
    cache[domain] = (ip, record_type, time.time() + cache_time)

def forward_to_server(query, serverIP, serverPort):
    # Forward the DNS query to the specified server and return the response.
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.sendto(query.encode('utf-8'), (serverIP, int(serverPort)))
        response, _ = server_socket.recvfrom(1024)
        return response.decode('utf-8')
    
def main(myPort, parentIP, parentPort, cache_time):
    # Handle incoming DNS queries and respond appropriately.
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', int(myPort)))

    while True:
        data, clientAddr = s.recvfrom(1024)
        query = data.decode('utf-8').strip()

        if not is_valid_domain(query):
            continue

        # Check if the query can be answered from the cache
        cached_response = cache_response(query)
        if cached_response != "non-existent domain":
            if cached_response.endswith("A"):
                # Send cached 'A' record to the client
                s.sendto(cached_response.encode('utf-8'), clientAddr)
            elif cached_response.endswith("NS"):
                # Use cached NS record to forward the query
                parent_response = cached_response
                while True:
                    try:
                        suffix_domain, ipport, record_type = parent_response.split(',')
                        if ':' not in ipport or record_type.strip() != "NS":
                            s.sendto("non-existent domain".encode('utf-8'), clientAddr)
                            break
                        serverIP, serverPort = ipport.strip().split(':')
                        parent_response = forward_to_server(query, serverIP, int(serverPort))
                        if parent_response != "non-existent domain":
                            add_to_cache(parent_response, cache_time)
                        if parent_response.endswith("A"):
                            s.sendto(parent_response.encode('utf-8'), clientAddr)
                            break
                        elif parent_response.endswith("NS"):
                            continue  # Continue forwarding using the new NS record
                        else:
                            s.sendto("non-existent domain".encode('utf-8'), clientAddr)
                            break
                    except Exception:
                        s.sendto("non-existent domain".encode('utf-8'), clientAddr)
                        break
            else:
                # Unexpected record type in cache
                s.sendto("non-existent domain".encode('utf-8'), clientAddr)
        else:
            # Forward the query to the parent server
            parent_response = forward_to_server(query, parentIP, parentPort)
            if parent_response != "non-existent domain":
                while True:
                    add_to_cache(parent_response, cache_time)
                    if parent_response.endswith("A"):
                        s.sendto(parent_response.encode('utf-8'), clientAddr)
                        break
                    elif parent_response.endswith("NS"):
                        try:
                            suffix_domain, ipport, record_type = parent_response.split(',')
                            if ':' not in ipport or record_type.strip() != "NS":
                                s.sendto("non-existent domain".encode('utf-8'), clientAddr)
                                break
                            serverIP, serverPort = ipport.strip().split(':')
                            parent_response = forward_to_server(query, serverIP, int(serverPort))
                            if parent_response != "non-existent domain":
                                add_to_cache(parent_response, cache_time)
                        except Exception:
                            s.sendto("non-existent domain".encode('utf-8'), clientAddr)
                            break
                    else:
                        s.sendto("non-existent domain".encode('utf-8'), clientAddr)
                        break
            else:
                # No response from parent server
                s.sendto(parent_response.encode('utf-8'), clientAddr)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python3 resolver.py [myPort] [parentIP] [parentPort] [cacheTime]")
        sys.exit(1)
    else:
        myPort = int(sys.argv[1])
        parentIP = sys.argv[2]
        parentPort = int(sys.argv[3])
        cache_time = int(sys.argv[4])
        main(myPort, parentIP, parentPort, cache_time)
