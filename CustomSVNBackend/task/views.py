from django.shortcuts import render, get_object_or_404, redirect
from .models import Task, Comment
from .forms import TaskForm, CommentForm


def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    comments = task.comments.all()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST, request.FILES)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()
            return redirect('task_detail', task_id=task.id)
    else:
        comment_form = CommentForm()

    return render(request, 'task/task_detail.html', {
        'task': task,
        'comments': comments,
        'comment_form': comment_form
    })


def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.save()
            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskForm()

    return render(request, 'task/task_form.html', {'form': form})
