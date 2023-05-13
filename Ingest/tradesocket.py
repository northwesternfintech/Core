import websocket, logging, threading, time, json, os, datetime
import numpy as np

SYMBOLS = []
BASEPATH = ""
global symbol_data
symbol_data = {symbol: np.array([]) for symbol in SYMBOLS} 
stop_event = threading.Event()
symbollock = threading.Lock()


def start_socket():
    logging.basicConfig(level=logging.WARNING)
    while True:
        try:
            ws = websocket.WebSocketApp("wss://ws-feed.exchange.coinbase.com",
                                        on_open=on_open,
                                        on_message=on_message,
                                        on_error=on_error,
                                        on_close=on_close,
                                      )
            ws.run_forever(ping_interval=5)
        except Exception as e:
            time.sleep(5)

def on_close(ws, close_status_code, close_msg):
    print(f"WebSocket closed with status code {close_status_code} and message: {close_msg}")

def on_error(ws, error):
    print(f"WebSocket error: {error}")

def on_open(ws):
    print("WebSocket opened")
    subscribe = {"type": "subscribe", "channels": [{"name": "matches", "product_ids": SYMBOLS}]}
    ws.send(json.dumps(subscribe))

def on_message(ws, message):
    global symbol_data
    message_data = dict(json.loads(message))
    if message_data == {}:
        raise Exception
    product_id = message_data.get("product_id")
    with symbollock:
        if product_id in symbol_data:
            symbol_data[product_id] = np.append(symbol_data[product_id], message_data)
        else:
            print(f"Unknown product_id {product_id} in message: {message_data}")

def start_discharge():
    while True:
        if stop_event.is_set():
            return
        time.sleep(60)
        global symbol_data
        with symbollock:
            for symbol in SYMBOLS:
                path = BASEPATH + symbol + "/" + symbol+ "_UATrades_" + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")) + ".csv"
                os.makedirs(os.path.dirname(path), exist_ok=True)
                np.savetxt(path, symbol_data[symbol], delimiter=",", fmt="%s")
            symbol_data = {symbol: np.array([]) for symbol in SYMBOLS}
            print("Data Saved")

def end():
    stop_event.set()

if __name__ == "__main__":
    t = threading.Thread(target=start_socket)
    s = threading.Thread(target=start_discharge)
    t.start()
    s.start()
    while True:
        time.sleep(1)
