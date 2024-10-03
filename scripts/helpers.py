"""Helpers for scripts."""

import json
import re
import subprocess
import sys

from const import BRANCH_NAME, GITHUB_PROJECT
from slugify import slugify


def check_dirty_repo():
    """Check if repo is dirty and message user."""
    if subprocess.run(["which", "git"], capture_output=True, check=True).stdout:
        if (
            subprocess.run(
                ["git", "diff", "--stat"],
                check=True,
            ).stdout
            is not None
        ):
            print("Repo is dirty and needs to be committed!")
            sys.exit(1)
    else:
        print(
            "Could not run `git diff --stat` on repo, please run it to determine "
            "whether constants have changed."
        )


def get_registry_location(filename: str) -> str:
    """Get the registry location for the given filename."""
    return (
        f"https://github.com/{GITHUB_PROJECT}/blob/{BRANCH_NAME}/packages/core/"
        f"src/registries/{filename}"
    )


def run_black(file_path: str):
    """Run black on the given file path."""
    if subprocess.run(["which", "black"], capture_output=True, check=True).stdout:
        subprocess.run(
            ["black", file_path],
            check=True,
        )
    else:
        print("Could not run black on new file, please run it to properly format it.")


def get_manually_written_code(file_path: str):
    """Get a list of manually written code from the given file path."""
    existing_const_file = file_path.read_text(encoding="utf-8").splitlines()

    manually_written_code_start_idx = (
        next(
            i
            for i, line in enumerate(existing_const_file)
            if "**END OF AUTOGENERATED CONTENT**" in line
        )
        + 6
    )
    if len(existing_const_file) > manually_written_code_start_idx:
        return [
            line.strip("\n")
            for line in existing_const_file[manually_written_code_start_idx:]
        ]
    return []


def remove_parenthesis(text: str) -> str:
    """Remove text in parenthesis from a string."""
    return re.sub(r"\([^)]*\)", "", text)


def enum_name_format(name: str, should_remove_parenthesis: bool) -> str:
    """Convert sensor/scale name to enum format."""
    if should_remove_parenthesis:
        name = remove_parenthesis(name)
    return slugify(name, separator="_").upper()


def separate_camel_case(my_str: str) -> str:
    """Split a camel case string."""
    if all(char.islower() for char in my_str):
        return my_str.title()
    start_idx = [i for i, e in enumerate(my_str) if e.isupper()] + [len(my_str)]
    start_idx = [0] + start_idx
    return " ".join(my_str[x:y] for x, y in zip(start_idx, start_idx[1:])).title()


def get_json_file(file_path: str):
    """Get a JSON file from the given file path."""
    with open(file_path) as fp:
        return json.load(fp)


def normalize_name(name: str) -> str:
    """Convert a sensor/scale name into a normalized name."""
    return enum_name_format(name, True).replace("_", " ").title()


def format_for_class_name(name: str, suffix: str = "") -> str:
    """Convert sensor/scale name to class name format."""
    return f"{normalize_name(name).replace(' ', '')}{suffix}"
