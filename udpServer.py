import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('0.0.0.0', 12345))  # Binding to all available interfaces on port 12345

# print("Server is listening for incoming messages...")

while True:
    data, addr = s.recvfrom(1024)
    print(str(data), addr)
    # print("Received message:", str(data), "from", addr)
    s.sendto(data.upper(), addr)
