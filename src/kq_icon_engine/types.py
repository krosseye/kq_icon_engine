from enum import Enum, StrEnum, auto


class FillMode(Enum):
    """Fill rendering mode."""

    FLAT = auto()
    GRADIENT = auto()


class IconStyle(StrEnum):
    """Style variant for icons."""

    REGULAR = auto()
    THIN = auto()
    LIGHT = auto()
    BOLD = auto()
    FILL = auto()
    DUOTONE = auto()
