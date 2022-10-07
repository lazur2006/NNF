import os
from git import Repo
import git
import subprocess
from sys import platform

repository = 'https://github.com/lazur2006/NNF.git'
branch = 'unstable_beta_2_0_0'

class git_manager():

    def __init__(self) -> None:
        self.repository = git.Repo(os.getcwd())
        self.repository.git.checkout('main')
        
    def update_repository(self):
        if self.__allow_update_by_os_type():
            try:
                Repo.clone_from(repository, '', branch=branch)
            except:
                self.repository.remotes.origin.pull()
            self.__restart_server()
        else:
            pass

    def update_available(self):
        if self.__allow_update_by_os_type():
            self.repository.remotes.origin.fetch()
            if(self.repository.git.diff('origin/unstable_beta_2_0_0') != ''):
                return({'update_is_available':True,'diff':self.repository.git.diff('origin/unstable_beta_2_0_0')})
            else:
                return({'update_is_available':False,'diff':''})
        else:
            return({'update_is_available':False,'diff':'OS: unix isn''t used'})

    def __restart_server(self):
        subprocess.check_output("sudo systemctl restart my-server --now", shell=True)
        #print('restart')

    def __allow_update_by_os_type(self):
        if platform == "linux" or platform == "linux2":
            # linux
            return(True)
        elif platform == "darwin":
            # OS X - for debugging -
            return(False)
        elif platform == "win32":
            # Windows...
            return(False)
