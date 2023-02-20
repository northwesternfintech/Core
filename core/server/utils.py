import socket
import zmq
import zmq.asyncio

from typing import List, Optional, Dict


def is_port_in_use(port: int) -> bool:
    """Determines whether a given port is in use on this machine.

    Credit: https://codereview.stackexchange.com/questions/116450/find-available-ports-on-localhost
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(('localhost', port)) == 0


def find_open_ports(num_ports) -> List[int]:
    """Finds an open port to use on this machines.

    Parameters
    ----------
    num_ports : int
        Number of ports to find.

    Returns
    -------
    List[int]
        List of available ports.
    """
    free_ports = []
    for i in range(num_ports):
        sock = socket.socket()
        sock.bind(('', 0))
        free_ports.append(sock.getsockname()[1])

        sock.close()

    return free_ports


def convert_tcp_address(tcp_address: str, interface: str = "localhost"):
    """Replaces the wildcard ("*") in a tcp_address (e.g. "tcp://*:5000")
    with the interface 

    Parameters
    ----------
    tcp_address : str
        ZMQ tcp address string to convert (e.g. "tcp://*:5000")
    interface : str, optional
        String to replace wildcard ("*") with, by default "localhost". If no
        wildcard is found, return tcp_address
    """
    return tcp_address.replace("*", interface)


async def send_zmq_req(message: List[str], address: str, timeout_s=5) -> Optional[List]:
    """Decodes message to bytes, sends message to ZMQ as REQ, polls for response

    Parameters
    ----------
    message : Dict
        Multipart messae to serialize and send to ZMQ
    address : str
        Address for socket to connect/send to
    timeout_s : int, optional
        Polling timeout, by default 5

    Returns
    -------
    Optional[List]
        Returns response or None if timeout
    """
    context = zmq.asyncio.Context()
    poller = zmq.asyncio.Poller()
    socket = context.socket(zmq.REQ)
    socket.connect(address)
    poller.register(socket, zmq.POLLIN)

    for i, frame in enumerate(message):
        message[i] = frame.encode()

    await socket.send_multipart(message)

    socks = await poller.poll(timeout_s * 1000)
    socks = dict(socks)
    
    res = None
    if socks.get(socket) == zmq.POLLIN:
        res = (await socket.recv_multipart())[1:]

    socket.setsockopt(zmq.LINGER, 0)
    socket.close()
    context.term()
    
    return res

