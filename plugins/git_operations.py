import git
from plugins.plugin_template import BasePlugin

class GitOperations(BasePlugin):
    def __init__(self):
        super().__init__()
        self.repo = None
        
    def initialize_repo(self, path: str):
        try:
            self.repo = git.Repo(path)
        except git.InvalidGitRepositoryError:
            return "Not a valid git repository"
            
    def get_commands(self):
        return {
            "status": self.get_status,
            "commit": self.commit_changes,
            "push": self.push_changes,
            "pull": self.pull_changes,
            "branch": self.branch_operations
        }
        
    def get_status(self):
        if not self.repo:
            return "Repository not initialized"
        return self.repo.git.status()
        
    def commit_changes(self, message: str):
        if not self.repo:
            return "Repository not initialized"
        try:
            self.repo.index.add('*')
            self.repo.index.commit(message)
            return "Changes committed successfully"
        except Exception as e:
            return f"Error committing changes: {str(e)}"
            
    def execute(self, command: str, args: dict):
        cmd = self.get_commands().get(command)
        if cmd:
            return cmd(**args)
        return "Command not found"
        
    def help(self):
        return """
        Git Operations Available:
        - status: Show repository status
        - commit <message>: Commit changes
        - push: Push changes to remote
        - pull: Pull changes from remote
        - branch <operation>: Branch operations
        """
