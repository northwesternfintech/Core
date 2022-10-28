from operator import truediv
import socket
import ssl
from datetime import date, datetime
import pickle
import subprocess
import platform

class Server():
    def __init__(self, name, port, connection, priority):
        self.name = name
        self.port = port
        self.connection = connection.lower()
        self.priority = priority.lower()
        self.history = []
        self.alert = False; # this is for email alerts, probably want to make it slack instead

    # get message with success & date/time when checking connection
    def check_connection(self):
        msg = ""
        success = False
        now = datetime.now()

        try:
            if self.connection == "plain":
                socket.create_connection((self.name, self.port), timeout = 10)
                msg = f"{self.name} is up. On port {self.port} with {self.conenction}"
                success = True
                self.alert = False
            elif self.connection == "ssl":
                ssl.wrap_socket(socket.create_connection((self.name, self.port), timeout = 10))
                msg = f"{self.name} is up. On port {self.port} with {self.conenction}"
                success = True
                self.alert = False
            else:
                if self.ping():
                    msg = f"{self.name} is up. On port {self.port} with {self.conenction}"
                    success = True
                    self.alert = False
        except socket.timeout:
            msg = f"server: {self.name} timeout. On port {self.port}"
        except (ConnectionRefusedError, ConnectionResetError) as e:
            msg = f"server: {self.name} {e}"
        except Exception as e:
            msg = f"Other?: {e}"

        if success == False and self.alert == False:
            # want to send alert or not?
            pass
        self.create_history(msg, success, now)


    def create_history(self, msg, success, now):
        pass


    def ping(self):
        pass


if __name__ == "__main__":
    pass


    

    

