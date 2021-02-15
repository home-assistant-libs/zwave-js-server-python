"""Helper functions for zwave-js-server."""


# Adapted from https://stackoverflow.com/a/19053800
def snake_to_camel_case(snake_str: str) -> str:
    """Convert snake string to camel case."""
    components = snake_str.split("_")
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return f"{components[0]}{''.join(x.title() for x in components[1:])}"
