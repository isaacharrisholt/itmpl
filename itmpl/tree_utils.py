import shutil
from pathlib import Path
from typing import Callable, Optional


def find_duplicates(
    source: Path,
    destination: Path,
    ignore: Optional[Callable[[Path], bool]] = None,
):
    """Find all the files in the destination directory that are present in the
    source directory. Unlike shutil.copytree, this function will not overwrite
    existing files and will create the destination directory if it does not
    exist.
    """
    ignore = ignore or (lambda p: False)

    for item in source.iterdir():
        if ignore(item):
            # Item is ignored
            continue
        elif not (destination / item.name).exists():
            # Item does not exist in destination
            continue
        elif item.is_dir():
            # Item is a directory, so recurse
            yield from find_duplicates(item, destination / item.name)
        elif (destination / item.name).exists():
            # Item is a file and exists in destination
            yield destination / item.name


def copy_tree(
    source: Path,
    destination: Path,
    ignore: Optional[Callable[[Path], bool]] = None,
):
    """Copy a tree of files from source to destination. Unlike shutil.copytree,
    this function will not overwrite existing files and will create the
    destination directory if it does not exist.
    """
    ignore = ignore or (lambda p: False)

    for item in source.iterdir():
        if ignore(item):
            continue
        elif item.is_dir():
            copy_tree(item, destination / item.name)
        else:
            destination.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, destination / item.name)


def recursive_delete(directory: Path, glob: str) -> None:
    """Delete all files in a directory matching a glob."""
    for file in directory.rglob(glob):
        if file.is_file():
            file.unlink()
        else:
            shutil.rmtree(file)
