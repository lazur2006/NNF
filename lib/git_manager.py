import os
from git import Repo
import git
import subprocess

repository = 'https://github.com/lazur2006/NNF.git'
branch = 'main'

class git_manager():

    def __init__(self) -> None:
        self.repository = git.Repo(os.getcwd())
    
    def update_repository(self):
        try:
            Repo.clone_from(repository, '', branch=branch)
        except:
            self.repository.remotes.origin.pull()
        self.__restart_server()

    def update_available(self):
        self.repository.remotes.origin.fetch()
        if(self.repository.git.diff('origin/main') != ''):
            return({'update_is_available':True,'diff':self.repository.git.diff('origin/main')})
        else:
            return({'update_is_available':False,'diff':''})

    def __restart_server(self):
        subprocess.check_output("sudo systemctl restart my-server --now", shell=True)