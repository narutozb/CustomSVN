import dataclasses


@dataclasses.dataclass
class SVNFileSimpleDC:
    revision: int = None
    local_path: str = None
    url: str = None

    def __eq__(self, other):
        return self.url == other.url and self.revision == other.revision


@dataclasses.dataclass
class SVNChangedFileDC(SVNFileSimpleDC):
    change_type: str = None


