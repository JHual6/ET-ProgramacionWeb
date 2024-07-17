from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('home/', views.home, name='home'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('return/', views.return_from_webpay, name='return_from_webpay'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('aumentar_del_carrito/<int:cart_item_id>/', views.aumentar_del_carrito, name='aumentar_del_carrito'),
    path('disminuir_del_carrito/<int:cart_item_id>/', views.disminuir_del_carrito, name='disminuir_del_carrito'),
    path('remove_from_cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('contacto/', views.contacto_nuevo, name='contacto_nuevo'),
    path('contacto/<int:pk>/', views.contacto_detalle, name='contacto_detalle'),
    path('contacto/<int:pk>/editar/', views.contacto_editar, name='contacto_editar'),
    path('contacto/<int:pk>/eliminar/', views.contacto_eliminar, name='contacto_eliminar'),
    path('contactos/', views.contacto_lista, name='contacto_lista'),
    path('contacto/confirmacion/', views.contacto_confirmacion, name='contacto_confirmacion'),
    path('vista_protegida/', views.vista_protegida, name='vista_protegida'),
]
