import os
from git import Repo
import git
import subprocess
from sys import platform

repository = 'https://github.com/lazur2006/NNF.git'
branch = 'main_v2'

class git_manager():

    def __init__(self) -> None:
        self.repository = git.Repo(os.getcwd())
    
    def update_repository(self):
        if self.__allow_update_by_os_type():
            try:
                self.repository.git.checkout(branch)
                Repo.clone_from(repository, '', branch=branch)
            except:
                self.repository.remotes.origin.pull()
            self.__restart_server()
        else:
            pass

    def update_available(self):
        if self.__allow_update_by_os_type():
            self.repository.remotes.origin.fetch()
            if(self.repository.git.diff('origin/main_v2') != ''):
                return({'update_is_available':True,'diff':self.repository.git.diff('origin/main_v2')})
            else:
                return({'update_is_available':False,'diff':''})
        else:
            return({'update_is_available':False,'diff':'OS: unix isn''t used'})

    def __restart_server(self):
        subprocess.check_output("sudo systemctl restart my-server --now", shell=True)

    def __allow_update_by_os_type(self):
        if platform == "linux" or platform == "linux2":
            # linux
            return(True)
        elif platform == "darwin":
            # OS X
            return(False)
        elif platform == "win32":
            # Windows...
            return(False)
