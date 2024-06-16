import fbx

from fbx_client._dc import CustomFBSkeletonAttributesDC, CustomFloat3DC
from fbx_client.reader import CustomFbxReader


class CustomFBSkeletonUtils:

    @classmethod
    def get_fbx_node_attributes(cls, scene: fbx.FbxScene):
        '''

        :param scene:
        :param typ:
        FbxNodeAttribute.EType.eMarker
        FbxNodeAttribute.EType.eSkeleton
        FbxNodeAttribute.EType.eMesh
        FbxNodeAttribute.EType.eNurbs
        FbxNodeAttribute.EType.ePatch
        FbxNodeAttribute.EType.eCamera
        FbxNodeAttribute.EType.eLight
        :return:
        '''

        def traverse(node, ):
            '''
            Traverse node and all its children
            :param node: FbxNode object
            :return: List of FBBox objects
            '''
            boxes = []
            if node.GetNodeAttribute() is not None:
                boxes.append(node)

            for i in range(node.GetChildCount()):
                boxes.extend(traverse(node.GetChild(i)))
            return boxes

        root_node = scene.GetRootNode()
        return traverse(root_node)


class CustomFBModelSkeleton():
    def __init__(self, fb_box):
        self.fb_box: fbx.FbxNode = fb_box

    def get_local_location(self):
        return self.fb_box.LclTranslation

    def get_world_transform(self, time=fbx.FbxTime(0)) -> fbx.FbxAMatrix:
        return self.fb_box.EvaluateGlobalTransform(time)

    def get_local_rotation(self):
        return self.fb_box.LclRotation

    def get_local_scale(self):
        return self.fb_box.LclScaling

    def get_local_transform(self, time=fbx.FbxTime(0)):
        return self.fb_box.EvaluateLocalTransform(time)

    def get_custom_attributes_by_anim_stack(self, anim_stack: fbx.FbxAnimStack, time=fbx.FbxTime(0)):

        return CustomFBSkeletonAttributesDC(
            name=self.fb_box.GetName(),
            lcl_location=CustomFloat3DC.convert_fbx_vec4_to_f3(self.get_local_transform(time).GetT()),
            lcl_rotation=CustomFloat3DC.convert_fbx_vec4_to_f3(self.get_local_transform(time).GetR()),
            lcl_scale=CustomFloat3DC.convert_fbx_vec4_to_f3(self.get_local_transform(time).GetS()),
            ws_location=CustomFloat3DC.convert_fbx_vec4_to_f3(self.get_world_transform(time).GetT()),
            ws_rotation=CustomFloat3DC.convert_fbx_vec4_to_f3(self.get_world_transform(time).GetR()),
            ws_scale=CustomFloat3DC.convert_fbx_vec4_to_f3(self.get_world_transform(time).GetS()),
            frame=time.GetSecondDouble(),
            take_name=anim_stack.GetName(),
            parent=self.fb_box.GetParent().GetName() if self.fb_box.GetParent() else None
        )

    def __get_anim_curve(self, anim_stack, channel):
        """
        获取特定FbxNode的动画曲线
        :param anim_stack: FbxAnimStack对象
        :param channel: 通道名称，例如"LclTranslation"
        :return: FbxAnimCurve对象
        """
        node = self.fb_box
        # 获取FbxAnimLayer

        anim_layer = anim_stack.GetMember(fbx.FbxAnimLayer.ClassId, 0)

        # 获取FbxProperty
        prop = node.FindProperty(channel)

        # 获取FbxAnimCurve
        anim_curve = prop.GetCurve(anim_layer, channel)

        return anim_curve

    def get_transform_by_take(self, fb_box, take_name, frame, scene):
        '''
        根据所在take返回特定FBBox的transform
        :param fb_box: FBBox对象
        :param take_name: take的名称
        :param frame: 帧数
        :param scene: FbxScene对象
        :return: transform
        '''
        # 找到对应的take
        for i in range(scene.GetSrcObjectCount(fbx.FbxCriteria.ObjectType(fbx.FbxAnimStack.ClassId))):
            anim_stack = scene.GetSrcObject(fbx.FbxCriteria.ObjectType(fbx.FbxAnimStack.ClassId), i)
            if anim_stack.GetName() == take_name:
                take = anim_stack
                break
        else:
            raise ValueError(f"Take {take_name} not found in the scene")

        # 设置当前的take
        scene.SetCurrentAnimationStack(take)

        # 创建一个FbxTime对象，并设置它的frame数
        time = fbx.FbxTime()
        time.SetFrame(frame)

        # 获取FBBox在这个时间点的transform
        transform: fbx.FbxAMatrix = fb_box.EvaluateGlobalTransform(time)

        return transform


class SkeletonAttributeCollector:
    def __init__(self, reader: CustomFbxReader):
        self.reader = reader

    def get_all_skeletons_attributes(self):
        result: list[CustomFBSkeletonAttributesDC] = []
        scene = self.reader.scene
        takes = self.reader.get_all_takes(scene)
        boxes = CustomFBSkeletonUtils.get_fbx_node_attributes(scene)
        for take in takes:
            for box in boxes:
                if isinstance(box.GetNodeAttribute(), fbx.FbxSkeleton):
                    custom_fb_box = CustomFBModelSkeleton(box)
                    result.append(custom_fb_box.get_custom_attributes_by_anim_stack(take))
        return result
