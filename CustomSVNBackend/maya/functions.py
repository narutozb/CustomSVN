from maya.models import TransformNode


def get_node_full_path(node_name: str, scene_id: int):
    '''
    通过节点名称和场景ID获取节点的全路径
    '''

    def build_path(node):
        if node.parent is None:
            return f"|{node.node_name}"
        else:
            return f"{build_path(node.parent)}|{node.node_name}"

    try:
        node = TransformNode.objects.get(node_name=node_name, scene_id=scene_id)
        return build_path(node)
    except TransformNode.DoesNotExist:
        return None
