import re
from django.db.models import OuterRef, Subquery, F, Q, Count
from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from rest_framework.views import APIView

from svn.models import FileChange, Commit
from svn.query_functions.functions import query_file_changes_by_repo_name_and_file_changes
from svn.serializers import QueryFileChangeSerializer, CommitSerializer, FileChangeSerializer, CommitDetailSerializer
from svn.views.custom_class import CustomPagination


class FileChangeListLatestExistView(APIView):
    '''
    repo_name/<str:repo_name>/list_latest_exit_file_changes/?branch_name=branches/branch_name

    通过仓库名和分支名查找所有现存的FileChange数据

    '''

    def get(self, request, repo_name, *args, **kwargs):
        branch_name = request.query_params.get('branch_name', 'trunk')  # 获取分支名字

        # 创建一个Subquery，找到每个file_path的最大revision
        latest_revisions = FileChange.objects.filter(path=OuterRef('path')).order_by('-commit__revision')

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
        file_changes = file_changes.exclude(action='D')

        data = file_changes.values(
            'path',
            'action',
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
        "path":"https://qiaoyuanzhen/svn/MyDataSVN/trunk/RootFolder/fbx_files/animation_test1.fbx"
    }
    '''

    def put(self, request, repo_name: str):
        try:
            path = request.data.get('path')
            queryset = FileChange.objects.filter(commit__repository__name=repo_name, path=path).order_by(
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
            "path": "https://qiaoyuanzhen/svn/MyDataSVN/trunk/RootFolder/fbx_files/animation_test1.fbx",
            "revision": 17,
            "repo_name": "MyDataSVN"},
        {
            "path": "https://qiaoyuanzhen/svn/MyDataSVN/trunk/RootFolder/fbx_files/animation_test2.fbx",
            "revision": 17,
            "repo_name": "MyDataSVN"},
        {
            "path": "https://qiaoyuanzhen/svn/MyDataSVN/tags/release-1.0/RootFolder/_test_file.mb",
            "revision": 13,
            "repo_name": "MyDataSVN"}
        ]
    }
    """

    def get(self, request, *args, **kwargs):
        data = {'msg': 12121212}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        # 检查请求数据是否包含file_changes

        try:
            serializer = query_file_changes_by_repo_name_and_file_changes(request)
            return Response(serializer.data, status=status.HTTP_200_OK)


        except FileChange.DoesNotExist:
            return Response({
                'status': 'error', 'message': 'FileChange does not exist.如果有任意一个FileChange不存在，将返回404错误',
            },
                status=status.HTTP_404_NOT_FOUND)


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 50000


class CommitSearchView(APIView):
    pagination_class = CustomPageNumberPagination

    def post(self, request):
        '''
        前端搜索数据使用
        '''
        # 获取请求数据
        data = request.data
        repository_id = data.get('repository')
        branches = data.get('branches', [])
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        contents = data.get('contents')
        exact_search = data.get('exact_search', False)
        search_type = data.get('search_type', [])

        # 开始构建查询
        queryset = Commit.objects.filter(repository_id=repository_id)

        if branches:
            queryset = queryset.filter(branch_id__in=branches)

        # 处理日期过滤
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])
        elif start_date:
            queryset = queryset.filter(date__gte=start_date)
        elif end_date:
            queryset = queryset.filter(date__lte=end_date)

        # 处理内容搜索
        if contents:
            content_filter = Q()
            for search_field in search_type:
                if search_field == 'revision':
                    if contents.isdigit():
                        if exact_search:
                            content_filter |= Q(revision=int(contents))
                        else:
                            content_filter |= Q(revision__icontains=contents)
                    elif exact_search:
                        # 如果是精确搜索且内容不是数字，则返回空结果
                        return Response({'results': [], 'count': 0})
                elif search_field == 'message':
                    if exact_search:
                        content_filter |= Q(message__exact=contents)
                    else:
                        content_filter |= Q(message__icontains=contents)
                elif search_field == 'auth':  # 这里改为 'author'
                    if exact_search:
                        content_filter |= Q(author__exact=contents)
                    else:
                        content_filter |= Q(author__icontains=contents)

            queryset = queryset.filter(content_filter)

        # 应用分页
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        # 序列化结果
        serializer = CommitSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class CommitDetailView(APIView):

    def get(self, request, commit_id):
        try:
            commit = Commit.objects.get(id=commit_id)
            serializer = CommitDetailSerializer(commit)
            return Response(serializer.data)
        except Commit.DoesNotExist:
            return Response({"error": "Commit not found"}, status=status.HTTP_404_NOT_FOUND)