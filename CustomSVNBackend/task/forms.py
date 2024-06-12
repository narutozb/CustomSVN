from django import forms
from .models import Task, Comment


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['project', 'name', 'description', 'assigned_to', 'status', 'priority', 'parent_task']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content',]
