import socket

from typing import List


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
