from django.urls import path
from .views import UserGenericAPIView, AuthenticateUser, login, logout, register, PermissionAPIView, RoleAPIView, ProfileInfoAPIView, ProfilePasswordAPIView

urlpatterns = [
    path('register', register),
    path('login', login),
    path('user', AuthenticateUser.as_view()),
    path('permission', PermissionAPIView.as_view()),
    path('role', RoleAPIView.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('role/<str:pk>', RoleAPIView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    })),
    # it should always be above users/pk as it may conflict with it
    path('users/info', ProfileInfoAPIView.as_view()),
    path('users/password', ProfilePasswordAPIView.as_view()),
    path('users', UserGenericAPIView.as_view()),
    path('users/<str:pk>', UserGenericAPIView.as_view()),
    path('logout', logout)
]