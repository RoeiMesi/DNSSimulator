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
                print(f"Found in cache: {key}, {cache[key][0]}, {cache[key][1]}") #Todo: remove
                return f"{key}, {cache[key][0]}, {cache[key][1]}"
        elif domain.endswith(key):
                if time.time() > cache[key][2]:
                    del cache[key]
                    return "non-existent domain"
                else:
                    if cache[key][1] == "NS":
                        print(f"Found in cache: {key}, {cache[key][0]}, {cache[key][1]}") #Todo: remove
                        return f"{key}, {cache[key][0]}, {cache[key][1]}"
    return "non-existent domain"

def is_valid_domain(domain):
    if domain == "non-existent domain":
        return False
    return "." in domain and "," not in domain

def add_to_cache(input, cache_time):
    domain, ip, type = input.split(',')
    cache[domain] = (ip, type, time.time() + cache_time)
    print(f"----{domain},{ip},{type} added to cache----") #Todo: remove

def forward_to_server(query, parentIP, parentPort):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as parent_socket:
        parent_socket.sendto(query.encode('utf-8'), (parentIP, int(parentPort)))
        response, _ = parent_socket.recvfrom(1024)  # Wait for the parent's response
        return response.decode('utf-8')
    
def main(myPort, parentIP, parentPort, cache_time):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', int(myPort)))

    while True:
        data, clientAddr = s.recvfrom(1024)
        query = data.decode('utf-8').strip()

        if not is_valid_domain(query):
            print(f"--Invalid domain: {query}--") #Todo: remove
            continue

        print("-----------current cache list----------") #Todo: remove
        for key in list(cache.keys()): #Todo: remove
            print(f"Found in cache: {key}, {cache[key][0]}, {cache[key][1]}") #Todo: remove
        print("--------------------------------") #Todo: remove
        # Check the cache
        cached_response = cache_response(query)
        if cached_response != "non-existent domain":
            if cached_response.endswith("A"):
                # cached 'A' record, send to client
                s.sendto(cached_response.encode('utf-8'), clientAddr)
            elif cached_response.endswith("NS"):
                # handle cached NS record by using it to forward the query
                parent_response = cached_response
                while True:
                    print(f"Using cached NS record: {parent_response}") #Todo: remove
                    # extract server IP and port from the cached NS record
                    try:
                        suffix_domain, ipport, record_type = parent_response.split(',')
                        if ':' not in ipport or record_type.strip() != "NS":
                            print(f"Invalid NS record format: {parent_response}") #Todo: remove
                            s.sendto("non-existent domain".encode('utf-8'), clientAddr)
                            break
                        serverIP, serverPort = ipport.strip().split(':')
                        print(f"Forwarding query '{query}' to {serverIP}:{serverPort}") #Todo: remove
                        # Forward the query to the next server
                        parent_response = forward_to_server(query, serverIP, int(serverPort))
                        print(f"Received response: {parent_response}") #Todo: remove
                        if parent_response != "non-existent domain":
                            add_to_cache(parent_response, cache_time)
                        # Check the type of the response
                        if parent_response.endswith("A"):
                            print("Final response received. Returning to client.") #Todo: remove
                            s.sendto(parent_response.encode('utf-8'), clientAddr)
                            break
                        elif parent_response.endswith("NS"):
                            # Continue forwarding using the new NS record
                            continue
                        else:
                            print(f"Unexpected response type: {parent_response}") #Todo: probably useless if input is promised to be correct.
                            s.sendto("non-existent domain".encode('utf-8'), clientAddr)
                            break
                    except Exception as e:
                        print(f"Error processing cached NS record: {e}") #Todo: remove
                        s.sendto("non-existent domain".encode('utf-8'), clientAddr)
                        break
            else:
                # Unexpected record type
                print(f"Unexpected cached response: {cached_response}") #Todo: remove
                s.sendto("non-existent domain".encode('utf-8'), clientAddr)
        else:
            # Proceed to query the parent server
            parent_response = forward_to_server(query, parentIP, parentPort)
            # Cache the parent's response
            if parent_response != "non-existent domain":
                while True:
                    print(f"Response from parent: {parent_response}") #Todo: remove
                    if parent_response != "non-existent domain":
                        add_to_cache(parent_response, cache_time)
                    # If the response ends with "A", it's the final answer
                    if parent_response.endswith("A"):
                        print("Final response received. Returning to client.") #Todo: remove
                        s.sendto(parent_response.encode('utf-8'), clientAddr)
                        break
                    elif parent_response.endswith("NS"):
                        try:
                            # Parse the NS record to extract IP and port
                            suffix_domain, ipport, record_type = parent_response.split(',')
                            if ':' not in ipport or record_type.strip() != "NS":
                                print(f"Invalid NS response format: {parent_response}") #Todo: remove
                                s.sendto("non-existent domain".encode('utf-8'), clientAddr)
                                break
                            serverIP, serverPort = ipport.strip().split(':')
                            print(f"Forwarding query '{query}' to {serverIP}:{serverPort}") #Todo: remove
                            # Forward the query to the next server
                            parent_response = forward_to_server(query, serverIP, int(serverPort))
                            print(f"Received response: {parent_response}") #Todo: remove
                            if parent_response != "non-existent domain":
                                add_to_cache(parent_response, cache_time)
                        except Exception as e:
                            print(f"Error parsing or forwarding NS response: {e}")
                            s.sendto("non-existent domain".encode('utf-8'), clientAddr)
                            break
                    else:
                        print(f"Unexpected response type: {parent_response}") #Todo: probably useless if input is promised to be correct.
                        s.sendto("non-existent domain".encode('utf-8'), clientAddr)
                        break
            else:
                # Parent response is "non-existent domain"
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
        print("Resolver server is running.") #Todo: remove
        main(myPort, parentIP, parentPort, cache_time)