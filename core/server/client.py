import zmq
import json
import requests
import time


def start():
    params = {
        "exchange": "kraken", 
        "tickers": ["BTC/USD"]
    }
    res = requests.post("http://127.0.0.1:5000/websocket/start", json=params)
    print(res.status_code)
    return res.json()


# def start(socket):
#     params = {
#         "exchange": "kraken", 
#         "tickers": ["BTC/USD"]
#     }

#     msg = [b"websocket", b"start", json.dumps(params).encode()]
#     socket.send_multipart(msg)
#     return socket.recv_multipart()[1:]


# def status(socket, uuid):
#     params = { "uuid": uuid
#     }
#     msg = [b"websocket", b"status", json.dumps(params).encode()]
#     socket.send_multipart(msg)
#     return socket.recv_multipart()[1:]

def status(uuid):
    res = requests.get(f"http://127.0.0.1:5000/websocket/status/{uuid}")
    print(res.status_code)
    print(res.json())
    return res.text

def stop(uuid):
    res = requests.post(f"http://127.0.0.1:5000/websocket/stop/{uuid}")
    print(res.status_code)
    print(res.json())
    return res.json()
# def stop(socket, uuid):
#     params = { "uuid": uuid
#     }
#     msg = [b"websocket", b"stop", json.dumps(params).encode()]
#     socket.send_multipart(msg)
#     return socket.recv_multipart()[1:]

def main():
    uuid = start()
    for i in range(3):
        status(uuid)
        time.sleep(0.5)
    stop(uuid)


# def main():
#     import time
#     context = zmq.Context()
#     sock = context.socket(zmq.REQ)
#     sock.connect("tcp://localhost:5557")
#     # print(status(sock, "ef543728-a9b2-4296-a6a4-5c413a0db88a"))

#     rep = start(sock)
#     if rep[0] == b"\x04":
#         print(rep)
#         for i in range(2):
#             time.sleep(3)
#             print(status(sock, rep[1].decode()))
#         print(stop(sock, rep[1].decode()))
#         print(status(sock, rep[1].decode()))
#     else:
#         print("ERROR")
#         print(rep)