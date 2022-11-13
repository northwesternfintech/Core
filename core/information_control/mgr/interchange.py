import argparse
import signal
import threading
import time
from typing import Tuple

import zmq


class Interchange:
    """Acts as a broker/manager for information flow."""

    def __init__(self,
                 address: str = '127.0.0.1',
                 pub_sub_ports: Tuple[int, int] = (50001, 50002)):
        """Initializes interchange.

        Parameters
        ----------
        address : str, optional
            Address to reach the interchange, by default '127.0.0.1'
        pub_sub_ports : Tuple[int, int], optional
            Tuple containing the port for publishers to connect to (XSUB port)
            and the port for subscribers to connect to (XPUB port), by 
            default (50001, 50002)
        """
        self._interchange_address = address
        self._xsub_port = pub_sub_ports[0]
        self._xpub_port = pub_sub_ports[1]

        self._context = zmq.Context()

    def _run_pub_sub_proxy(self):
        """Thread function for running proxy for pub-sub model."""
        # Connects to publishers
        self._frontend = self._context.socket(zmq.XSUB)
        self._frontend.setsockopt(zmq.LINGER, 0)
        self._frontend.bind(f"tcp://{self._interchange_address}:{self._xsub_port}")

        # Connects to subscribers
        self._backend = self._context.socket(zmq.XPUB)
        self._backend.setsockopt(zmq.LINGER, 0)

        self._backend.bind(f"tcp://{self._interchange_address}:{self._xpub_port}")

        try:
            zmq.proxy(self._frontend, self._backend)
        except zmq.ContextTerminated:
            self._frontend.close()
            self._backend.close()

    def stop(self):
        """Handles termination of interchange."""
        self._context.term()
        self._proxy_thread.join()

    def _handle_sigterm(self, sig_num, curr_stack_frame):
        self.stop()

    def run(self):
        """Starts all threads to manage information flow"""
        signal.signal(signal.SIGTERM, self._handle_sigterm)

        self._kill_event = threading.Event()
        
        self._proxy_thread = threading.Thread(
            target=self._run_pub_sub_proxy,
            name="RUN_PUB_SUB_PROXY_THREAD"
        )

        self._proxy_thread.start()

        self._proxy_thread.join()


def main():
    i = Interchange("127.0.0.1", (50001, 50002))
    i.run()


def cli_run():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--address", required=False, default='127.0.0.1',
        help="Address of interchange"
    )
    parser.add_argument(
        "--pub_sub_ports", required=False, default=(50001, 50002),
        help="Pair of ports for publishers/subsribers to connect to, "
        "e.g. --pub_sub_ports=50001,50002"
    )
    args = parser.parse_args()

    pub_sub_ports = None
    if isinstance(args.pub_sub_ports, str):
        pub_str, sub_str = args.pub_sub_ports.split(",")
        pub_sub_ports = (int(pub_str), int(sub_str))
    else:
        pub_sub_ports = args.pub_sub_ports

    interchange = Interchange(args.address, pub_sub_ports)
    interchange.run()
