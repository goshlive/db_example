# uow.py
class UnitOfWork:
    """
    Simple UnitOfWork context manager.
    Usage:
        with UnitOfWork(SessionFactory) as session:
            repo = AccountRepository(session)
            repo.transfer(...)
    Commit happens when context exits without exception; otherwise rollback.
    """
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session = None

    def __enter__(self):
        self.session = self.session_factory()
        return self.session  # callers will create repos with this session

    def __exit__(self, exc_type, exc, tb):
        try:
            if exc_type is None:
                self.session.commit()
            else:
                # something happened: rollback
                self.session.rollback()
        finally:
            self.session.close()
        # Do not suppress exceptions: return False
        return False
