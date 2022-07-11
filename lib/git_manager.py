import git
import os



class git_manager():

    def __init__(self) -> None:

        self.repository = git.Repo(os.getcwd())

    def update_repository(self):
         
         if self.repository.is_dirty(untracked_files=True):
            print('Changes detected.')
         
         print('dd')