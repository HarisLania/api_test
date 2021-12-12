from django.urls import path
from .views import FileUploadAPIView, ProductGenericView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('products', ProductGenericView.as_view()),
    path('products/<str:pk>', ProductGenericView.as_view()),
    path('upload', FileUploadAPIView.as_view())
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)