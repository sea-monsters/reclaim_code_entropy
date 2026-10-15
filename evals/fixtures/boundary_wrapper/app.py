"""render owns authorization; denied requests must not touch the input."""


def _forward(value):
    return value.strip().casefold()


def render(value, authorized=False):
    if not authorized:
        raise PermissionError("denied")
    return _forward(value)
