class Pointer:
    """ A Pointer consists of 32 bits.
    The first bit is reserved.
    The next 23 bits represent the Page Number.
    The remaining 8 bits represent the Line Number.
    """
    def __init__(self, page: int = 0, line: int = 0) -> None:
        if page > 8388607 or page < 0:
            raise ValueError('Page number must be positive and less than 8388607')
        if line > 255 or line < 0:
            raise ValueError('Line number must be positive and less than 255')
        self._pointer: bytes = page.to_bytes(length=3) + line.to_bytes(length=1)

    @staticmethod
    def from_bytes(chars: bytes) -> 'Pointer':
        """
        Alternative constructor for Pointer.
        :param chars: 4 bytes representing a Pointer.
        :return: Pointer object.
        :raises ValueError: If the input is not 4 bytes long.
        """
        if len(chars) != 4:
            raise ValueError('Pointer must be 4 bytes long')
        new_pointer = Pointer() # blank pointer
        new_pointer._pointer = chars # inject the bytes into the blank pointer
        return new_pointer

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
