from dataclasses import dataclass, field


@dataclass
class Record:
    sumber: str
    jenis: str                 # "artikel", "paten", "preprint", dll.
    judul: str
    tahun: int | None = None
    abstrak: str = ""
    doi: str = ""
    url: str = ""
    venue: str = ""
    penulis: str = ""
    sitasi: int | None = None
    open_access: bool | None = None
    kueri: str = ""
    kategori: list[str] = field(default_factory=list)
    produk: list[str] = field(default_factory=list)
