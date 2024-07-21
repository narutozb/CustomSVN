# users/views.py
from django.contrib.auth import logout

from django.shortcuts import redirect, render
from django.contrib import messages
from django.views import View
from django.contrib.auth import authenticate, login

from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from svn.models import Commit
from svn.serializers import CommitQuerySerializer, CommitSerializer
from .models import CustomUser
from .serializers import UserSerializer


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, f'退出登录')
        return redirect('home')
    else:
        return redirect('home')


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]


class UserInfoView(APIView):
    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
        })


class TestAPI(APIView):
    def post(self, request):
        print(request.data)
        _data = request.data
        data = {'repositories': [_data['repository']], 'branches': _data['branches']}
        query_serializer = CommitQuerySerializer(data=data)

        if not query_serializer.is_valid():
            return Response(query_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        repositories = query_serializer.validated_data['repositories']
        branches = query_serializer.validated_data['branches']

        commits = Commit.objects.filter(
            repository__id__in=repositories,
            branch__id__in=branches
        ).select_related('repository', 'branch')

        serializer = CommitSerializer(commits, many=True)
        return Response(serializer.data)
