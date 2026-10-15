"""Private module; only render is a supported entrypoint. No dynamic loading."""


def _legacy_format(value):
    return "old:" + str(value)


def render(value):
    return "current:" + str(value)
