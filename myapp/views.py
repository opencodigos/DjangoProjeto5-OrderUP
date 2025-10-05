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
from .models import Restaurant, Table, Reservation
    
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