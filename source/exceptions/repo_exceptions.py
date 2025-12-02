class RepoError(Exception):
    pass

class DeleteIsNotActive(RepoError):
    pass

class RevertDeleteIsActive(RepoError):
    pass

class UpdateIsNotActive(RepoError):
    pass