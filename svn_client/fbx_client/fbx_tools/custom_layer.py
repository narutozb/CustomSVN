import fbx

from fbx_client.fbx_tools._dc import CustomTakeDC


class CustomLayer:

    @classmethod
    def get_all_takes_custom_data(cls, scene: fbx.FbxScene):
        takes: list[CustomTakeDC] = []
        anim_stack_count = scene.GetSrcObjectCount(fbx.FbxCriteria.ObjectType(fbx.FbxAnimStack.ClassId))
        # 获取场景的时间模式
        time_mode = scene.GetGlobalSettings().GetTimeMode()
        # 获取该时间模式的帧率
        frame_rate = fbx.FbxTime.GetFrameRate(time_mode)
        for i in range(anim_stack_count):
            anim_stack = scene.GetSrcObject(fbx.FbxCriteria.ObjectType(fbx.FbxAnimStack.ClassId), i)
            # print(anim_stack.GetName())
            custom_take = CustomTakeDC(
                name=anim_stack.GetName(),
                start_frame=anim_stack.GetLocalTimeSpan().GetStart().GetSecondDouble() * frame_rate,
                end_frame=anim_stack.GetLocalTimeSpan().GetStop().GetSecondDouble() * frame_rate,
            )
            takes.append(custom_take)

        return takes
