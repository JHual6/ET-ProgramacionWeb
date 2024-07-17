from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Cart, CartItem, Contacto
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required
from .forms import ContactoForm
from django.conf import settings
from transbank.webpay.webpay_plus.transaction import Transaction
from django.http import JsonResponse  
# Página inicial
def home(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})
# Lista de productos
def product_list(request):
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()
    
    cart_items = []
    total = 0  
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        total = sum(item.product.price * item.quantity for item in cart_items)
    else:
        cart = request.session.get('cart', {})
        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, id=product_id)
            cart_items.append({'product': product, 'quantity': quantity, 'subtotal': product.price * quantity})
        total = sum(item['subtotal'] for item in cart_items)
    return render(request, 'product_list.html', {'products': products, 'cart_items': cart_items, 'total': total})
# Ver carrito de compras
def view_cart(request):
    cart_items = []
    total = 0  
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        total = sum(item.product.price * item.quantity for item in cart_items)
    else:
        cart = request.session.get('cart', {})
        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, id=product_id)
            cart_items.append({'product': product, 'quantity': quantity, 'subtotal': product.price * quantity})
        total = sum(item['subtotal'] for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})
# Redirección al pago con webpay
@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    total = sum(item.product.price * item.quantity for item in cart_items)
    buy_order = str(cart.id)
    session_id = str(request.user.id)
    return_url = request.build_absolute_uri('/store/return/')
    
    transaction = Transaction()
    response = transaction.create(buy_order, session_id, total, return_url)
    
    token = response.get('token')
    webpay_url = response.get('url')
    if token and webpay_url:
        return redirect(f"{webpay_url}?token_ws={token}")
    else:
        return JsonResponse({'message': 'Error en la transacción', 'response': response})
# Crear un nuevo contacto (Todos los usuarios)
def contacto_nuevo(request):
    if request.method == "POST":
        form = ContactoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('store:contacto_confirmacion')
    else:
        form = ContactoForm()
    return render(request, 'store/contacto_formulario.html', {'form': form})
# Ver detalles de un contacto
@login_required
def contacto_detalle(request, pk):
    contacto = get_object_or_404(Contacto, pk=pk)
    return render(request, 'store/contacto_detalle.html', {'contacto': contacto})
# Editar datos en un contacto
@login_required
def contacto_editar(request, pk):
    contacto = get_object_or_404(Contacto, pk=pk)
    if request.method == "POST":
        form = ContactoForm(request.POST, instance=contacto)
        if form.is_valid():
            form.save()
            return redirect('store:contacto_detalle', pk=contacto.pk)
    else:
        form = ContactoForm(instance=contacto)
    return render(request, 'store/contacto_editar.html', {'form': form})
# Eliminar un mensaje en contacto
@login_required
def contacto_eliminar(request, pk):
    contacto = get_object_or_404(Contacto, pk=pk)
    contacto.delete()
    return redirect('store:contacto_lista')
# Lista de mensajes de contacto
@login_required
def contacto_lista(request):
    contactos = Contacto.objects.all()
    return render(request, 'store/contacto_lista.html', {'contactos': contactos})
# Confirmación del envío de mensaje de contacto
def contacto_confirmacion(request):
    return render(request, 'store/contacto_confirmacion.html')
# Vista protegida (No se ocupa)
@login_required
def vista_protegida(request):
    return render(request, 'store:vista_protegida.html')
# Volver de webpay
@login_required
def return_from_webpay(request):
    token = request.GET.get('token_ws')
    transaction = Transaction()
    response = transaction.commit(token)
    
    if response.get('response_code') == 0:
        # Actualiza el estado del pedido, vacía el carrito, etc.
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        for item in cart_items:
            item.product.stock -= item.quantity
            item.product.save()
        cart_items.delete()
        return render(request, 'store/payment_success.html', {'response': response})
    else:
        return render(request, 'store/payment_failed.html', {'response': response})
# Obtener los detalles del carrito de compras
def get_cart_details(request):
    cart_items = []
    total = 0  
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        total = sum(item.product.price * item.quantity for item in cart_items)
    else:
        cart = request.session.get('cart', {})
        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, id=product_id)
            cart_items.append({'product': product, 'quantity': quantity, 'subtotal': product.price * quantity})
        total = sum(item['subtotal'] for item in cart_items)
    return cart_items, total
# Cambiar la imagen para poder guardarla y ocuparla en las funciones js
class CustomJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'url'):
            return obj.url
        return super().default(obj)
# Agregar un producto al carrito
def add_to_cart(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id)
        cart = request.session.get('cart', {})
        cart[str(product_id)] = cart.get(str(product_id), 0) + 1
        request.session['cart'] = cart
        # Obtener los elementos del carrito desde la sesión
        cart_items = [{'product': get_object_or_404(Product, id=pid), 'quantity': qty} for pid, qty in cart.items()]
        total = sum(item['product'].price * item['quantity'] for item in cart_items)
        # Preparar los datos del carrito para la respuesta JSON
        cart_items_data = [
            {
                'id': pid,
                'product': {
                    'name': item['product'].name,
                    'price': float(item['product'].price),  # Asegurarse de que el precio sea un número
                    'image': item['product'].image.url if item['product'].image else None
                },
                'quantity': item['quantity']
            }
            for pid, item in zip(cart.keys(), cart_items)
        ]
        return JsonResponse({'success': True, 'cart_items': cart_items_data, 'total': float(total)}, encoder=CustomJSONEncoder)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
# Aumentar en 1 un producto en el carrito
def aumentar_del_carrito(request, cart_item_id):
    try:
        cart_item = get_object_or_404(CartItem, id=cart_item_id)
        cart_item.quantity += 1
        cart_item.save()
        cart_items, total = get_cart_details(request)
        cart_items_data = [{'id': item.id, 'product': {'name': item.product.name, 'price': item.product.price, 'image': item.product.image.url if item.product.image else None}, 'quantity': item.quantity} for item in cart_items]
        return JsonResponse({'success': True, 'quantity': cart_item.quantity, 'cart_items': cart_items_data, 'total': total})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
# Disminuir en 1 de un producto en el carrito
def disminuir_del_carrito(request, cart_item_id):
    try:
        cart_item = get_object_or_404(CartItem, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
        cart_items, total = get_cart_details(request)
        cart_items_data = [{'id': item.id, 'product': {'name': item.product.name, 'price': item.product.price, 'image': item.product.image.url if item.product.image else None}, 'quantity': item.quantity} for item in cart_items]
        return JsonResponse({'success': True, 'quantity': cart_item.quantity, 'cart_items': cart_items_data, 'total': total})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
# Eliminar un producto del carrito
def remove_from_cart(request, cart_item_id):
    try:
        cart_item = get_object_or_404(CartItem, id=cart_item_id)
        cart_item.delete()
        cart_items, total = get_cart_details(request)
        cart_items_data = [{'id': item.id, 'product': {'name': item.product.name, 'price': item.product.price, 'image': item.product.image.url if item.product.image else None}, 'quantity': item.quantity} for item in cart_items]
        return JsonResponse({'success': True, 'cart_items': cart_items_data, 'total': total})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)