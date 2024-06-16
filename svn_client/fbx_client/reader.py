import fbx
import FbxCommon


class CustomFbxReader:

    def __init__(self):
        """
        自定义打开fbx文件类
        """
        self.sdk_manager, self.scene = FbxCommon.InitializeSdkObjects()
        self.__file_path = None

    def load_scene(self, file_path: str):
        self.__file_path = file_path
        return FbxCommon.LoadScene(self.sdk_manager, self.scene, file_path)

    def get_frame_rate(self):
        time_mode = self.scene.GetGlobalSettings().GetTimeMode()
        # 获取该时间模式的帧率
        return fbx.FbxTime.GetFrameRate(time_mode)

    @classmethod
    def get_all_takes(cls, scene: fbx.FbxScene):
        takes = []
        anim_stack_count = scene.GetSrcObjectCount(fbx.FbxCriteria.ObjectType(fbx.FbxAnimStack.ClassId))
        for i in range(anim_stack_count):
            anim_stack = scene.GetSrcObject(fbx.FbxCriteria.ObjectType(fbx.FbxAnimStack.ClassId), i)
            takes.append(anim_stack)
        return takes
