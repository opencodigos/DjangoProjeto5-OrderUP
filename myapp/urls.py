from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import ( 
    home, 
    register,
    restaurant_create,
    restaurant_detail, 
    menu_item_create,
    my_restaurants,
    reservation_create,
    reservation_detail,
    my_reservations,
    reservation_manage,
    reservation_update_status, 
    create_order,
    order_detail,
    order_manage,
    order_update_status,
    my_orders,
)

urlpatterns = [
    path('', home, name='home'), 

    path('login/', LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),

    # URLs de restaurante
    path('restaurant/create/', restaurant_create, name='restaurant_create'),
    path('restaurant/<int:pk>/', restaurant_detail, name='restaurant_detail'),
    path('restaurant/<int:restaurant_pk>/menu/add/', menu_item_create, name='menu_item_create'),
    path('my-restaurants/', my_restaurants, name='my_restaurants'), 

    # URLs de reserva
    path('restaurant/<int:restaurant_pk>/reserve/', reservation_create, name='reservation_create'), 
    path('reservation/<int:pk>/', reservation_detail, name='reservation_detail'), 
    path('reservations/', my_reservations, name='my_reservations'),

    path('restaurant/<int:restaurant_pk>/reservations/', reservation_manage, name='reservation_manage'), 
    path('reservation/<int:pk>/update-status/', reservation_update_status, name='reservation_update_status'),
    
    # URLs de Order
    path('reservation/<int:reservation_pk>/order/', create_order, name='create_order'),
    path('order/<int:pk>/', order_detail, name='order_detail'),

    path('restaurant/<int:restaurant_pk>/orders/', order_manage, name='order_manage'),
    path('order/<int:pk>/update-status/', order_update_status, name='order_update_status'),

    path('orders/', my_orders, name='my_orders'), 
]