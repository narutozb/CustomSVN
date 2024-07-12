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
        file_changes_instances = [FileChange(commit=commit, **change_data) for change_data in file_changes_data]
        FileChange.objects.bulk_create(file_changes_instances)

        return commit

    def update(self, instance, validated_data):
        file_changes_data = validated_data.pop('file_changes', [])
        current_version = version.parse(instance.svn_client_version)
        new_version = version.parse(validated_data.get('svn_client_version', '0.0.0'))

        # 比较版本号
        if new_version > current_version:  # TODO: 测试时为>= 。commit时更改为>
            # print('update...')
            for k, v in validated_data.items():
                setattr(instance, k, v)
            instance.save()

            file_changes_to_update = []  # 准备更新的列表
            file_changes_to_create = []  # 准备创建的列表
            update_fields = set()  # 使用集合来避免重复字段名
            existing_file_changes = FileChange.objects.filter(
                commit=instance,
                path__in=[_['path'] for _ in file_changes_data]
            )
            existing_file_changes_dict = {_.path: _ for _ in existing_file_changes}
            for i in file_changes_data:
                file_change = existing_file_changes_dict.get(i['path'])
                if file_change:
                    # 如果存在则更新
                    for k, v in i.items():
                        if hasattr(file_change, k):
                            setattr(file_change, k, v)
                            update_fields.add(k)
                    file_changes_to_update.append(file_change)
                else:
                    # 如果不存在则创建新对象
                    file_changes_to_create.append(FileChange(commit=instance, **i))

            # 更新或创建 file changes
            FileChange.objects.bulk_update(file_changes_to_update, list(update_fields))
            FileChange.objects.bulk_create(file_changes_to_create)

            # print(f"Updated {len(file_changes_to_update)} records with fields {list(update_fields)}.")
            # print(f"Created {len(file_changes_to_create)} new records.")

        return instance


@api_view(['POST', 'GET'])
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
