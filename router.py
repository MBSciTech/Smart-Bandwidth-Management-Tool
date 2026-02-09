import socket
import threading
from packet import Packet
import time

HOST = "0.0.0.0"
PORT = 5000

clients = {}  # ip -> socket
BANDWIDTH_LIMIT_KBPS = 100  # per PC


def handle_client(sock, ip):
    print(f"[ROUTER] PC connected: {ip}")
    last_sent = time.time()

    try:
        while True:
            data = sock.recv(4096).decode()
            if not data:
                break

            packet = Packet.from_json(data)
            print(f"[ROUTER] {packet.src_ip} → {packet.dest_ip} | {packet.size_kb}KB")

            # Bandwidth control
            now = time.time()
            time_needed = packet.size_kb / BANDWIDTH_LIMIT_KBPS
            if now - last_sent < time_needed:
                time.sleep(time_needed - (now - last_sent))
            last_sent = time.time()

            if packet.dest_ip in clients:
                try:
                    clients[packet.dest_ip].sendall((packet.to_json() + "\n").encode())
                except:
                    print(f"[ROUTER] Dropped packet {packet.packet_id} (destination offline)")

            else:
                print("[ROUTER] Destination unreachable")

    except:
        pass
    finally:
        sock.close()
        clients.pop(ip, None)
        print(f"[ROUTER] PC disconnected: {ip}")


def start_router():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print("[ROUTER] Router running...\n")

    while True:
        sock, _ = server.accept()
        ip = sock.recv(1024).decode()
        clients[ip] = sock

        threading.Thread(
            target=handle_client,
            args=(sock, ip),
            daemon=True
        ).start()


if __name__ == "__main__":
    start_router()
