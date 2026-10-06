# -*- coding: utf-8 -*-
# 🚀 SS YAZILIM UZAKTAN BAĞLANMA - ARKA PLAN SİNYAL PORT MOTORU
import socket
import threading
import json
import random
import os

# Render'ın otonom portunu yakalayan akıllı satır
PORT = int(os.environ.get("PORT", 1999))
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', PORT))
server.listen(50)

print(f"🟢 SS Yazılım Sinyal Hattı {PORT} üzerinde aktif!")
clients = {}

def handle_client(conn, addr):
    client_id = None
    while True:
        try:
            data = conn.recv(1024 * 1024)
            if not data: break
            try:
                packet = json.loads(data.decode('utf-8'))
            except:
                if client_id and client_id in clients:
                    target_id = clients[client_id].get("target")
                    if target_id and target_id in clients:
                        clients[target_id]["socket"].sendall(data)
                continue

            if packet.get("type") == "register":
                if packet.get("role") == "client":
                    client_id = str(random.randint(100000, 999999))
                    while client_id in clients: client_id = str(random.randint(100000, 999999))
                    clients[client_id] = {"socket": conn, "role": "client", "password": packet.get("password"), "target": None}
                    conn.sendall(json.dumps({"type": "init_success", "id": client_id}).encode('utf-8'))
                elif packet.get("role") == "admin":
                    client_id = "ADMIN_" + str(random.randint(1000, 9999))
                    clients[client_id] = {"socket": conn, "role": "admin", "target": None}

            elif packet.get("type") == "connect_request":
                t = packet.get("target_id")
                if t in clients and clients[t]["role"] == "client" and clients[t]["password"] == packet.get("password"):
                    clients[client_id]["target"] = t
                    clients[t]["target"] = client_id
                    conn.sendall(json.dumps({"type": "connect_success"}).encode('utf-8'))
                    clients[t]["socket"].sendall(json.dumps({"type": "start_stream"}).encode('utf-8'))
                else:
                    conn.sendall(json.dumps({"type": "connect_failed"}).encode('utf-8'))

            elif packet.get("type") in ["mousemove", "click"] and client_id in clients:
                target_id = clients[client_id].get("target")
                if target_id and target_id in clients: clients[target_id]["socket"].sendall(data)
        except: break

    if client_id in clients:
        target_id = clients[client_id].get("target")
        if target_id and target_id in clients:
            try: clients[target_id]["socket"].sendall(json.dumps({"type": "target_disconnected"}).encode('utf-8'))
            except: pass
            clients[target_id]["target"] = None
        del clients[client_id]
    conn.close()

while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr)).start()
