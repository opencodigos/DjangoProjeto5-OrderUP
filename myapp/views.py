from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import login
from django.contrib import messages 
from .forms import (
    UserRegistrationForm, 
    RestaurantForm, 
    MenuItemForm, 
    ReservationForm
) 
from .models import Restaurant, Table, Reservation, MenuItem, Order, OrderItem
    
def home(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'home.html', {'restaurants': restaurants})


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registro realizado com sucesso!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'auth/register.html', {'form': form})


# Criar um restaurante
@login_required
def restaurant_create(request):
    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES) # Imagens
        if form.is_valid():
            restaurant = form.save(commit=False)
            restaurant.owner = request.user
            restaurant.save()
            messages.success(request, 'Restaurante criado com sucesso!')
            return redirect('restaurant_detail', pk=restaurant.pk)
    else:
        form = RestaurantForm()
    return render(request, 'restaurant_form.html', {'form': form})

# Editar um restaurante 
def restaurant_detail(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)    

    menu_by_category = {}
    for item in restaurant.menuitem_set.all():
        if item.category not in menu_by_category:
            menu_by_category[item.category] = []
        menu_by_category[item.category].append(item)

    context = {
        'restaurant': restaurant,
        'menu_by_category': menu_by_category,
    }

    return render(request, 'restaurant_detail.html', context) 
    
@login_required
def my_restaurants(request):
    restaurants = Restaurant.objects.filter(owner=request.user)
    return render(request, 'my_restaurants.html', {'restaurants': restaurants})
 

@login_required
def menu_item_create(request, restaurant_pk):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_pk)

    if request.user != restaurant.owner:
        messages.error(request, 'Você não tem permissão para adicionar itens ao cardápio.')
        return redirect('restaurant_detail', pk=restaurant_pk)

    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            menu_item = form.save(commit=False)
            menu_item.restaurant = restaurant
            menu_item.save()
            messages.success(request, 'Item adicionado ao cardápio com sucesso!')
            return redirect('restaurant_detail', pk=restaurant_pk)
    else:
        form = MenuItemForm()
    return render(request, 'menu_item_form.html', {'form': form, 'restaurant': restaurant})


@login_required
def reservation_create(request, restaurant_pk):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_pk)
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.restaurant = restaurant
            
            # Lógica para encontrar uma mesa disponível
            available_table = Table.objects.filter(
                restaurant=restaurant,
                capacity__gte=form.cleaned_data['guests']
            ).first()
            
            if available_table:
                reservation.table = available_table # Mesa 5 disponivel
                reservation.save()
                messages.success(request, 'Reserva realizada com sucesso!')
                return redirect('reservation_detail', pk=reservation.pk)
            else:
                messages.error(request, 'Não há mesas disponíveis para o número de pessoas solicitado.')
    else:
        form = ReservationForm()
    return render(request, 'reservation_form.html', 
                  {'form': form, 'restaurant': restaurant})

@login_required
def reservation_detail(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    return render(request, 'reservation_detail.html', {'reservation': reservation})


@login_required
def my_reservations(request):
    reservations = Reservation.objects.filter(
        user=request.user).order_by('-date', '-time')
    return render(request, 'my_reservations.html', {'reservations': reservations})



@login_required
def reservation_manage(request, restaurant_pk):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_pk)

    # Verifica se o usuário é o dono do restaurante
    if request.user != restaurant.owner:
        messages.error(request, 'Você não tem permissão para gerenciar \
                       as reservas deste restaurante.')
        return redirect('restaurant_detail', pk=restaurant_pk)

    # Filtro por status
    status_filter = request.GET.get('status')
    reservations = Reservation.objects.filter(restaurant=restaurant)

    if status_filter:
        reservations = reservations.filter(status=status_filter)

    # Contadores para o menu
    pending_count = Reservation.objects.filter(
        restaurant=restaurant, status='pendente').count()
    confirmed_count = Reservation.objects.filter(
        restaurant=restaurant, status='confirmada').count()
    cancelled_count = Reservation.objects.filter(
        restaurant=restaurant, status='cancelada').count()

    context = {
        'restaurant': restaurant,
        'reservations': reservations.order_by('-date', '-time'),
        'status_filter': status_filter,
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'cancelled_count': cancelled_count,
    }

    return render(request, 'reservation_manage.html', context) 
    
    
