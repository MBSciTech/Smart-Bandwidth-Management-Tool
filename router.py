import socket
import threading
import time
import json
from datetime import datetime
from packet import Packet

# ==========================================
# 1. ROUTER CONFIGURATION
# ==========================================
HOST = "0.0.0.0"
PORT = 5000        # Traffic Port
ADMIN_PORT = 6000  # Controller Port (NEW)

# Shared Config (Now mutable by Controller)
config = {
    "TOTAL_CAPACITY_KBPS": 1000,
    "QUOTA_LIMIT_KB": 5000,
    "FUP_PENALTY_FACTOR": 0.1,
    "RECOVERY_RATE_KB": 1000,
    "RECOVERY_INTERVAL": 5
}

# Quality of Service (QoS) Weights
PRIORITY_WEIGHTS = {
    "video": 1.0,   
    "image": 0.5,   
    "text":  0.2    
}

# Global State
clients = {}       # ip -> socket
client_usage = {}  # ip -> total_kb_used
usage_lock = threading.Lock() 

# ==========================================
# 2. ADMIN LISTENER (NEW FEATURE)
# ==========================================
def handle_admin(sock):
    print(f"\n[ADMIN] Controller connected.")
    try:
        while True:
            data = sock.recv(1024).decode()
            if not data: break
            
            command = json.loads(data)
            action = command.get("action")
            value = command.get("value")

            if action in config:
                config[action] = value
                print(f"[ADMIN] UPDATE: Set {action} to {value}")
                sock.send(f"Success: {action} -> {value}".encode())
            elif action == "GET_CONFIG":
                sock.send(json.dumps(config).encode())
            else:
                sock.send("Error: Unknown command".encode())
    except:
        pass
    finally:
        print("[ADMIN] Controller disconnected.")
        sock.close()

def start_admin_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, ADMIN_PORT))
    server.listen()
    while True:
        sock, _ = server.accept()
        threading.Thread(target=handle_admin, args=(sock,), daemon=True).start()

# ==========================================
# 3. BACKGROUND TASKS (Quota Manager)
# ==========================================
def quota_manager():
    while True:
        time.sleep(config["RECOVERY_INTERVAL"]) # Use dynamic config
        
        with usage_lock:
            active_ips = list(client_usage.keys())
            users_needing_refill = [ip for ip in active_ips if client_usage[ip] > 0]
            
            if users_needing_refill:
                rate = config["RECOVERY_RATE_KB"] # Use dynamic config
                print(f"\n[SYSTEM] ♻️  Refilling Quotas (-{rate}KB)...")
                
                for ip in users_needing_refill:
                    client_usage[ip] = max(0, client_usage[ip] - rate)
                    
                    limit = config["QUOTA_LIMIT_KB"] # Use dynamic config
                    status = "RECOVERING" if client_usage[ip] > limit else "OK"
                    print(f"    ↳ {ip}: {client_usage[ip]}/{limit} KB [{status}]")

# ==========================================
# 4. CLIENT HANDLING (Traffic)
# ==========================================
def handle_client(sock, ip):
    curr_time = datetime.now().strftime("%H:%M:%S")
    print(f"[{curr_time}] [CONNECTION] PC Connected: {ip}")
    
    last_sent = time.time()
    buffer = ""

    with usage_lock:
        if ip not in client_usage: client_usage[ip] = 0

    try:
        while True:
            data = sock.recv(4096).decode()
            if not data: break
            buffer += data
            
            while "\n" in buffer:
                message, buffer = buffer.split("\n", 1)
                if not message.strip(): continue

                try:
                    packet = Packet.from_json(message)
                except: continue

                # --- SMART LOGIC (Using Dynamic Config) ---
                with usage_lock:
                    client_usage[ip] += packet.size_kb
                    current_usage = client_usage[ip]

                active_count = max(1, len(clients))
                base_speed = config["TOTAL_CAPACITY_KBPS"] / active_count

                is_penalized = False
                if current_usage > config["QUOTA_LIMIT_KB"]:
                    base_speed *= config["FUP_PENALTY_FACTOR"]
                    is_penalized = True

                p_type = packet.payload_type.lower()
                priority = PRIORITY_WEIGHTS.get(p_type, 0.5)
                allowed_speed = base_speed * priority
                # ------------------------------------------

                curr_time = datetime.now().strftime("%H:%M:%S")
                status_tag = "[FUP-PENALTY]" if is_penalized else "[OK]"
                print(f"[{curr_time}] {status_tag} {packet.src_ip} -> {packet.dest_ip} ({packet.payload_type})")
                print(f"    ↳ Usage: {current_usage:.0f}/{config['QUOTA_LIMIT_KB']}KB | Limit: {allowed_speed:.0f} KBps")

                now = time.time()
                time_needed = packet.size_kb / allowed_speed
                if now - last_sent < time_needed:
                    time.sleep(time_needed - (now - last_sent))
                last_sent = time.time()

                if packet.dest_ip in clients:
                    try:
                        clients[packet.dest_ip].sendall((packet.to_json() + "\n").encode())
                    except: pass
                else:
                    print(f"[{curr_time}] [ERROR] Dest {packet.dest_ip} unreachable")

    except: pass
    finally:
        sock.close()
        if ip in clients: del clients[ip]
        print(f"[CONNECTION] PC Disconnected: {ip}")

# ==========================================
# 5. MAIN ROUTER START
# ==========================================
def start_router():
    # Start Admin Server Thread
    threading.Thread(target=start_admin_server, daemon=True).start()
    
    # Start Quota Manager Thread
    threading.Thread(target=quota_manager, daemon=True).start()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"==================================================")
    print(f" SMART ROUTER RUNNING")
    print(f" Traffic Port: {PORT} | Admin Port: {ADMIN_PORT}")
    print(f"==================================================\n")

    while True:
        try:
            sock, _ = server.accept()
            ip = sock.recv(1024).decode().strip()
            if ip:
                clients[ip] = sock
                threading.Thread(target=handle_client, args=(sock, ip), daemon=True).start()
        except: pass

if __name__ == "__main__":
    start_router()