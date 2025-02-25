from typing import Protocol

import attrs


class IOManager(Protocol):
    pass


@attrs.define
class DefaultIOManager:
    pass
