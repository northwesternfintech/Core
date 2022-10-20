import cement

# TODO: Make ascii art banner
BANNER = """

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