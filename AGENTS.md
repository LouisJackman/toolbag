# Toolbag — AI Coding Agent Instructions

This file provides guidance to AI coding agents when working with code in this repository.

## Project Overview

A collection of standalone Python 3 scripts (minimum Python 3.9) for DevOps and system administration tasks. No build system, package manager, or external dependencies — standard library only.

## Running Scripts

Scripts are executable and self-documenting via `--help`:

```sh
python3 <script-name> --help
./clean-old-container-images --help
```

Each script uses `argparse` and exposes its module docstring as the usage description.

## Adding Linting and Type Checking

No linting or type-checking is configured. To add:

```sh
uv tool run ruff check .
uv tool run mypy --strict .
```

## Architecture

### Shared Utilities (`utils/__init__.py`)

Two shared constructs used across scripts:

- **`SemanticVersion`** — A `NamedTuple` (`major`, `minor`, `patch`) with a `parse(tag)` classmethod that parses Docker image tags (e.g. `my-image:1.2.3` → `SemanticVersion(1, 2, 3)`). Used to identify and compare versioned container images.
- **`docker()`** — Thin subprocess wrapper around the `docker` CLI that returns decoded stdout. Used by container management scripts.

### Script Patterns

Each script follows the same structure:
1. Module docstring (becomes CLI description)
2. `argparse` setup in `main()`
3. Delegation to functions that call external tools via `subprocess`

### External Tool Dependencies Per Script

| Script | Requires |
|---|---|
| `clean-old-container-images` | `docker` |
| `clean-old-container-images-from-registry` | `docker`, `reg` |
| `clean-old-local-k8s-images` | `docker` |
| `get-temperature` | Linux `/sys/class/thermal/` (Linux only) |
| `locate-local-ssh` | `nmap` |
| `start-ec2-instance` | `aws` CLI |

## Repository Hosting

GitLab (`gitlab.com/louis.jackman/toolbag`) is the canonical source; GitHub is a read-only mirror.
