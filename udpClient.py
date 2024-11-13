import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(b'Dean Cohen & Roei Mesilaty', ('192.168.49.131', 12345))
# print("The data has been sent")

data, addr = s.recvfrom(1024)
print(str(data), addr)
# print("Received data from server: ", str(data), addr)

s.close()
# print("The socket has been closed")