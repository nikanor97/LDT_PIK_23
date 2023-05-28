from decimal import Decimal


def entities_with_coordinates(msp) -> dict[str, tuple[Decimal, Decimal]]:
    group = msp.groupby(dxfattrib="layer")
    sanitizing_stuff: dict[str, tuple[Decimal, Decimal]] = {}
    for layer, entities in group.items():
        if layer == "P-SANR-FIXT":
            for entity in entities:
                sanitizing_stuff[entity.dxf.name] = tuple(entity.dxf.insert.vec2)
    return sanitizing_stuff


# doc = ezdxf.readfile(
#     "./СТМ8-1П-Б-2.dxf"
# )
# modelspace = doc.modelspace()
# stuffs = entities_with_coordinates(msp)
