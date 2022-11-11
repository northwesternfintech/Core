import cement

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