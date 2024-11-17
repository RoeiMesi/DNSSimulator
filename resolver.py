import socket
import sys
import time

cache = {}
def cache_response(domain):
    for key in list(cache.keys()):
        if domain == key:
            if time.time() > cache[key][2]:
                del cache[key]
                return "non-existent domain"
            else:
                return f"{key}, {cache[key][0]}, {cache[key][1]}"
        elif domain.endswith(key):
                if time.time() > cache[key][2]:
                    del cache[key]
                    return "non-existent domain"
                else:
                    if cache[key][1] == "NS":
                        return f"{key}, {cache[key][0]}, {cache[key][1]}"
    return "non-existent domain"

def is_valid_domain(domain):
    if domain == "non-existent domain":
        return False
    return "." in domain and "," not in domain

def add_to_cache(input, cache_time):
    domain, ip, type = input.split(',')
    cache[domain] = (ip, type, time.time() + cache_time)

def forward_to_parent(query, parentIP, parentPort):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as parent_socket:
        parent_socket.sendto(query.encode('utf-8'), (parentIP, int(parentPort)))
        response, _ = parent_socket.recvfrom(1024)  # Wait for the parent's response
        return response.decode('utf-8')

def main(myPort, parentIP, parentPort, cache_time):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('0.0.0.0', int(myPort)))

    while True:
        data, addr = s.recvfrom(1024)
        query = data.decode('utf-8').strip()

        if not is_valid_domain(query):
            print(f"--Invalid domain: {query}--")
            continue

        # Check the cache
        cached_response = cache_response(query)
        if cached_response != "non-existent domain":
            s.sendto(cached_response.encode('utf-8'), addr)
        else:
            parent_response = forward_to_parent(query, parentIP, parentPort)

            # Cache the parent's response
            if parent_response != "non-existent domain":
                print(f"Response from parent: {parent_response}")
                add_to_cache(parent_response, cache_time)
            
            # Send the parent's response to the client
            s.sendto(parent_response.encode('utf-8'), addr)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit(1)
    else:
        myPort = int(sys.argv[1])
        parentIP = sys.argv[2]
        parentPort = int(sys.argv[3])
        cache_time = int(sys.argv[4])
        main(myPort, parentIP, parentPort, cache_time)