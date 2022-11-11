import socket
import random


def is_port_in_use(port: int) -> bool:
    """Determines whether a given port is in use on this machine.

    Credit: https://codereview.stackexchange.com/questions/116450/find-available-ports-on-localhost
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(('localhost', port)) == 0


def find_open_port(port_range=(50000, 60000), max_tries=100) -> int:
    """Finds an open port to use on this machine.

    Parameters
    ----------
    port_range : tuple, optional
        Range of ports to check, by default (50000, 60000)
    max_tries : int, optional
        Numer of times to try to find an open port, by default 100

    Returns
    -------
    int
        An available port.
    """
    for i in range(max_tries):
        port_to_check = random.randint(port_range[0], port_range[1])

        if not is_port_in_use(port_to_check):
            return port_to_check

    raise ValueError("Failed to find an open port")