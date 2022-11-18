import cement
import requests
import subprocess

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


class BaseController(cement.Controller):
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
        cmd = (
            "manager_server "
        )

        subprocess.Popen(cmd.split(), shell=False,
                         start_new_session=True)

    @cement.ex()
    def shutdown(self) -> None:
        """Shutsdown manager server"""
        path = f"{self.app.server_address}/shutdown"
        res = requests.post(path)

        if res.status_code != 200:
            print(f"Error: {res.text}")
            return

        print("Successfully shutdown server")

