from django.shortcuts import render
from rest_framework import exceptions, pagination, serializers, viewsets, status, generics, mixins
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import ViewPermission
from .authentication import generate_access_token, JWTAuthentication
from users.models import User, Permission, Role
from .serializers import PermissionSerializer, RoleSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated
from api_test.pagination import CustomPagination
# Create your views here.

@api_view(['POST'])
def register(request):
    data = request.data
    if data['password'] != data['confirm_password']:
        raise exceptions.APIException('passwords not match')
    user = UserSerializer(data=data)
    user.is_valid(raise_exception=True)
    user.save()
    return Response(user.data)


@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = User.objects.filter(username=username).first()
    if user is None:
        raise exceptions.AuthenticationFailed('user not found')
    
    if not user.check_password(password):
        raise exceptions.AuthenticationFailed('incorrect password')

    response = Response()
    token = generate_access_token(user)
    response.set_cookie(key='jwt', value=token, httponly=True)
    response.data = {
        'jwt':token
    }

    return response


class AuthenticateUser(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = UserSerializer(request.user).data
        data['permissions'] = [p['name'] for p in data['role']['permissions']]
        return Response({
            'data': data
        })

@api_view(['POST'])
def logout(_):
    response = Response()
    response.delete_cookie(key='jwt')
    response.data = {
        'message': 'Success'
    }

    return response



class PermissionAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = PermissionSerializer(Permission.objects.all(), many=True)

        return Response({
            'data':serializer.data
        })


class RoleAPIView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated & ViewPermission]
    permission_obj = 'roles'

    # get all objs --> get
    def list(self, request):
        serializer = RoleSerializer(Role.objects.all(), many=True)
        return Response({
            'data': serializer.data
        })

    # create obj --> post
    def create(self, request):
        serializer = RoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'data':serializer.data
        }, status=status.HTTP_201_CREATED)


    # get single obj --> get
    def retrieve(self, request, pk=None):
        role = Role.objects.get(id=pk)
        serializer = RoleSerializer(role)

        return Response({
            'data':serializer.data
        })

    # update obj --> put
    def update(self, request, pk=None):
        role = Role.objects.get(id=pk)
        serializer = RoleSerializer(instance=role, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'data':serializer.data
        }, status=status.HTTP_202_ACCEPTED)

    # delete obj --> delete
    def destroy(self, request, pk=None):
        role = Role.objects.get(id=pk)
        role.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class UserGenericAPIView(generics.GenericAPIView, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated & ViewPermission]
    permission_obj = 'users'
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination

    def get(self, request, pk=None):
        if pk:
            return Response({
                'data': self.retrieve(request, pk).data
            })
        
        return self.list(request, pk)
        
    def post(self, request):
        request.data.update({
            'password': 'pass123',
            'role':request.data['role_id']
        })
        return Response({
                'data': self.create(request).data
            })
    
    def put(self, request, pk=None):
        request.data.update({
            'password': 'pass123',
            'role':request.data['role_id']
        })
        return Response({
                'data': self.update(request, pk).data
            })
    
    def patch(self, request, pk=None):
        role_id = request.data.get('role_id', None)
        if role_id:
            request.data.update({
                'role':role_id
            })
            
        return Response({
                'data': self.partial_update(request, pk).data
            })
    
    def delete(self, request, pk=None):
        return self.destroy(request, pk)



class ProfileInfoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated & ViewPermission]
    permission_obj = 'users'

    def put(self, request, pk=None):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    

class ProfilePasswordAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated & ViewPermission]
    permission_obj = 'users'

    def put(self, request, pk=None):
        user = request.user

        if request.data['password'] != request.data['confirm_password']:
            raise exceptions.ValidationError('passwords donot match')

        user.set_password(request.data['password'])
        user.save()
        serializer = UserSerializer(user)
        return Response(serializer.data)
    