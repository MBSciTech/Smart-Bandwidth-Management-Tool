# Smart Bandwidth Management Tool

A Python-based network simulation that demonstrates advanced **Software-Defined Networking (SDN)** concepts.
This tool simulates a **Smart Router** capable of real-time **Traffic Shaping**, **Congestion Control**, **Fair Usage Policy (FUP)** enforcement, and **Quality of Service (QoS)** prioritization.

---

## 🚀 Key Features

* **Smart Traffic Shaping (QoS)**
  Automatically prioritizes traffic based on payload type:

  * 🎥 **Video:** High Priority (100% bandwidth)
  * 🖼️ **Image:** Medium Priority (50% bandwidth)
  * 💬 **Text:** Low Priority (20% bandwidth)

* **Congestion Control (Load Balancing)**
  Dynamically distributes total bandwidth among all active users in real time.

* **Fair Usage Policy (FUP)**
  Monitors per-user data usage. If a user exceeds the quota (e.g., 5MB), their speed is throttled to **10%**.

* **Auto-Recovery (Leaky Bucket Algorithm)**
  Gradually restores quota over time, allowing users to recover from penalties automatically.

* **SDN Controller (Live Admin Control)**
  A separate control plane to update router settings without restarting the system.

---

## 📂 Project Structure

* `router.py` — Core router logic (packet handling, QoS, FUP, client management, admin server)
* `client.py` — Simulated PC that sends traffic (manual / automatic)
* `controller.py` — SDN controller to modify router settings at runtime
* `packet.py` — Packet format definition and JSON serialization

---

## ⚙️ Installation & Setup

* **Requirement:** Python 3.x
* **Libraries:** Uses only standard Python libraries (`socket`, `threading`, `json`, `time`)
* **Setup:** Place all files in the same directory

---

## 🏃 How to Run the Simulation

Open **three terminals**.

### Terminal 1: Router

```bash
python router.py
```

* Traffic Server → Port 5000
* Admin Server → Port 6000

### Terminal 2: Client (PC)

```bash
python client.py
```

* Enter PC IP (e.g., `127.0.0.1` or `192.168.1.10`)
* Select mode:

  * 1 → Manual
  * 2 → Automatic

### Terminal 3: Controller (Admin)

```bash
python controller.py
```

* Change bandwidth, quota, and recovery rate live

---

## 🧪 Demonstration Scenarios

### QoS

* Send text and video packets
* Video gets higher bandwidth

### Fair Usage Policy (FUP)

* Exceed quota in automatic mode
* Speed is throttled

### Auto-Recovery

* Stop traffic after penalty
* Quota refills automatically

### SDN Control

* Modify capacity via controller
* Client speed updates instantly

---

## 📝 Configuration

```python
TOTAL_CAPACITY_KBPS = 1000
QUOTA_LIMIT_KB = 5000
RECOVERY_RATE_KB = 1000
```

---

## 📜 License

Open-source project for educational use.
