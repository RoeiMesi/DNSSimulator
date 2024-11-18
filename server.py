import sys
import socket

def parse_file(records, file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        print("----------Parsing Test----------")
        for line in lines:
            line.strip()
            if line:
                domain, ip, type = line.split(',')
                records[domain] = (ip, type.strip())
                print(f"{domain},{ip},{type.strip()}")
        print("----------Parsing Test----------")


def records_response(domain, records):
    for key in records:
        if domain == key:
            return f"{key},{records[key][0]},{records[key][1]}"
        elif domain.endswith(key):
            if records[key][1] == "NS":
                return f"{key},{records[key][0]},{records[key][1]}"
    return "non-existent domain"


def main(myPort, zoneFileName):
    records = {}
    parse_file(records, zoneFileName)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', myPort))

    while True:
        data, addr = s.recvfrom(1024)
        domain = data.decode('utf-8').strip()
        answer = records_response(domain, records)
        s.sendto(answer.encode('utf-8'), addr)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("[myPort], [zoneFileName]") # Testing
        sys.exit(1)

    myPort = int(sys.argv[1])
    zoneFileName = sys.argv[2]

    main(myPort, zoneFileName)