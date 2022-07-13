import os
from git import Repo
from git import Git
import git


class git_manager():

    def __init__(self) -> None:

        git_ssh_identity_file = os.path.expanduser('id_rsa')
        #git_ssh_identity_file = os.path.expanduser('git')
        git_ssh_cmd = 'ssh -i %s' % git_ssh_identity_file

        with Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
            try:
                Repo.clone_from('git@github.com:lazur2006/NNF_releases.git', 'test', branch='main')
            except:
                self.repository = git.Repo(os.getcwd() + '/test')
                self.repository.remotes.origin.pull()