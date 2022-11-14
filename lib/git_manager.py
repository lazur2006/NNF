import os
from git import Repo
import git
import subprocess
from sys import platform
import requests

import re

repository = 'https://github.com/lazur2006/NNF.git'
branch = 'unstable_beta_2_0_0'
# unstable_alpha_dev_2_0_1 unstable_beta_2_0_0
# abc

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
            if(self.repository.git.diff(f'origin/{branch}') != ''):
                return({'update_is_available':True,'diff':self.repository.git.diff(f'origin/{branch}'),'notes':self.get_commit_history()})
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
            return(True)
        elif platform == "win32":
            # Windows...
            return(False)

    def get_commit_history(self):
        url = f"https://api.github.com/repos/lazur2006/NNF/commits?sha={branch}"
        response = requests.request("GET", url).json()
        results = []
        title = []
        features = []
        for e in response:
            # if e.get('sha') == self.get_repo_head_sha():
            #     break
            # else:
            msg = repr(e.get('commit').get('message'))
            

            regex = r"([^\\]*\s*)(\\n\\n|\\r\\n)([^\\]*\s*)"
            #test_str = "Upgrade\\n\\n#1 Upgrade to newer Version available!\\r\\n# Bug fixed\\r\\n# Bla bla"
            try:
                title.append([e.group(1) for e in re.finditer(regex, msg, re.MULTILINE)][0])
            except:
                pass
            f = [e.group(3) for e in re.finditer(regex, msg, re.MULTILINE)]
            if f:
                features.append(f)
            else:
                features.append(msg)

        return(results)

    def get_repo_head_sha(self):
        return(self.repository.head.object.hexsha)
