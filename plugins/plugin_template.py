from abc import ABC, abstractmethod

class BasePlugin(ABC):
    def __init__(self):
        self.name = self.__class__.__name__

    @abstractmethod
    def get_commands(self):
        """Return list of supported commands"""
        pass

    @abstractmethod
    def execute(self, command, args):
        """Execute the plugin command"""
        pass

    @abstractmethod
    def help(self):
        """Return plugin help information"""
        pass
