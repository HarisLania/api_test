from types import FrameType
from django.shortcuts import render
from rest_framework import generics, mixins, serializers
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import authentication_classes, parser_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from main.authentication import JWTAuthentication
from users.permissions import ViewPermission
from .models import Product
from .serializers import ProductSerializer
from django.core.files.storage import default_storage


# Create your views here.

class ProductGenericView(generics.GenericAPIView, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated & ViewPermission]
    permission_obj = 'products'
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, request, pk=None):
        if pk:
            return Response({
                'data': self.retrieve(request, pk).data
            })
        return Response({
                'data': self.list(request).data
            })


    def post(self, request):
        return Response({
            'data': self.create(request).data
        })
    
    def put(self, request, pk=None):
        if pk:
            return Response({
                'data': self.update(request, pk).data
            })
    
    def patch(self, request, pk=None):
        if pk:
            return Response({
                'data': self.partial_update(request, pk).data
            })

    def delete(self, request, pk=None):
        if pk:
            return self.destroy(request, pk)


# image upload 
class FileUploadAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated & ViewPermission]
    permission_obj = 'products'
    parser_classes = (MultiPartParser, )

    def post(self, request):
        file = request.FILES['image']
        file_name = default_storage.save(file.name, file)
        url = default_storage.url(file_name)

        return Response({
            'url': 'http://127.0.0.1:8000/products' + url
        })

