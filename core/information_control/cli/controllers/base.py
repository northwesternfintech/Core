import cement
import requests
import subprocess
from ...mgr.utils import find_open_ports
from ...mgr.utils import print_cli_error
from cement.ext.ext_argparse import ArgparseArgumentHandler

# TODO: Make ascii art banner
BANNER = r"""

 ________   ___  ___  ________ _________   
|\   ___  \|\  \|\  \|\  _____\\___   ___\ 
\ \  \\ \  \ \  \\\  \ \  \__/\|___ \  \_| 
 \ \  \\ \  \ \  \\\  \ \   __\    \ \  \  
  \ \  \\ \  \ \  \\\  \ \  \_|     \ \  \ 
   \ \__\\ \__\ \_______\ \__\       \ \__\
    \|__| \|__|\|_______|\|__|        \|__|
                                           
                                           
                                           

NUFT
An interactive platform for using NUFT Core
Docs:
"""

__all__ = ['BaseController']


class BaseParser(ArgparseArgumentHandler):
    class Meta:
        ignore_unknown_arguments = True


class BaseController(cement.Controller, BaseParser):
    class Meta:
        label = 'base'
        description = 'An interactive platform for using NUFT Core'
        arguments = [
            (['--version'], {'action': 'version', 'version': BANNER})
        ]

    def default(self) -> None:
        self.app.args.print_help()

    @cement.ex()
    def start(self) -> None:
        """Starts manager server"""
        config_dict = self.app.config

        server_host = config_dict['server']['host']
        server_port = find_open_ports(1)[0]
        config_dict['server']['port'] = str(server_port)

        manager_path = self.app.nuft_dir

        interchange_host = config_dict['interchange']['host']
        interchange_pub_port, interchange_sub_port = list(map(str, find_open_ports(2)))
        config_dict['interchange']['pub_port'] = interchange_pub_port
        config_dict['interchange']['sub_port'] = interchange_sub_port
        

        cmd = (
            "manager_server "
            f"--server-address {server_host} "
            f"--server-port {server_port} "
            f"--manager-path {manager_path} "
            f"--interchange-address {interchange_host} "
            f"--interchange-pub-port {interchange_pub_port} "
            f"--interchange-sub-port {interchange_sub_port} "
        )

        try:
            subprocess.Popen(cmd.split(), shell=False,
                             start_new_session=True)
        except Exception as e:
            print_cli_error(f"Failed to start server: {e}")
            return

        self.app.server_address = f"http://{server_host}:{server_port}"

        with open(self.app.conf_path, 'w') as f:
            self.app.config.write(f)

    @cement.ex()
    def shutdown(self) -> None:
        """Shutsdown manager server"""
        if self.app.server_address is None:
            colored("Error: Server not running!")
            return

        path = f"{self.app.server_address}/shutdown"
        res = requests.post(path)

        if res.status_code != 200:
            print_cli_error(res.text)
            return

        print("Successfully shutdown server")

