import operator
import re
from datetime import datetime, time
from functools import reduce
from django.core.exceptions import ValidationError
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.db import DatabaseError
from django.db.models import OuterRef, Subquery, F, Q
from django.utils import timezone
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from rest_framework.views import APIView

from svn.models import FileChange, Commit
from svn.serializers import QueryFileChangeSerializer, CommitSerializer, FileChangeSerializer, CommitDetailSerializer
from svn.pagination import CustomPagination


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




class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 50000


class CommitSearchView(APIView):
    pagination_class = CustomPageNumberPagination

    def post(self, request):
        '''
        前端搜索数据使用
        '''
        try:
            # 获取请求数据
            data = request.data
            repository_id = data.get('repository')
            branches = data.get('branches', [])
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            contents = data.get('contents')
            regex_search = data.get('regex_search', False)
            search_type = data.get('search_fields', [])

            # 开始构建查询
            queryset = Commit.objects.filter(repository_id=repository_id)

            if branches:
                queryset = queryset.filter(branch_id__in=branches)

            # 过滤时间
            if start_date or end_date:
                queryset = self.__filter_date(queryset, start_date, end_date)

            # 过滤关键字
            if regex_search and contents:
                queryset, error = self.__safe_regex_filter(queryset, fields=search_type, keywords=[contents])
                if error:
                    return Response({
                        "error": "Invalid regex pattern",
                        "details": error,
                        "data": []
                    }, status=status.HTTP_400_BAD_REQUEST)
            elif not regex_search and contents:
                queryset = self.__filter_contains_keywords(queryset, fields=search_type, keywords=[contents], )

            # 应用分页
            paginator = self.pagination_class()
            try:
                page = paginator.paginate_queryset(queryset, request)
            except (EmptyPage, PageNotAnInteger) as e:
                return Response({
                    "error": f"Pagination error: {str(e)}",
                    "data": []
                }, status=status.HTTP_400_BAD_REQUEST)

            # 序列化结果
            serializer = CommitSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            return Response({
                "error": f"An unexpected error occurred: {str(e)}",
                "data": []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def __safe_regex_filter(self, queryset, fields, keywords):
        try:
            queries = []
            for field in fields:
                for keyword in keywords:
                    if field == 'file_changes':
                        subquery = FileChange.objects.filter(path__regex=keyword).values('commit')
                        queries.append(Q(id__in=subquery))
                    else:
                        queries.append(Q(**{f"{field}__regex": keyword}))

            query = reduce(operator.or_, queries)
            return queryset.filter(query).distinct(), None
        except (re.error, ValidationError, DatabaseError) as e:
            error_message = f"Invalid regex pattern: {str(e)}"
            return queryset.none(), error_message

    def __filter_contains_keywords(self, queryset, fields: list[str] = None, keywords: list[str] = None):
        if fields is None:
            fields = ['message', 'author', 'revision']  # 默认搜索字段

        queries = []
        for field in fields:
            for keyword in keywords:
                if field == 'file_changes':
                    # 对file_changes字段使用子查询
                    subquery = FileChange.objects.filter(path__icontains=keyword).values('commit')
                    queries.append(Q(id__in=subquery))
                else:
                    queries.append(Q(**{f"{field}__icontains": keyword}))

        query = reduce(operator.or_, queries)
        return queryset.filter(query).distinct()

    def __build_search_query(self, fields, keywords, search_option='__icontains'):
        queries = [
            Q(**{f"{field}{search_option}": keyword})
            for field in fields
            for keyword in keywords
        ]
        return reduce(operator.or_, queries)

    def __filter_date(self, queryset, start_date, end_date):
        # 处理日期过滤
        if start_date or end_date:
            if start_date:
                start_datetime = timezone.localtime(
                    timezone.make_aware(datetime.combine(datetime.strptime(start_date, '%Y-%m-%d'), time.min)))
            else:
                start_datetime = None

            if end_date:
                end_datetime = timezone.localtime(
                    timezone.make_aware(datetime.combine(datetime.strptime(end_date, '%Y-%m-%d'), time.max)))
            else:
                end_datetime = None

            if start_datetime and end_datetime:
                queryset = queryset.filter(date__range=(start_datetime, end_datetime))
            elif start_datetime:
                queryset = queryset.filter(date__gte=start_datetime)
            elif end_datetime:
                queryset = queryset.filter(date__lte=end_datetime)

            return queryset


class CommitDetailView(APIView):
    def get(self, request, commit_id):
        try:
            commit = Commit.objects.select_related('repository', 'branch').get(id=commit_id)
            serializer = CommitDetailSerializer(commit)
            return Response(serializer.data)
        except Commit.DoesNotExist:
            return Response({"error": "Commit not found"}, status=status.HTTP_404_NOT_FOUND)


class CommitsByFilePathView(APIView):
    pagination_class = PageNumberPagination

    def get(self, request):
        file_path = request.query_params.get('path')

        if not file_path:
            return Response({"error": "File path is required"}, status=status.HTTP_400_BAD_REQUEST)

        commits = Commit.objects.filter(file_changes__path=file_path).distinct().order_by('-date')

        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(commits, request)
        serializer = CommitSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class GetFileChangeDetail(APIView):
    def get(self, request, file_change_id):
        try:
            file_change = FileChange.objects.select_related('commit__repository').get(id=file_change_id)
            serializer = FileChangeSerializer(file_change)
            return Response(serializer.data)
        except FileChange.DoesNotExist:
            return Response({"error": "File change not found"}, status=status.HTTP_404_NOT_FOUND)
