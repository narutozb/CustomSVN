from django.core.management.base import BaseCommand
from svn.models import Repository, Commit, FileChange
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Populate the database with test data'

    def handle(self, *args, **kwargs):
        # Clear existing data
        FileChange.objects.all().delete()
        Commit.objects.all().delete()
        Repository.objects.all().delete()

        # Create test repositories
        repo1 = Repository.objects.create(name='Repo1', url='http://example.com/repo1', description='Test repository 1', created_at=timezone.now())
        repo2 = Repository.objects.create(name='Repo2', url='http://example.com/repo2', description='Test repository 2', created_at=timezone.now())

        # Create test commits for Repo1
        commit1 = Commit.objects.create(repository=repo1, revision='1', author='Alice', message='Initial commit', date=timezone.now())
        commit2 = Commit.objects.create(repository=repo1, revision='2', author='Bob', message='Added new feature', date=timezone.now())

        # Create test commits for Repo2
        commit3 = Commit.objects.create(repository=repo2, revision='1', author='Charlie', message='Initial commit', date=timezone.now())
        commit4 = Commit.objects.create(repository=repo2, revision='2', author='Dave', message='Fixed bug', date=timezone.now())

        # Create test file changes for commits
        FileChange.objects.create(commit=commit1, file_path='file1.txt', change_type='A')
        FileChange.objects.create(commit=commit2, file_path='file2.txt', change_type='M')
        FileChange.objects.create(commit=commit3, file_path='file3.txt', change_type='A')
        FileChange.objects.create(commit=commit4, file_path='file4.txt', change_type='D')

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with test data'))
