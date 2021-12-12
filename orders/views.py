from datetime import date
from django.db import connection
from django.shortcuts import render
from rest_framework import generics
from django.shortcuts import render
from rest_framework import generics, mixins
from rest_framework import response
from rest_framework.permissions import IsAuthenticated
from main.authentication import JWTAuthentication
from users.permissions import ViewPermission
from .models import Order, OrderItem
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import OrderSerializer
from api_test.pagination import CustomPagination
from django.http import HttpResponse
import csv
# Create your views here.

class OrderGenericAPIView(generics.GenericAPIView, mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated & ViewPermission]
    permission_obj = 'orders'
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = CustomPagination

    def get(self, request, pk=None):
        if pk:
            return Response({
                'data': self.retrieve(request, pk).data
            })
        return Response({
                'data': self.list(request).data
            })
    
    def delete(self, request, pk=None):
        if pk:
            return self.destroy(request, pk)
    


class ExportAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated & ViewPermission]
    permission_obj = 'users'

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachement; filename=orders.json'
        orders = Order.objects.all()
        writer = csv.writer(response)
        writer.writerow(['ID', 'Name', 'Email', 'Prdouct Title', 'Price', 'Quantity'])

        for order in orders:
            writer.writerow([order.id, order.name, order.email, '', '', ''])

            orderItems = OrderItem.objects.filter(order_id=order.id)
            for items in orderItems:
                writer.writerow(['', '', '', items.product_title, items.price, items.quantity])


        return response



class ChartAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated & ViewPermission]
    permission_obj = 'users'

    def get(self, _):
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT o.created_at AS date, sum(i.quantity * i.price) AS sum
            FROM orders_order as o
            JOIN orders_orderitem as i ON o.id = i.order_id
            GROUP BY date
            """)
            row = cursor.fetchall()

            data = [
                {
                    'date': result[0],
                    'sum': result[1]
                } for result in row
            ]
        
        return Response({
            'data': data
        })