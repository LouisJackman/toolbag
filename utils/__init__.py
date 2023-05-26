from functools import total_ordering
from typing import NamedTuple


@total_ordering
class SemanticVersion(NamedTuple):
    major: int
    minor: int
    patch: int

    def __lt__(self, other):
        self_tuple = (self.major, self.minor, self.patch)
        other_tuple = (other.major, other.minor, other.patch)
        return self_tuple < other_tuple

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"
