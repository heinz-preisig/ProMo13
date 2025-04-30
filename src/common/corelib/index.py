import attrs


@attrs.define
class Index:
    identifier: str
    iri: str = ""
    label: str = ""
    network: list[str] = attrs.Factory(list)
    aliases: dict[str, str] = attrs.Factory(dict)
