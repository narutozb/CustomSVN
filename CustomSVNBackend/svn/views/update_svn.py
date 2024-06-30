from rest_framework import serializers
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from packaging import version
from ..models import Commit, Branch, Repository, FileChange
from ..serializers import FileChangeSerializer, RepositorySerializer


class ReceiveCommitSerializer(serializers.ModelSerializer):
    file_changes = FileChangeSerializer(many=True, required=False)

    class Meta:
        model = Commit
        fields = ['repository', 'revision', 'author', 'message', 'date', 'branch', 'svn_client_version', 'file_changes']

    def create(self, validated_data):
        print('create..')
        file_changes_data = validated_data.pop('file_changes', [])
        commit = Commit.objects.create(**validated_data)
        for change_data in file_changes_data:
            FileChange.objects.create(commit=commit, **change_data)

        return commit

    def update(self, instance, validated_data):
        file_changes_data = validated_data.pop('file_changes', [])
        current_version = version.parse(instance.svn_client_version)
        new_version = version.parse(validated_data.get('svn_client_version', '0.0.0'))

        # 比较版本号
        if new_version >= current_version:  # TODO: 测试时为>= 。commit时更改为>
            print('update...')
            for k, v in validated_data.items():
                setattr(instance, k, v)
            instance.save()

            # 更新或创建 file changes
            for change_data in file_changes_data:
                file_change, created = FileChange.objects.update_or_create(
                    commit=instance,
                    path=change_data['path'],
                    defaults=change_data
                )

        return instance


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def receive_commits(request):
    '''
    接收commits数据并且储存进数据库
    '''
    commits_data = request.data
    for d in commits_data:
        repo = Repository.objects.get(name=d.get('repo_name'))
        branch, _ = Branch.objects.get_or_create(name=d.get('branch_name'), repository=repo)
        commit_data = {
            'repository': repo.id,
            'revision': d.get('revision'),
            'branch': branch.id,
            'author': d.get('author'),
            'message': d.get('message'),
            'date': d.get('date'),
            'svn_client_version': d.get('svn_client_version'),
            'file_changes': d.get('file_changes', [])
        }
        try:
            # 尝试获取现有的 Commit 实例
            commit_instance = Commit.objects.get(repository=repo, revision=d.get('revision'))
            # 序列化器使用现有实例进行更新
            serializer = ReceiveCommitSerializer(commit_instance, data=commit_data)
        except Commit.DoesNotExist:
            # 如果不存在，创建新的 Commit
            serializer = ReceiveCommitSerializer(data=commit_data)
        if serializer.is_valid():
            serializer.save()
        else:
            # 处理无效数据的情况
            return Response(serializer.errors, status=400)

    return Response({'status': 'success'}, status=200)
