from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import login
from django.contrib import messages 
from .forms import UserRegistrationForm, RestaurantForm, MenuItemForm
from .models import Restaurant
    
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
