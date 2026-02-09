import socket
import threading
import random
import time
from packet import Packet

ROUTER_IP = "127.0.0.1"
PORT = 5000


def listen(sock):
    while True:
        try:
            data = sock.recv(4096).decode()
            if not data:
                break
            pkt = Packet.from_json(data)
            print(f"\n[RECEIVED] From {pkt.src_ip} | {pkt.size_kb}KB | {pkt.payload_type}")
            print("> ", end="", flush=True)
        except:
            break


def main():
    print("Creating PC...")
    my_ip = input("Give PC IP: ").strip()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ROUTER_IP, PORT))
    sock.send(my_ip.encode())

    print("\nSelect Mode:")
    print("1. Manual")
    print("2. Automatic")
    choice = input("> ").strip()

    listener = threading.Thread(target=listen, args=(sock,), daemon=True)
    listener.start()

    if choice == "1":
        while True:
            try:
                dest = input("Destination IP: ")
                size = int(input("Size (KB): "))
                ptype = input("Type (text/image/video): ")
                pkt = Packet(my_ip, dest, size, ptype)
                sock.sendall(pkt.to_json().encode())
            except:
                print("Connection closed.")
                break

    elif choice == "2":
        dest = input("Destination IP: ")
        print("Automatic sending started...\n")

        while True:
            try:
                pkt = Packet(
                    my_ip,
                    dest,
                    random.randint(10, 300),
                    random.choice(["text", "image", "video"])
                )
                try:
                    sock.sendall((pkt.to_json() + "\n").encode())
                except:
                    print("Router unreachable. Stopping sender.")
                    break

                time.sleep(1)
            except:
                print("Connection closed by router.")
                break


if __name__ == "__main__":
    main()
