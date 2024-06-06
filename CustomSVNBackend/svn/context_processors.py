from svn.models import Repository


def navbar_context_processor(request):
    return {'repositories': Repository.objects.all()}
