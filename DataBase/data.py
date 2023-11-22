class Pointer:
    """ A Pointer consists of 32 bits.
    The first bit is reserved.
    The next 23 bits represent the Page Number.
    The remaining 8 bits represent the Line Number.
    """
    def __init__(self, page: int = 0, line: int = 0) -> None:
        self._pointer: bytes = page.to_bytes(length=3) + line.to_bytes(length=1)

    @property
    def page(self) -> int:
        return int.from_bytes(self._pointer[:3])

    @property
    def line(self) -> int:
        return self._pointer[-1]

    def __str__(self) -> str:
        return f"{self.page}:{self.line}"

    def __repr__(self) -> str:
        return f'pointer({self.page}, {self.line})'

    def __eq__(self, other: 'Pointer') -> bool:
        return self._pointer == other._pointer
