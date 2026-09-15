#!/usr/bin/env python3
"""
Simple DNS client for testing the ad blocker server
"""

import socket
import struct
import sys

def send_dns_query(server_ip: str, domain: str, port: int = 53) -> str:
    """Send DNS query and receive response"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Build DNS query packet
    transaction_id = b'\x12\x34'  # Random ID
    query = transaction_id + b'\x01\x00'  # Standard query
    query += b'\x00\x01'  # 1 question
    query += b'\x00\x00\x00\x00\x00\x00'  # 0 answers, authority, additional
    
    # Add domain name
    for label in domain.split('.'):
        query += struct.pack('!B', len(label)) + label.encode()
    query += b'\x00'
    query += struct.pack('!H', 1)  # Type A
    query += struct.pack('!H', 1)  # Class IN
    
    try:
        sock.sendto(query, (server_ip, port))
        sock.settimeout(2)
        response, _ = sock.recvfrom(512)
        
        # Parse response
        if len(response) > 6:
            answer_count = struct.unpack('!H', response[6:8])[0]
            return f"Domain: {domain} | Answers: {answer_count} | Response: {'BLOCKED' if answer_count == 0 else 'ALLOWED'}"
        else:
            return f"Domain: {domain} | No response"
    except socket.timeout:
        return f"Domain: {domain} | Timeout"
    except Exception as e:
        return f"Domain: {domain} | Error: {e}"
    finally:
        sock.close()

if __name__ == "__main__":
    server = "127.0.0.1"
    port = 53
    
    # Test domains
    test_domains = [
        "google.com",
        "ads.google.com",
        "doubleclick.net",
        "example.com",
        "github.com",
    ]
    
    print(f"Testing DNS queries against {server}:{port}\n")
    for domain in test_domains:
        print(send_dns_query(server, domain, port))
