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
    """The container CLI: $CONTAINER_ENGINE, then podman, then docker."""
    if explicit := os.environ.get("CONTAINER_ENGINE"):
        if shutil.which(explicit):
            return explicit
        raise RuntimeError(f"CONTAINER_ENGINE is not executable: {explicit}")
    for candidate in ("podman", "docker"):
        if shutil.which(candidate):
            return candidate
    raise RuntimeError(
        "no container runtime found; install podman or docker, or set CONTAINER_ENGINE"
    )


def container(*args: str, **kwargs: Any) -> CompletedProcess[Any]:
    """Run ``<runtime> args...``, forwarding keyword arguments to subprocess.run."""
    return run([container_runtime(), *args], check=True, **kwargs)
