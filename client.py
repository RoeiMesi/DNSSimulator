import socket
import sys

def main(serverIP, serverPort):
    # Send DNS queries to the server and print the responses.
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (serverIP, int(serverPort))

    while True:
        try:
            query = input().strip()
        except EOFError:
            break
        if query.lower() == "exit":
            break

        if not query:
            continue

        client_socket.sendto(query.encode('utf-8'), server_address)
        response, _ = client_socket.recvfrom(1024)
        response_str = response.decode('utf-8')
        if response_str != "non-existent domain":
            parts = response_str.split(",")
            ip_address = parts[1]
            print(f"{ip_address}")
        else:
            print("non-existent domain")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(1)

    serverIP = sys.argv[1]
    serverPort = int(sys.argv[2])
    main(serverIP, serverPort)
