import dataclasses

import fbx

from fbx_client._dc import FBSkeletonDC
from fbx_client.custom_layer import CustomLayer
from fbx_client.custom_skeleton import CustomFBSkeletonUtils
from fbx_client_config import FBXClientConfig


class DataManager:
    def __init__(self, scene: fbx.FbxScene):
        self.scene = scene

    def get_scene_data(self):
        print(FBXClientConfig.version)
        return {
            'fps': self._get_fps(),
            'client_version': FBXClientConfig.version,
        }

    def get_takes(self):
        return [dataclasses.asdict(i) for i in CustomLayer.get_all_takes_custom_data(self.scene)]

    def _get_fps(self):
        # 获取场景的时间模式
        time_mode = self.scene.GetGlobalSettings().GetTimeMode()
        # 获取该时间模式的帧率
        frame_rate = fbx.FbxTime.GetFrameRate(time_mode)
        return frame_rate

    def get_skeletons(self):
        return [FBSkeletonDC(_.GetName(), _.GetParent().GetName()) for _ in
                CustomFBSkeletonUtils.get_fbx_node_attributes(self.scene)]
