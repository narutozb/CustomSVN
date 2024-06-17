from django.db.models import OuterRef, Subquery, F
from rest_framework import status
from rest_framework.response import Response

from rest_framework.views import APIView

from svn._dc import FileChangeSummaryDC
from svn.models import FileChange
from svn.serializers import QueryFileChangeSerializer
from svn.views.custom_class import CustomPagination


class FileChangeListLatestExistView(APIView):
    '''
    repo_name/<str:repo_name>/list_latest_exit_file_changes/?branch_name=branches/branch_name

    通过仓库名和分支名查找所有现存的FileChange数据

    '''

    def get(self, request, repo_name, *args, **kwargs):
        branch_name = request.query_params.get('branch_name', 'trunk')  # 获取分支名字

        # 创建一个Subquery，找到每个file_path的最大revision
        latest_revisions = FileChange.objects.filter(file_path=OuterRef('file_path')).order_by('-commit__revision')

        # 使用annotate将Subquery添加到查询集中
        file_changes = FileChange.objects.annotate(
            latest_revision=Subquery(latest_revisions.values('commit__revision')[:1])
        )

        # 过滤查询集，只保留那些revision等于其最大revision的FileChange对象
        file_changes = file_changes.filter(commit__revision=F('latest_revision'), commit__branch__name=branch_name)

        # 如果提供了仓库名称，就添加一个过滤条件
        if repo_name:
            file_changes = file_changes.filter(commit__repository__name=repo_name)

        # 过滤掉已删除的文件
        file_changes = file_changes.exclude(change_type='D')

        data = file_changes.values(
            'file_path',
            'change_type',
            'commit__revision',
            'commit__repository__name',
        )

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(data, request)
        return paginator.get_paginated_response(result_page)


class GetFileChangesByFilePath(APIView):
    '''
    通过特定file_path获取其以往数据
    {
        "file_path":"https://qiaoyuanzhen/svn/MyDataSVN/trunk/RootFolder/fbx_files/animation_test1.fbx"
    }
    '''

    def put(self, request, repo_name: str):
        try:
            file_path = request.data.get('file_path')
            queryset = FileChange.objects.filter(commit__repository__name=repo_name, file_path=file_path).order_by(
                '-commit__revision')
            serializer = QueryFileChangeSerializer(queryset, many=True)

            paginator = CustomPagination()

            result_page = paginator.paginate_queryset(serializer.data, request)
            return paginator.get_paginated_response(result_page)
        except FileChange.DoesNotExist:
            return Response({
                'status': 'error', 'message': 'FileChange does not exist.',
            },
                status=status.HTTP_404_NOT_FOUND)


class GetFileChangeByRevisionView(APIView):
    """
    通过仓库名和其revision还有file_path获取特定FileChange信息
    POST信息如下
    {
    "file_changes":
    [
        {
            "file_path": "https://qiaoyuanzhen/svn/MyDataSVN/trunk/RootFolder/fbx_files/animation_test1.fbx",
            "revision": 17,
            "repo_name": "MyDataSVN"},
        {
            "file_path": "https://qiaoyuanzhen/svn/MyDataSVN/trunk/RootFolder/fbx_files/animation_test2.fbx",
            "revision": 17,
            "repo_name": "MyDataSVN"},
        {
            "file_path": "https://qiaoyuanzhen/svn/MyDataSVN/tags/release-1.0/RootFolder/_test_file.mb",
            "revision": 13,
            "repo_name": "MyDataSVN"}
        ]
    }
    """

    def put(self, request):
        # 检查请求数据是否包含file_changes
        try:
            file_changes: list[dict] = request.data['file_changes']
            # 将上面的列表反序列化为list[FileChangeSummaryDC]
            file_change_summaries = [FileChangeSummaryDC(**_) for _ in file_changes]
        except (KeyError, TypeError):
            return Response({
                'status': 'error', 'message': 'Invalid request data.file_changes数据格式错误',
            },
                status=status.HTTP_400_BAD_REQUEST)
        try:
            data = []
            for i in file_change_summaries:
                file_change = FileChange.objects.get(
                    commit__repository__name=i.repo_name, commit__revision=i.revision, file_path=i.file_path
                )
                data.append(file_change)
            serializer = QueryFileChangeSerializer(data, many=True)
            return Response(serializer.data)

        except FileChange.DoesNotExist:
            return Response({
                'status': 'error', 'message': 'FileChange does not exist.如果有任意一个FileChange不存在，将返回404错误',
            },
                status=status.HTTP_404_NOT_FOUND)
