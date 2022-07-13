import os
from git import Repo
from git import Git
import git


class git_manager():

    def __init__(self) -> None:

        self.repository = git.Repo(os.getcwd())

        self.handle_repository()

    
    def handle_repository(self):
        print('Before: ' + str(self.update_available()))

        try:
            Repo.clone_from('https://github.com/lazur2006/NNF.git', '', branch='main')
        except:
            self.repository.remotes.origin.pull()

        print('After: ' + str(self.update_available()))

        print('')

    def update_available(self):
        self.repository.remotes.origin.fetch()
        if(self.repository.git.diff('origin/main') != ''):
            return(True)
        else:
            return(False)