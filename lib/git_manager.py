import git
import os



class git_manager():

    def __init__(self) -> None:

        self.repository = git.Repo(os.getcwd())

    def update_repository(self):
        # check if any changes appeared to working copy
        if self.repository.is_dirty(untracked_files=True):
            print('Changes detected.')

        # Pull from remote repo
        print(self.repository.remotes.origin.pull())
         
        print('dd')