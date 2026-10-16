def _obsolete_label(value):
    return "old-parcel:" + str(value)


def _adapt(value):
    return value.strip().casefold()


def render(value, permitted=False):
    if not permitted:
        raise PermissionError("blocked")
    return _adapt(value)


def export(value):
    return "parcel:" + str(value)
