# DNS Simulator

This project simulates a simplified DNS resolution process using a client, a resolver (acting as a caching DNS server), and authoritative DNS servers. It demonstrates how DNS queries are forwarded, cached, and resolved against zone files, mimicking real DNS lookup behavior in a controlled environment.

## Overview

The system consists of three main components:

1. **Authoritative Server** (`server.py`):  
   Responds to DNS queries based on a specified zone file. The zone file contains mappings of domain names to IP addresses, along with their record types (`A` for direct IP mapping, or `NS` for delegating queries to another server).

2. **Resolver** (`resolver.py`):  
   Listens for incoming DNS queries from clients, checks its local cache, and if needed, forwards the queries to the authoritative server or other DNS servers (based on `NS` records). It caches responses to speed up subsequent queries.

3. **Client** (`client.py`):  
   Reads user input (domain names) and sends DNS queries to the resolver. Once the resolver responds, the client prints the resolved IP address or states that the domain does not exist.

The project includes two zone files (`zone.txt` and `zone2.txt`) that define the DNS records for testing purposes.

## Files

- `client.py`: The client program.
- `resolver.py`: The caching resolver.
- `server.py`: The authoritative server.
- `zone.txt`, `zone2.txt`: Zone files specifying domain records.

## Example Architecture

```
          Client
            |
            v
         Resolver
            |
     -----------------
     |               |
   Server1        Server2
   (with zone.txt) (with zone2.txt)
```

## Usage

1. **Start the Authoritative Servers**:  
   Each server reads from a zone file. For example, start the first server:
   ```bash
   python3 server.py 5555 zone.txt
   ```
   This will start the server listening on port `5555` using `zone.txt`.

   Similarly, start the second server for `zone2.txt`:
   ```bash
   python3 server.py 7777 zone2.txt
   ```

2. **Start the Resolver**:  
   The resolver expects a port to listen on, the IP and port of a "parent" server, and a cache time (in seconds). For example:
   ```bash
   python3 resolver.py 6666 127.0.0.1 5555 60
   ```
   This starts the resolver listening on port `6666`, with the authoritative server at `127.0.0.1:5555` as its parent, and a cache time of 60 seconds.

3. **Run the Client**:  
   The client connects to the resolver. Provide the resolver’s IP and port:
   ```bash
   python3 client.py 127.0.0.1 6666
   ```
   Once the client is running, type in a domain (e.g. `biu.ac.il`) and press Enter. The client sends a query to the resolver, which may resolve it directly from its cache or forward it to the appropriate server. The result will be printed on the client’s terminal.

   To exit the client, type:
   ```
   exit
   ```

## Environment

- Python 3.x
- Linux or macOS environment preferred (though it may work on other systems)
- Ensure that the ports used are free and accessible.
- No external libraries are required. The standard Python `socket` and `time` libraries are sufficient.

## How It Works

- **Query Resolution**:  
  The client sends a domain query to the resolver. The resolver checks its cache:
  - If cached, it returns the result immediately.
  - If not, it contacts the parent authoritative server or follows NS records until it finds the authoritative server that can resolve the domain.
  - The result is cached by the resolver for future queries.

- **Zone Files**:  
  The `server.py` script reads a zone file line-by-line. Each line specifies a domain, an IP (or `IP:Port` for NS), and a record type:
  - `A` records: Directly map a domain to an IP.
  - `NS` records: Indicate that another server (specified by IP:Port) should handle queries for domains under that suffix.

## Example Queries

- Running the client, if you query `biu.ac.il`, the resolver checks `zone.txt` via the authoritative server on port `5555`:
  - If found as an `A` record, it returns the IP directly.

- If you query a domain like `google.co.il`, and `.co.il` is delegated via an `NS` record to a server on `127.0.0.1:7777`:
  - The resolver forwards the query to the server on port `7777`.
  - The second server (with `zone2.txt`) resolves and returns the answer.
  - The resolver caches this result for future queries.

## Notes

- If a domain cannot be found in any server’s zone file or via NS delegation, the system returns `non-existent domain`.
- The cache ensures improved performance for repeated queries, respecting the defined `cache_time`.
- Update zone files to add/remove domain records as needed, then restart the server to apply the changes.

## Contributing

Feel free to extend or modify the project. You can:
- Add support for different record types.
- Implement advanced caching strategies.
- Introduce logging to track query resolution steps.

This project serves as a learning tool to understand the basics of DNS resolution, caching, and server delegation.
