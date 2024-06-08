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
        return f'{self.name}'


class Commit(models.Model):
    repository = models.ForeignKey(Repository, related_name='commits', on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, related_name='commits', on_delete=models.CASCADE)
    revision = models.IntegerField()
    author = models.CharField(max_length=100)
    message = models.TextField()
    date = models.DateTimeField()

    class Meta:
        unique_together = ('repository', 'revision')
        ordering = ['-revision']  # Default ordering by date

    def __str__(self):
        return f"r{self.revision} - {self.author}"


class FileChange(models.Model):
    commit = models.ForeignKey(Commit, related_name='file_changes', on_delete=models.CASCADE)
    file_path = models.CharField(max_length=255, )
    change_type = models.CharField(max_length=10, choices=[('A', 'Added'), ('M', 'Modified'), ('D', 'Deleted')])

    def __str__(self):
        return f"{self.id}-{self.file_path} ({self.change_type})"
