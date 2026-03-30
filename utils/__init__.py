from typing import NamedTuple
from subprocess import run


class SemanticVersion(NamedTuple):
    major: int
    minor: int
    patch: int

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"


def docker(*args, **kwargs):
    return run(["docker", *args], check=True, **kwargs)
