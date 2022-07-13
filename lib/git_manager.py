import os
from git import Repo
from git import Git
import git


class git_manager():

    def __init__(self) -> None:

        # Repo.clone_from('https://github.com/lazur2006/NNF.git', 'test', branch='main')
        # git_ssh_identity_file = os.path.expanduser('id_rsa')
        # #git_ssh_identity_file = os.path.expanduser('git')
        # git_ssh_cmd = 'ssh -i %s' % git_ssh_identity_file


        try:
            print('START :: try to clone the git')
            Repo.clone_from('https://github.com/lazur2006/NNF.git', '../test', branch='main')
        except:
            self.repository = git.Repo(os.getcwd() + '/../test')
            self.repository.remotes.origin.pull()
        print('END')