import mmap

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


PAGE_SIZE = 4096

class Record():
    """
    A Record consists of a Record Type and its Data.
    The first 2 bytes represent the Record Type.
    The remaining bytes represent the Data.
    """
    def __init__(self, record: bytes) -> None:
        self._record = record

    @property
    def record_type(self) -> int:
        return int.from_bytes(self._record[:2])

    @property
    def data(self) -> bytes:
        return self._record[2:]

    def __eq__(self, other: 'Record') -> bool:
        return self._record == other._record

    def __ne__(self, other: 'Record') -> bool:
        return self._record != other._record

    def __lt__(self, other: 'Record') -> bool:
        return self._record < other._record

    def __le__(self, other: 'Record') -> bool:
        return self._record <= other._record

    def __gt__(self, other: 'Record') -> bool:
        return self._record > other._record

    def __ge__(self, other: 'Record') -> bool:
        return self._record >= other._record

    def __len__(self) -> int:
        return len(self._record)

    def __getitem__(self, key: int) -> int:
        return self._record[key]

    def __setitem__(self, key: int, value: int) -> None:
        self._record[key] = value

    def __delitem__(self, key: int) -> None:
        del self._record[key]

    def __iter__(self) -> Iterator[int]:
        return iter(self._record)

    def __contains__(self, item: int) -> bool:
        return item in self._record

    def __reversed__(self) -> Iterator[int]:
        return reversed(self._record)

    def __add__(self, other: 'Record') -> 'Record':
        return Record(self._record + other._record)

    def __radd__(self, other: 'Record') -> 'Record':
        return Record(other._record + self._record)

    def __iadd__(self, other: 'Record') -> '

class DB_Page():
    """
    A DB_Page consists of PAGE_SIZE bytes.
    It contains a memory mapped page of the database.

    The first 24 bytes represent the Page Header.
    The last 8 bytes represent the Page Trailer.
    The Line Index comes just before the Page Trailer,
    and consists Line Index Entries for each Record on the Page.
    The Records come just after the Page Header, and are kept contiguous.
    The rest of the Page is known as the Free Space.
    """

    class PageHeader:
        """
        The Page Header consists of 24 bytes.
        The first 4 bytes contain the Page Number.
        The next 4 bytes represent the Calc First Pointer.
        The next 4 bytes represent the Calc Last Pointer.
        The next 2 bytes record the available Free Space.
        The next 2 bytes is a Write Switch for use by the DBMS.
        The remaining 8 bytes are reserved.
        """

        def __init__(self, header: bytes) -> None:
            self._header = header

        @property
        def page_number(self) -> int:
            return int.from_bytes(self._header[:4])

        @property
        def calc_first(self) -> Pointer:
            return Pointer.from_bytes(self._header[4:8])

        @property
        def calc_last(self) -> Pointer:
            return Pointer.from_bytes(self._header[8:12])

        @property
        def available_space(self) -> int:
            return int.from_bytes(self._header[12:14])

    class PageTrailer():
        """
        The Page Trailer consists of 8 bytes.
        The first byte is the count of Line Index Entries.
        The last 4 bytes contain the Page Number which should
        be the same as the Page Number in the Page Header.
        """

            def __init__(self, trailer: bytes) -> None:
                self._trailer = trailer

            @property
            def line_index_count(self) -> int:
                return self._trailer[0]

            @property
            def page_number(self) -> int:
                return int.from_bytes(self._trailer[4:])

    class LineIndex(size: int):
        """
        The Line Index consists of size Line Index Entries
        stored just before the Page Trailer in reverse list order.
        """

        class LineIndexEntry():
            """
            A Line Index Entry consists of 8 bytes used to locate a line on the page
            containing a Record.
            The first 2 bytes represent the Record Type indexed.
            The next 2 bytes represent the offset on the page of the line.
            The next 2 bytes represent the length of the line.
            The last 2 bytes represents the size of the pointers at the start of the line.
            """
                def __init__(self, entry: bytes) -> None:
                    self._entry = entry

                @property
                def record_type(self) -> int:
                    return int.from_bytes(self._entry[:2])

                @property
                def offset(self) -> int:
                    return int.from_bytes(self._entry[2:4])

                @property
                def length(self) -> int:
                    return int.from_bytes(self._entry[4:6])

                @property
                def pointer_size(self) -> int:
                    return int.from_bytes(self._entry[6:])

        def __init__(self, contents: bytes) -> None:
            self._entries = [self.LineIndexEntry(contents[-(i+8):-i])
                              for i in range(len(contents), 0, -8)]

        class Line():
            """
            A Line consists of a Record of a given type and its Pointers.
            The first pointer_count * 4 bytes represent the Pointers.
            The remaining bytes represent the Record.
            """
            def __init__(self, record_type: int, line: bytes, pointer_count: int) -> None:
                self._record_type = record_type
                self._line = line
                self._pointer_count = pointer_count

            @property
            def pointers(self) -> List[Pointer]:
                return [Pointer.from_bytes(self._line[4*i:4*(i+1)])
                        for i in range(self._pointer_count)]

            @property
            def record(self) -> Record:
                return Record(self._record_type, self._line[4*self._pointer_count:])


    def __init__(self, page: mmap.mmap) -> None:
        self._page = page
        self._page_header = self.PageHeader(self._page[:24])
        self._page_trailer = self.PageTrailer(self._page[-8:])
        assert self._page_header.page_number == self._page_trailer.page_number
        entry_count = self._page_trailer.line_index_count
        self._line_index = self.LineIndex(self.page[-8 * (entry_count + 1): -8])
        self._records = [self.Line(entry.record_type, self._page[entry.offset:entry.offset + entry.length],
                               entry.pointer_size)
                         for entry in self._line_index]

    def __getitem__(self, key: int) -> Record:
        return self._records[key]

    def __setitem__(self, key: int, value: Record) -> None:
        self._records[key] = value

    def __delitem__(self, key: int) -> None:
        del self._records[key]

    def __iter__(self) -> Iterator[Record]:
        return iter(self._records)

    def __len__(self) -> int:
        return len(self._records)

    def __contains__(self, item: Record) -> bool:
        return item in self._records