@login_required
def reservation_update_status(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)

    # Verifica se o usuário é o dono do restaurante ou superusuário
    if not request.user.is_superuser and request.user != reservation.restaurant.owner:
        messages.error(request, 'Você não tem permissão para atualizar esta reserva.')
        return redirect('reservation_detail', pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status') # pode ser 'confirmada' ou 'cancelada'
        if new_status in ['confirmada', 'cancelada']:
            reservation.status = new_status
            reservation.save()

            # Enviar notificação ao cliente
            status_display = 'confirmada' if new_status == 'confirmada' else 'rejeitada'
            messages.success(request, f'Reserva {status_display} com sucesso!')
        else:
            messages.error(request, 'Status inválido.')

    return redirect('reservation_detail', pk=pk)

def add_items_in_order(order, menu_items, quantities):
    """Adiciona itens ao pedido e retorna o total"""
    total = 0
    for item_id, quantity in zip(menu_items, quantities): # esse zip junta as listas
        if quantity and int(quantity) > 0:
            menu_item = MenuItem.objects.get(id=item_id)
            quantity = int(quantity)
            price = menu_item.price * quantity
            
            OrderItem.objects.create(
                order=order,
                item=menu_item,
                quantity=quantity,
                price=price
            )
            total += price
    return total


@login_required
def create_order(request, reservation_pk):
    """ 
    1. Pega a reserva
    2. Se POST:
       - Cria order
       - Adiciona itens (função separada)
       - Salva total
       - Redireciona
    3. Se GET:
       - Mostra formulário
    """
    reservation = get_object_or_404(Reservation, pk=reservation_pk)
    
    if request.method == 'POST':
        menu_items = request.POST.getlist('menu_items') # ids itens
        quantities = request.POST.getlist('quantities') # quantidades

        print(menu_items, quantities)  # Debugging line

        if menu_items and quantities:
            order = Order.objects.create(
                user=request.user,
                restaurant=reservation.restaurant,
                reservation=reservation
            )
            
            total = add_items_in_order(order, menu_items, quantities)
            order.total = total
            order.save()
            
            messages.success(request, 'Pedido realizado com sucesso!')
            return redirect('order_detail', pk=order.pk)
        else:
            messages.error(request, 'Selecione pelo menos um item para \
                           fazer o pedido.')

    menu_items = MenuItem.objects.filter(
        restaurant=reservation.restaurant, available=True)
    return render(request, 'order_create.html', {
        'reservation': reservation,
        'menu_items': menu_items
    })



@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'order_detail.html', {'order': order})


@login_required
def order_manage(request, restaurant_pk):
    """Gerencia pedidos de um restaurante"""
    restaurant = get_object_or_404(Restaurant, pk=restaurant_pk)

    # Verifica permissão
    if request.user != restaurant.owner and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão.')
        return redirect('restaurant_detail', pk=restaurant_pk)

    # Pega todos os pedidos do restaurante
    all_orders = Order.objects.filter(restaurant=restaurant)
    
    # Filtra por status se solicitado
    status_filter = request.GET.get('status')
    if status_filter:
        orders = all_orders.filter(status=status_filter)
    else:
        orders = all_orders

    # Conta pedidos por status
    from django.db.models import Count
    status_counts = all_orders.values('status').annotate(count=Count('id'))
    counts = {item['status']: item['count'] for item in status_counts}

    context = {
        'restaurant': restaurant,
        'orders': orders.order_by('-created_at'),
        'status_filter': status_filter,
        'pending_count': counts.get('pendente', 0),
        'preparing_count': counts.get('preparando', 0),
        'ready_count': counts.get('pronto', 0),
        'delivered_count': counts.get('entregue', 0),
        'cancelled_count': counts.get('cancelado', 0),
    }

    return render(request, 'order_manage.html', context)


@login_required
def order_update_status(request, pk):
    """Atualiza o status de um pedido"""
    order = get_object_or_404(Order, pk=pk)

    # Verifica permissão
    if request.user != order.restaurant.owner and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão.')
        return redirect('order_detail', pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status') # cancelado, preparando, pronto, entregue
        print(f'Novo status recebido: {new_status}')  # Linha de depuração
        
        # Lista de status válidos
        valid_statuses = ['pendente', 'preparando', 'pronto', 'entregue', 'cancelado']
        
        if new_status in valid_statuses:
            order.status = new_status
            order.save()
            messages.success(request, f'Pedido atualizado para: {order.get_status_display()}')
        else:
            messages.error(request, 'Status inválido.')

    return redirect('order_manage', restaurant_pk=order.restaurant.pk)

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_orders.html', {'orders': orders})