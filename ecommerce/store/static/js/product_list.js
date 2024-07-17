// Función para actualizar el contenido del carrito en la interfaz
function updateCartUI(cartItems, total) {
    const cartContainer = $('#cartContainer');
    cartContainer.empty();

    if (cartItems.length > 0) {
        cartItems.forEach(item => {
            const productPrice = parseFloat(item.product.price).toFixed(0);
            cartContainer.append(`
                <div class="cart-item">
                    ${item.product.image ? `<img src="${item.product.image}" alt="${item.product.name}">` : ''}
                    <div class="cart-item-details">
                        <span>${item.product.name}</span>
                        <span class="cart-item-price">${item.quantity} x $${productPrice}</span>
                        <div class="container-fluid botones_carrito">
                            <a href="#" data-cart-item-id="${item.id}" class="btn boton_aumentar d-flex justify-content-center align-items-center"><i class="fa-solid fa-plus"></i></a>
                            <a href="#" data-cart-item-id="${item.id}" class="btn boton_disminuir d-flex justify-content-center align-items-center"><i class="fa-solid fa-minus"></i></a>
                            <a href="#" data-cart-item-id="${item.id}" class="btn boton_eliminar d-flex justify-content-center align-items-center"><i class="fa-solid fa-trash"></i></a>
                        </div>
                    </div>
                </div>
            `);
        });
        cartContainer.append(`
            <hr class="dropdown-divider">
            <div class="cart-subtotal">Subtotal: $${parseFloat(total).toFixed(0)}</div>
            <div class="cart-actions">
                <a href="/store/view_cart/" class="btn boton_carrito">Ver carrito</a>
                <a href="/store/checkout/" class="btn boton_carrito">Finalizar compra</a>
            </div>
        `);
    } else {
        cartContainer.append(`<div class="dropdown-item text-center">No hay productos en el carrito</div>`);
    }
}

// Document ready handler
$(document).ready(function() {
    // Mostrar el carrito al hacer clic en el botón
    const cartButton = document.getElementById('cartButton');
    const cartContainer = document.getElementById('cartContainer');

    cartButton.addEventListener('click', function() {
        cartContainer.style.display = (cartContainer.style.display === 'none' || cartContainer.style.display === '') ? 'block' : 'none';
    });

    document.addEventListener('click', function(event) {
        if (!cartButton.contains(event.target) && !cartContainer.contains(event.target)) {
            cartContainer.style.display = 'none';
        }
    });

    // Función para agregar un producto al carrito sin recargar la página
    $('.boton_agregar').click(function(event) {
        event.preventDefault();
        const productId = $(this).data('product-id');
        $.ajax({
            url: `/add_to_cart/${productId}/`,
            type: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(data) {
                if (data.success) {
                    alert('Producto agregado al carrito');
                    updateCartUI(data.cart_items, data.total);
                }
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
            }
        });
    });

    // Eventos para aumentar, disminuir y eliminar productos del carrito sin recargar la página
    $(document).on('click', '.boton_aumentar, .boton_disminuir, .boton_eliminar', function(event) {
        event.preventDefault();
        const cartItemId = $(this).data('cart-item-id');
        const actionType = $(this).attr('class').split(' ')[1]; // Detecta el tipo de acción

        let url = '';
        if (actionType === 'boton_aumentar') {
            url = `/aumentar_del_carrito/${cartItemId}/`;
        } else if (actionType === 'boton_disminuir') {
            url = `/disminuir_del_carrito/${cartItemId}/`;
        } else if (actionType === 'boton_eliminar') {
            url = `/remove_from_cart/${cartItemId}/`;
        }

        $.ajax({
            url: url,
            type: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(data) {
                if (data.success) {
                    if (actionType === 'boton_eliminar') {
                        alert('Producto eliminado del carrito');
                    }
                    updateCartUI(data.cart_items, data.total);
                } else {
                    alert(data.message);
                }
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
            }
        });
    });
});
