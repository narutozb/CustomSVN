import dataclasses


@dataclasses.dataclass
class TableFieldsSettings:
    key: str
    label: str
    sortable: bool
    editable: bool


@dataclasses.dataclass
class EditFieldsSettings:
    key: str
    label: str
    typ: str
    required: bool
