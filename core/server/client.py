import zmq
import json

def start(socket):
    params = {
        "exchange": "kraken", 
        "tickers": ["BTC/USD"]
    }

    msg = [b"websocket", b"start", json.dumps(params).encode()]
    socket.send_multipart(msg)
    return socket.recv_multipart()[1:]


def status(socket, uuid):
    params = { "uuid": uuid
    }
    msg = [b"websocket", b"status", json.dumps(params).encode()]
    socket.send_multipart(msg)
    return socket.recv_multipart()[1:]


def stop(socket, uuid):
    params = { "uuid": uuid
    }
    msg = [b"websocket", b"stop", json.dumps(params).encode()]
    socket.send_multipart(msg)
    return socket.recv_multipart()[1:]


def main():
    context = zmq.Context()
    sock = context.socket(zmq.REQ)
    sock.connect("tcp://localhost:5557")

    rep = start(sock)
    if rep[0] == b"\x04":
        print(rep)
        for i in range(5):
            print(status(sock, rep[1].decode()))
        print(stop(sock, rep[1].decode()))
        print(status(sock, rep[1].decode()))
    else:
        print("ERROR")
        print(rep)