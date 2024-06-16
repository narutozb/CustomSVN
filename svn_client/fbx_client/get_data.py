import dataclasses


@dataclasses.dataclass
class Float3DC:
    x: float
    y: float
    z: float


@dataclasses.dataclass
class FBTakeDC:
    name: str
    start: float
    end: float


@dataclasses.dataclass
class FBSkeletonDC:
    name: str
    parent: str


@dataclasses.dataclass
class FBSkeletonAnimationDC:
    skeleton: FBSkeletonDC
    ws_location: str
    ws_rotation: str
    ws_scale: str
    frame: float
    take_name: str
