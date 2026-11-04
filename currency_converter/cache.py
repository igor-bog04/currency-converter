"""JSON cache for persisting the last successful rate snapshot."""


class RateCache:
    def __init__(self, path=None):
        raise NotImplementedError

    def save(self, snapshot):
        raise NotImplementedError

    def load(self):
        raise NotImplementedError
