import dataclasses

import fbx


@dataclasses.dataclass
class CustomTakeDC:
    name: str
    start_frame: float
    end_frame: float


@dataclasses.dataclass
class CustomSkeletonDC:
    name: str
    parent: str


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


@dataclasses.dataclass
class CustomFloat3DC:
    x: float
    y: float
    z: float

    @classmethod
    def convert_fbx_vec4_to_f3(cls, fbx_v4: fbx.FbxVector4):
        return CustomFloat3DC(
            fbx_v4[0],
            fbx_v4[1],
            fbx_v4[2],
        )


@dataclasses.dataclass
class CustomFloat4DC:
    x: float
    y: float
    z: float
    a: float

    @classmethod
    def convert_fbx_vec4_to_f4(cls, fbx_v4: fbx.FbxVector4):
        return CustomFloat4DC(
            fbx_v4[0],
            fbx_v4[1],
            fbx_v4[2],
            fbx_v4[3],
        )


@dataclasses.dataclass
class CustomFBSkeletonAttributesDC:
    name: str
    lcl_location: CustomFloat3DC
    lcl_rotation: CustomFloat3DC
    lcl_scale: CustomFloat3DC
    ws_location: CustomFloat3DC
    ws_rotation: CustomFloat3DC
    ws_scale: CustomFloat3DC
    frame: float
    take_name: str
    parent: str = None
