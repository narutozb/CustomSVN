from django.db import models
from .validators import validate_url


class Repository(models.Model):
    name = models.CharField(max_length=100, unique=True)

    url = models.CharField(max_length=200, unique=True, validators=[validate_url])
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Branch(models.Model):
    name = models.CharField(max_length=100)
    repository = models.ForeignKey(Repository, related_name='branches', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.repository.name}-{self.name}'

    class Meta:
        ordering = ['id']


class Commit(models.Model):
    repository = models.ForeignKey(Repository, related_name='commits', on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, related_name='commits', on_delete=models.CASCADE, null=True, blank=True)
    revision = models.IntegerField()
    author = models.CharField(max_length=100, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    svn_client_version = models.CharField(max_length=16, default='0.0.0', null=True, blank=True)

    class Meta:
        unique_together = ('repository', 'revision')
        ordering = ['-revision']  # Default ordering by date

    def __str__(self):
        return f"r{self.revision} - {self.author}"


class FileChange(models.Model):
    commit = models.ForeignKey(Commit, related_name='file_changes', on_delete=models.CASCADE)
    path = models.CharField(max_length=255, )
    action = models.CharField(max_length=10)  # , choices=[('A', 'Added'), ('M', 'Modified'), ('D', 'Deleted')])
    kind = models.CharField(max_length=8, null=True, blank=True)

    def __str__(self):
        return f"{self.id}-{self.path} ({self.action})"
