import os
import shutil
from functools import cache
from subprocess import CompletedProcess, run
from typing import Any, NamedTuple


class SemanticVersion(NamedTuple):
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


@cache
def container_runtime() -> str:
    """The container CLI to use: $CONTAINER_RUNTIME, else podman, else docker."""
    if explicit := os.environ.get("CONTAINER_RUNTIME"):
        return explicit
    for candidate in ("podman", "docker"):
        if shutil.which(candidate):
            return candidate
    raise RuntimeError(
        "no container runtime found (podman or docker); set CONTAINER_RUNTIME"
    )


def container(*args: str, **kwargs: Any) -> CompletedProcess[Any]:
    """Run ``<runtime> args...``, forwarding keyword arguments to subprocess.run."""
    return run([container_runtime(), *args], check=True, **kwargs)
