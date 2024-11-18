import socket
import sys

def main(serverIP, serverPort):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (serverIP, int(serverPort))

    # Need to remove this print before submission.
    print("Client is running. Enter a domain to query or type 'exit' to quit.")

    while True:
        # UI print - Need to be removed
        query = input("Enter domain: ").strip()
        if query.lower() == "exit":
            # UI print - Need to be removed
            print("Exiting client.")
            break

        if not query:
            # UI print - Need to be removed
            print("Please enter a valid domain.")
            continue

        client_socket.sendto(query.encode('utf-8'), server_address)
        response, _ = client_socket.recvfrom(1024)
        response_str = response.decode('utf-8')
        if response_str != "non-existent domain":
          parts = response_str.split(",")
          ip_address = parts[1]
          # Need to remove the "IP Address" from the print
          print(f"IP Address: {ip_address}")
        else:
            print("non-existent domain")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        # UI Print - Need to be removed
        print("Usage: python client.py [serverIP] [serverPort]")
        sys.exit(1)

    serverIP = sys.argv[1]
    serverPort = int(sys.argv[2])
    main(serverIP, serverPort)
