import socket
import json
import time

ROUTER_IP = "127.0.0.1"
ADMIN_PORT = 6000

def main():
    print("Connecting to Router Admin Console...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ROUTER_IP, ADMIN_PORT))
        print("Connected! You can now control the router live.\n")
    except:
        print("Could not connect to Router. Make sure router.py is running.")
        return

    while True:
        print("-" * 30)
        print("1. Set Total Bandwidth Capacity")
        print("2. Set FUP Quota Limit")
        print("3. Set Recovery Rate")
        print("4. View Current Config")
        print("5. Exit")
        
        choice = input("Select Option > ").strip()

        if choice == "5":
            break

        command = {}
        
        if choice == "1":
            val = float(input("Enter new Capacity (KBps): "))
            command = {"action": "TOTAL_CAPACITY_KBPS", "value": val}
            
        elif choice == "2":
            val = float(input("Enter new Quota Limit (KB): "))
            command = {"action": "QUOTA_LIMIT_KB", "value": val}
            
        elif choice == "3":
            val = float(input("Enter Recovery Rate (KB): "))
            command = {"action": "RECOVERY_RATE_KB", "value": val}
            
        elif choice == "4":
            command = {"action": "GET_CONFIG"}
            
        else:
            print("Invalid option.")
            continue

        sock.send(json.dumps(command).encode())
        response = sock.recv(1024).decode()
        print(f"\n[ROUTER RESPONSE]: {response}\n")

    sock.close()

if __name__ == "__main__":
    main()