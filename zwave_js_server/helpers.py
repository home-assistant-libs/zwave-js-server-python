"""Helper functions for zwave-js-server."""
import re

# Adapted from https://rodic.fr/blog/camelcase-and-snake_case-strings-conversion-with-python/
SNAKE_TO_CAMEL_PATTERN = re.compile(r"_([a-z])")
CAMEL_TO_SNAKE_PATTERN = re.compile(r"[A-Z]")


def snake_to_camel_case(snake_str: str) -> str:
    """Convert snake string to camel case."""
    return SNAKE_TO_CAMEL_PATTERN.sub(lambda x: x.group(1).upper(), snake_str)


def camel_case_to_snake(camel_case_str: str) -> str:
    """Convert camel case string to snake."""
    return CAMEL_TO_SNAKE_PATTERN.sub(
        lambda x: "_" + x.group(0).lower(), camel_case_str
    )
