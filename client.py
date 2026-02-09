import socket
import threading
import random
import time
import sys
from packet import Packet

ROUTER_IP = "127.0.0.1"
PORT = 5000

def listen(sock):
    while True:
        try:
            data = sock.recv(4096).decode()
            if not data:
                break
            
            for line in data.split('\n'):
                if not line.strip(): continue
                pkt = Packet.from_json(line)
                print(f"\n[RECEIVED] From {pkt.src_ip} | {pkt.size_kb}KB | {pkt.payload_type}")
                print("> ", end="", flush=True)
        except:
            break

def main():
    print("Creating PC...")
    my_ip = input("Give PC IP: ").strip()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ROUTER_IP, PORT))
        sock.send(my_ip.encode())
    except:
        print("Could not connect to Router. Is it running?")
        return

    listener = threading.Thread(target=listen, args=(sock,), daemon=True)
    listener.start()

    while True:
        print("\n" + "="*20)
        print(f" PC: {my_ip} (Connected)")
        print("="*20)
        print("1. Manual Mode")
        print("2. Automatic Mode")
        print("3. Exit")
        choice = input("> ").strip()

        if choice == "1":
            print("\n[MANUAL] Type 'exit' as IP to go back.")
            while True:
                try:
                    dest = input("Destination IP: ")
                    if dest.lower() == "exit": 
                        break # Break the inner loop and return to menu

                    size = int(input("Size (KB): "))
                    ptype = input("Type (text/image/video): ")
                    
                    pkt = Packet(my_ip, dest, size, ptype)
                    # Added '\n' to fix stickiness on router side
                    sock.sendall((pkt.to_json() + "\n").encode()) 
                    print("Packet sent.")
                except ValueError:
                    print("Invalid number input.")
                except Exception as e:
                    print(f"Error: {e}")
                    break

        elif choice == "2":
            dest = input("Destination IP: ")
            print("\n[AUTO] Starting... Press 'Ctrl + C' to stop.")
            print("-" * 30)

            try:
                while True:
                    pkt = Packet(
                        my_ip,
                        dest,
                        random.randint(10, 300),
                        random.choice(["text", "image", "video"])
                    )
                    try:
                        sock.sendall((pkt.to_json() + "\n").encode())
                        print(f"Sent {pkt.payload_type} ({pkt.size_kb}KB) -> {dest}")
                    except:
                        print("Router unreachable. Stopping sender.")
                        break

                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n[STOPPED] Automatic sending stopped.")
                print("Returning to Main Menu...")
                time.sleep(0.5) 

        elif choice == "3":
            print("Disconnecting...")
            sock.close()
            sys.exit()

if __name__ == "__main__":
    main()