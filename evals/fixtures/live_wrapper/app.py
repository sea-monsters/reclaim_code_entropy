"""render is a supported public entrypoint; the helper is private."""


def _forward(value):
    return value.strip().casefold()


def render(value):
    return _forward(value)
