# Django Projeto 5 - Sistema de Reservas para Restaurantes

- **Funcionalidades**:
    - ✅ **Reserva de mesas**: Usuários escolhem data, hora e quantidade de pessoas para a reserva.
    - ✅ **Cardápio digital**: Restaurantes podem criar menus dinâmicos, com fotos e descrições.
    - ✅ **Pedido online**: Os clientes podem realizar pedidos diretamente pelo site (para consumo no local ou para entrega).
    - ✅ **Painel administrativo**: Restaurantes podem gerenciar reservas, pedidos.

 repo_completo: https://github.com/opencodigos/DjangoProjeto5-OrderUp

## ⚙️ Configuração do Ambiente

**Configuração Base Django**: https://opencodigo.com/blog/configuracao-padrao-simples-para-usar-no-django

### Pré-requisitos

- Python
- pip (gerenciador de pacotes Python)
- Git

### Configuração Inicial

1. **Crie e ative o ambiente virtual**

```bash
# Windows
python -m venv venv
venv\\Scripts\\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate

```

1. **Instale as dependências**

```bash
pip install django
pip install pillow
pip install django-crispy-forms
pip install crispy-bootstrap5 

# Ou se tiver requirements.txt
pip freeze -r requirements.txt

# Grava um requirements
pip freeze > requirements.txt
```

### Criar SuperUsuário

```html
python manage.py migrate
python manage.py createsuperuser
```
 
<details>
<summary>⚙️ Configurações (Settings)</summary>
settings.py

```python
# Vamos utilizar o crispy
INSTALLED_APPS = [
    ...
    'crispy_forms', # Adicionar crispy 
    'crispy_bootstrap5', # Adicionar crispy bootstrap
]

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5' # Template bootstrap5 
CRISPY_TEMPLATE_PACK = 'bootstrap5' 

# Configuração de Mensagens
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-secondary',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# Configurações de Login
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

```

Testamos:

```tsx
python manage.py runserver
```
</details>


<details>
<summary>📊 Modelos (Models)</summary> 

### Restaurant (Restaurante)

```python
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone

# Tabela de restaurantes
class Restaurant(models.Model):
    name = models.CharField('Nome', max_length=100)
    description = models.TextField('Descrição')
    address = models.CharField('Endereço', max_length=200)
    phone = models.CharField('Telefone', max_length=20)
    opening_time = models.TimeField('Horário de Abertura')
    closing_time = models.TimeField('Horário de Fechamento')
    image = models.ImageField('Imagem', upload_to='restaurants/', null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Proprietário')
    created_at = models.DateTimeField('Criado em', default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '1 - Restaurante'
        verbose_name_plural = '1 - Restaurantes'
        ordering = ['name']

```

### Table (Mesa)

```python
# Tabela de mesas (vinculada a restaurantes)
class Table(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, verbose_name='Restaurante')
    number = models.IntegerField('Número da Mesa')
    capacity = models.IntegerField('Capacidade', validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = '2 - Mesa'
        verbose_name_plural = '2 - Mesas'
        unique_together = ['restaurant', 'number']

    def __str__(self):
        return f'Mesa {self.number} - {self.restaurant.name}'

```

### MenuItem (Item do Menu)

```python
# Cardápio e Itens do Cardápio (vinculado a restaurantes)
class MenuItem(models.Model):
    CATEGORY_CHOICES = [
        ('entrada', 'Entrada'),
        ('prato_principal', 'Prato Principal'),
        ('sobremesa', 'Sobremesa'),
        ('bebida', 'Bebida'),
    ]

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, verbose_name='Restaurante')
    name = models.CharField('Nome', max_length=100)
    description = models.TextField('Descrição')
    price = models.DecimalField('Preço', max_digits=10, decimal_places=2)
    category = models.CharField('Categoria', max_length=20, choices=CATEGORY_CHOICES)
    image = models.ImageField('Imagem', upload_to='menu_items/', null=True, blank=True)
    available = models.BooleanField('Disponível', default=True)

    def __str__(self):
        return f'{self.name} - {self.restaurant.name}'

    class Meta:
        verbose_name = '3 - Item do Cardápio'
        verbose_name_plural = '3 - Itens do Cardápio'
        ordering = ['category', 'name']

```

### Reservation (Reserva)

```python
# Tabela de reservas (vinculada a usuários, restaurantes e mesas)
class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('concluida', 'Concluída'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Cliente')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, verbose_name='Restaurante')
    table = models.ForeignKey(Table, on_delete=models.CASCADE, verbose_name='Mesa')
    date = models.DateField('Data')
    time = models.TimeField('Horário')
    guests = models.IntegerField('Número de Pessoas', validators=[MinValueValidator(1)])
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pendente')
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    notes = models.TextField('Observações', blank=True, null=True)

    def __str__(self):
        return f'Reserva de {self.user.get_full_name()} - {self.restaurant.name}'

    class Meta:
        verbose_name = '4 - Reserva'
        verbose_name_plural = '4 - Reservas'
        ordering = ['-date', '-time']

```

### Order (Pedido)

```python
# Tabela de pedidos (vinculada a usuários, restaurantes, reservas e itens do cardápio)
class Order(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('preparando', 'Preparando'),
        ('pronto', 'Pronto'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Cliente')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, verbose_name='Restaurante')
    reservation = models.ForeignKey(Reservation, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Reserva')
    items = models.ManyToManyField(MenuItem, through='OrderItem', verbose_name='Itens')
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pendente')
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    total = models.DecimalField('Total', max_digits=10, decimal_places=2, default=0)
    notes = models.TextField('Observações', blank=True, null=True)

    def __str__(self):
        return f'Pedido #{self.id} - {self.user.get_full_name()}'

    class Meta:
        verbose_name = '5 - Pedido'
        verbose_name_plural = '5 - Pedidos' 
        ordering = ['-created_at']

```

### OrderItem (Item do Pedido)

```python
# Tabela intermediária para itens do pedido
# Permite armazenar quantidade e preço no momento do pedido (para histórico e pagamento)
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Pedido')
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, verbose_name='Item')
    quantity = models.IntegerField('Quantidade', validators=[MinValueValidator(1)])
    price = models.DecimalField('Preço', max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Sempre atualiza o preço baseado no item e quantidade
        if self.item:
            self.price = self.item.price * self.quantity
        
        # Salva o item
        super().save(*args, **kwargs)
        
        # Atualiza o total do pedido
        if self.order:
            total = sum(item.price for item in self.order.orderitem_set.all())
            self.order.total = total
            self.order.save()

    def __str__(self):
        return f'{self.quantity}x {self.item.name}'

    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'
        ordering = ['order']
```

```tsx
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### Configuração no admin

Jeito simples para visualizar os modelos no django admin.

```html
from django.contrib import admin 
from .models import (
	Restaurant, Table, MenuItem, Reservation, Order, OrderItem)

admin.site.register(Restaurant)
admin.site.register(Table)
admin.site.register(MenuItem)
admin.site.register(Reservation)
admin.site.register(Order)
admin.site.register(OrderItem)
```

Para deixar a visualização um pouco melhor pode abordar essas configurações. 

https://docs.djangoproject.com/en/5.1/ref/contrib/admin/

```python
from django.contrib import admin
from django.utils.html import format_html
from .models import Restaurant, Table, MenuItem, Reservation, Order, OrderItem

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'phone', 'opening_time', 'closing_time', 'created_at']
    list_filter = ['created_at', 'owner']
    search_fields = ['name', 'address', 'phone', 'owner__username']
    date_hierarchy = 'created_at' #  filtrar registros por data em um modelo que possui um campo de data/hora

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['restaurant', 'number', 'capacity']
    list_filter = ['restaurant', 'capacity']
    search_fields = ['restaurant__name']

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'restaurant', 'category', 'price', 'available', 'display_image']
    list_filter = ['restaurant', 'category', 'available']
    search_fields = ['name', 'description', 'restaurant__name']
    list_editable = ['available', 'price']
		
		# Cria uma função para fazer algum tratamento na coluna especifica.
		# Nesse caso vou exibir o logo da imagem para melhor visualização
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" height="50"/>', obj.image.url)
        return "-"
    display_image.short_description = 'Imagem'

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['user', 'restaurant', 'date', 'time', 'guests', 'status', 'created_at']
    list_filter = ['status', 'date', 'restaurant']
    search_fields = ['user__username', 'restaurant__name', 'notes']
    date_hierarchy = 'date'
    readonly_fields = ['created_at'] # campos que não podem ser editados
		
		# Não necessariamente precisa, por que geralmente somente superuser tem acesso admin.
		# coloquei essa função para mostrar como podemos customizar ate lista de obejtos de acordo com usuário autenticado.
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Se não for superusuário, só vê reservas dos seus restaurantes
            return qs.filter(restaurant__owner=request.user)
        return qs

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'restaurant', 'total', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'restaurant']
    search_fields = ['user__username', 'restaurant__name']
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]
    readonly_fields = ['total', 'created_at']
		
		# Temporario
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Se não for superusuário, só vê pedidos dos seus restaurantes
            return qs.filter(restaurant__owner=request.user)
        return qs
```

Vou deixar alguns fixture.data.json iniciais para gente testar ok ?

[fixture.data.json](attachment:797d6c88-9324-4765-aee2-3e29be56cb97:fixture.data.json)

```html
python manage.py loaddata fixture.data.json 
``` 
</details> 


<details> 
<summary>📝 Forms / 🔄 Views / 🔗 Urls / 🎨 Templates</summary>

<details> 
    <summary>Home</summary> 

    views>index

    ```tsx
    from .models import Restaurant

    def home(request):
        restaurants = Restaurant.objects.all()
        return render(request, 'home.html', {'restaurants': restaurants})
    ```

    templates>index.html=home.html

    urls>index=home

    templates>base>index=home

    home>

    ```tsx
    <div class="bg-light rounded-3 p-5 mb-5 text-center">
        <h1 class="display-5 fw-bold">Bem-vindo ao OrderUP</h1>
        <p class="lead text-muted">Sistema de reservas para restaurantes</p>
        {% if user.is_authenticated %}
            <a href="#restaurant_create" class="btn btn-primary btn-lg mt-3">
                <i class="fas fa-plus-circle"></i> Cadastrar Restaurante
            </a>
        {% else %}
            <a href="#register" class="btn btn-primary btn-lg mt-3">
                <i class="fas fa-rocket"></i> Começar Agora
            </a>
        {% endif %}
    </div>

    <div class="row">
        {% for restaurant in restaurants %}
        <div class="col-md-3 col-sm-6 mb-4">
            <div class="card h-100 shadow-sm border-0">
                {% if restaurant.image %}
                    <img src="{{ restaurant.image.url }}" class="card-img-top" alt="{{ restaurant.name }}" style="height: 200px; object-fit: cover;">
                {% else %}
                    <div class="bg-light text-center d-flex align-items-center justify-content-center" style="height: 200px;">
                        <i class="fas fa-utensils fa-3x text-muted"></i>
                    </div>
                {% endif %}
                <div class="card-body">
                    <h5 class="card-title">{{ restaurant.name }}</h5>
                    <p class="card-text text-muted">{{ restaurant.description|truncatewords:15 }}</p>
                </div>
                <div class="card-footer bg-white border-0 d-flex justify-content-between align-items-center">
                    <a href="#" class="btn btn-outline-primary btn-sm">Ver Detalhes</a>
                    <small class="text-muted">
                        <i class="fas fa-clock"></i> {{ restaurant.opening_time|time:"H:i" }} - {{ restaurant.closing_time|time:"H:i" }}
                    </small>
                </div>
            </div>
        </div>
        {% empty %}
        <div class="col-12">
            <div class="alert alert-info text-center" role="alert">
                <i class="fas fa-info-circle"></i> Nenhum restaurante cadastrado ainda.
            </div>
        </div>
        {% endfor %}
    </div>
    ```

    base>messages

    ```markdown
    {% if messages %}
    <div class="container mt-3">
        {% for message in messages %}
        <div class="alert {{ message.tags }} alert-dismissible fade show" role="alert">
            {{ message }}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
        {% endfor %}
    </div>
    {% endif %}
    ```

    ### Registro / Login

    ### Login

    https://docs.djangoproject.com/en/5.2/topics/auth/default/#module-django.contrib.auth.views

    Adicione as rotas de autenticação:

    ```markdown
    from django.contrib.auth.views import LoginView, LogoutView

    path('login/', LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    ```

    templates>auth>login.html

    ```tsx
    {% extends 'base.html' %}
    {% block title %}Login{% endblock %}
    {% load crispy_forms_tags %}
    {% block content %} 
    <div class="col-md-6 offset-md-3">
        <h2 class="text-center mb-4">Login</h2>
        <form method="post">  
            {% csrf_token %}
            {{ form.as_p }}
            <button type="submit" class="btn btn-primary w-100">Login</button>
        </form>
        <hr>
        <p class="text-center">Já tem uma conta? <a href="#register">criar conta</a></p> 
    </div>
    {% endblock %}
    ```

    templates>base

    base>tag:nav

    ```tsx
    {% if user.is_authenticated %}
    <li class="nav-item dropdown">
        <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button" data-bs-toggle="dropdown">
            <i class="fas fa-user"></i> {{ user.get_full_name|default:user.username }}
        </a>
        <ul class="dropdown-menu dropdown-menu-end">
            <li>
                <a class="dropdown-item" href="#my_reservations">
                    <i class="fas fa-calendar"></i> Minhas Reservas
                </a>
            </li>
            <li>
                <a class="dropdown-item" href="#my_orders">
                    <i class="fas fa-shopping-bag"></i> Meus Pedidos
                </a>
            </li>
            {% if user.is_superuser %}
                <li><hr class="dropdown-divider"></li>
                <li>
                    <a class="dropdown-item" href="/admin/">
                        <i class="fas fa-cog"></i> Admin
                    </a>
                </li>
            {% endif %}
            <li><hr class="dropdown-divider"></li>
            <li>
                <a class="dropdown-item text-danger">
                
                <form method="post" action="{% url 'logout' %}" class="d-inline">
                    {% csrf_token %}
                    <button type="submit" class="dropdown-item text-danger" style="border: none; background: none; cursor: pointer;">
                        <i class="fas fa-sign-out-alt"></i> Sair
                    </button>
                </form>

                </a>
            </li>
        </ul>
    </li>
    {% else %}
    <li class="nav-item">
        <a class="btn btn-success" href="{% url 'login' %}">
            <i class="fas fa-sign-in-alt"></i> Entrar
        </a>
    </li> 
    {% endif %}
    ```

    ### Registro

    Vamos criar um formulário de registro de usuário para que clientes possam pedir uma reserva em algum restaurante e tambem cadastrar seu restaurante no sistema para receber essas reservas. 

    Inicialmente vou deixar essa inscrição de restaurante open para qualquer cliente consiga cadastrar e gerenciar seu restaurante. Detalhe um cliente pode ter mais de um restaurante.

    forms.py

    ```python
    from django import forms
    from django.contrib.auth.forms import UserCreationForm
    from django.contrib.auth.models import User
    from crispy_forms.helper import FormHelper
    from crispy_forms.layout import Layout, Row, Column, Submit

    class UserRegistrationForm(UserCreationForm):   
        email = forms.EmailField(required=True, label="Endereço de Email")
        first_name = forms.CharField(required=True, label="Primeiro Nome")
        last_name = forms.CharField(required=True, label="Sobrenome")
        
        class Meta:
            model = User
            fields = ('username', 'first_name', 'last_name', 'email', 'password1','password2')
            labels = {
                'username': 'Nome de Usuário',
                'password1': 'Senha',
                'password2': 'Confirme a Senha',
            }
            
            
        def __init__(self, *args, **kwargs):
            super(UserRegistrationForm, self).__init__(*args, **kwargs)
            
            self.fields['username'].help_text = None
            self.fields['password1'].help_text = None
            self.fields['password2'].help_text = None
            
            self.helper = FormHelper()
            self.helper.form_method = 'post' 
            self.helper.layout = Layout(
                Row(
                    Column('username', css_class='col-md-6'),
                    Column('email', css_class='col-md-6'),
                ),
                Row(
                    Column('first_name', css_class='col-md-6'),
                    Column('last_name', css_class='col-md-6'),
                ), 
                Row(
                    Column('password1', css_class='col-md-6'),
                    Column('password2', css_class='col-md-6'),
                ),
                Submit('submit', 'Registrar', css_class='btn btn-primary w-100'),
            )

    ```

    ### RegisterView

    views.py

    ```python
    from django.shortcuts import render, redirect 
    from django.contrib.auth import login
    from django.contrib import messages 
    from .forms import UserRegistrationForm 

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
        return render(request, 'restaurant/auth/register.html', {'form': form})

    ```

    ### Template (auth/register.html)

    ```html
    {% extends 'base.html' %}
    {% block title %}Registro{% endblock %}
    {% load crispy_forms_tags %}
    {% block content %} 
    <div class="col-md-6 offset-md-3">
        <h2 class="text-center mb-4">Criar Conta</h2>
        <form method="post" enctype="multipart/form-data">  
            {% crispy form %}  
        </form>
        <hr>
        <p class="text-center">Já tem uma conta? <a href="{% url 'login' %}">Entre aqui</a></p> 
    </div>
    {% endblock %}
    ```

    ### urls.py

    ```python
    path('register/', register, name='register'),
    ```

    index 

    ```html
    <a href="{% url 'register' %}" class="btn btn-primary">Comece Agora</a>
    ```
</details> 

<details> 
    <summary>Restaurante</summary>

    ### forms

    Cadastrar um restaurante

    ```python
    from crispy_forms.layout import Layout, Row, Column, Field, Submit, Button, HTML
    from .models import Restaurant

    class RestaurantForm(forms.ModelForm):
        class Meta:
            model = Restaurant
            fields = ['name', 'description', 'address', 'phone', 'opening_time', 'closing_time', 'image']
            widgets = {
                'opening_time': forms.TimeInput(attrs={'type': 'time'}),
                'closing_time': forms.TimeInput(attrs={'type': 'time'}),
            }

        def __init__(self, *args, **kwargs):
            super(RestaurantForm, self).__init__(*args, **kwargs)

            self.helper = FormHelper()
            self.helper.form_method = 'post'
            self.helper.attrs = {'enctype': 'multipart/form-data', 'novalidate': ''}
            self.helper.layout = Layout(
                Row(
                    Column(
                        HTML(''' 
                            <div class="mb-3">
                                <p class="fw-bold">Preview:</p>
                                <img src="
                                    {% if form.instance.image %}
                                        {{ form.instance.image.url }}{% else %}https://placehold.co/400x300{% endif %}" 
                                    alt="Preview" 
                                    class="img-thumbnail image-preview w-100" 
                                    style="height: 200px; object-fit: cover;">
                            </div>  
                        '''),
                        'image',
                        css_class='col-md-4 mb-3'
                    ), 
                    Column(
                        'name',
                        Field('description', rows=3),
                        Row(
                            Column('address', css_class='col-md-8'),
                            Column('phone', css_class='col-md-4'),
                        ),
                        Row(
                            Column('opening_time', css_class='col-md-6'),
                            Column('closing_time', css_class='col-md-6'),
                        ),
                        css_class='col-md-8 mb-3'
                    ),
                ), 
                Row(
                    Column(
                        HTML('<a href="{% url \'home\' %}" class="btn btn-secondary"><i class="fas fa-arrow-left"></i> Voltar</a>'),
                        css_class='col-auto'
                    ),
                    Column(
                        Submit('submit', '{% if form.instance.pk %}Salvar Alterações{% else %}Cadastrar Restaurante{% endif %}', css_class='btn btn-primary'),
                        css_class='col-auto ms-auto'
                    ),
                ),
            )
    ```

    ### Views

    Para criar / Editar

    ```python
    from django.shortcuts import render, redirect, get_object_or_404
    from django.contrib.auth.decorators import login_required
    from .forms import RestaurantForm

    # Criar um restaurante
    @login_required
    def restaurant_create(request):
        if request.method == 'POST':
            form = RestaurantForm(request.POST, request.FILES)
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
        context = {
            'restaurant': restaurant, 
        }
        return render(request, 'restaurant_detail.html', context) 
        
    @login_required
    def my_restaurants(request):
        restaurants = Restaurant.objects.filter(owner=request.user)
        return render(request, 'my_restaurants.html', {'restaurants': restaurants})
    ```

    ### Templates

    **Create**

    templates>restaurant_form.html

    ```html
    {% extends 'base.html' %}
    {% block title %}Cadastro de Restaurante{% endblock %}
    {% load crispy_forms_tags %}
    {% block content %} 
    <div class="col-md-8 offset-md-2">
        <h2 class="text-center mb-4">Cadastro de Restaurante</h2>
        {% crispy form %}
    </div>
    {% endblock %}
    {% block extra_js %} 
    <script type="text/javascript">
        // Preview da imagem antes do upload
        document.addEventListener('DOMContentLoaded', function() {
            const imageInput = document.getElementById('id_image');
            const imagePreview = document.querySelector('.image-preview');
            
            if (imageInput && imagePreview) {
                imageInput.addEventListener('change', function(e) {
                    const file = e.target.files[0];
                    if (file) {
                        const reader = new FileReader();
                        reader.onload = function(e) {
                            imagePreview.src = e.target.result;
                            imagePreview.style.height = '200px';
                            imagePreview.style.objectFit = 'cover';
                        }
                        reader.readAsDataURL(file);
                    }
                });
            }
        });
    </script>
    {% endblock %}
    ```

    **Detalhe**

    templates>restaurant_detail.html

    ```html
    {% extends 'base.html' %}
    {% block title %}{{ restaurant.name }}{% endblock %}
    {% load static %}
    {% block content %}

    <div class="row mb-4">

        <div class="col-md-8"> 

            <div class="row">

                <div class="col-md-4">
                    <img src="{% if restaurant.image %}{{ restaurant.image.url }}{% else %}https://placehold.co/400x300{% endif %}" 
                        alt="Preview" 
                        class="img-thumbnail image-preview" 
                        style="height: 200px; object-fit: cover;">
                </div>

                <div class="col-md-8">
                    <h1>{{ restaurant.name }}</h1>
                    <p class="lead">{{ restaurant.description }}</p>
                
                    <div class="mb-3">
                        <p><i class="fas fa-map-marker-alt"></i> {{ restaurant.address }}</p>
                        <p><i class="fas fa-phone"></i> {{ restaurant.phone }}</p>
                        <p><i class="fas fa-clock"></i> {{ restaurant.opening_time|time:"H:i" }} - {{ restaurant.closing_time|time:"H:i" }}</p>
                    </div>
                </div>

            </div>

        </div>
        
        <!-- Editar ou reservar -->
        <div class="col-md-4">

            {% if user.is_authenticated %}
                <a href="#" class="btn btn-primary btn-lg w-100 mb-2">
                    <i class="fas fa-calendar-plus"></i> Fazer Reserva
                </a>
                {% if user == restaurant.owner %}
                    <a href="#" class="btn btn-warning w-100">
                        <i class="fas fa-edit"></i> Editar
                    </a>
                {% endif %}
            {% else %}
                <a href="{% url 'login' %}" class="btn btn-primary btn-lg w-100">
                    <i class="fas fa-sign-in-alt"></i> Entre para Reservar
                </a>
            {% endif %}

        </div>
    </div>

    <div class="row">
        <div class="col-12">
            <h2 class="mb-3">Cardápio</h2>
            {% if user == restaurant.owner %}
                <a href="#" class="btn btn-success mb-3">
                    <i class="fas fa-plus"></i> Adicionar Item
                </a>
            {% endif %}
            <p class="text-muted">Cardápio em breve...</p>
        </div>
    </div>

    {% endblock %}
    ```

    **Lista** 

    templates>my_restaurants.html

    ```tsx
    {% extends 'base.html' %}
    {% block title %}Meus Restaurantes{% endblock %}
    {% load static %}
    {% block content %} 
    <div class="d-flex justify-content-between align-items-center">
        <h1>Meus Restaurantes</h1>
        <a href="{% url 'restaurant_create' %}" class="btn btn-primary">
            <i class="fas fa-plus"></i> Cadastrar Novo
        </a>
    </div> 
    {% if restaurants %}
    <div class="row">
        {% for restaurant in restaurants %}
        <div class="col-md-4 mb-4"> 
            <div class="card h-100">
                <h5 class="card-title">{{ restaurant.name }}</h5>
                <p class="card-text text-muted">{{ restaurant.description|truncatewords:15 }}</p>
                <div class="mb-2">
                    <small class="text-muted">
                        <i class="fas fa-clock"></i> {{ restaurant.opening_time|time:"H:i" }} - {{ restaurant.closing_time|time:"H:i" }}
                    </small>
                </div>
                <div class="d-flex gap-2">
                    <a href="{% url 'restaurant_detail' pk=restaurant.pk %}" class="btn btn-sm btn-outline-primary">
                        <i class="fas fa-eye"></i> Ver
                    </a>
                    <a href="#" class="btn btn-sm btn-outline-warning">
                        <i class="fas fa-edit"></i> Editar
                    </a>
                    <a href="#" class="btn btn-sm btn-outline-info">
                        <i class="fas fa-calendar-check"></i> Reservas
                    </a>
                </div> 
            </div> 
        </div>
        {% endfor %}
    </div>
    {% else %}
    <div class="alert alert-info text-center">
        <i class="fas fa-info-circle"></i> Você ainda não cadastrou nenhum restaurante.
        <br>
        <a href="{% url 'restaurant_create' %}" class="btn btn-primary mt-3">
            <i class="fas fa-plus"></i> Cadastrar Primeiro Restaurante
        </a>
    </div>
    {% endif %} 
    {% endblock %}

    ```

    ### Urls.py

    ```python
    from .views import home, register, restaurant_create, restaurant_detail, my_restaurants
    
    path('restaurant/create/', restaurant_create, name='restaurant_create'),
    path('restaurant/<int:pk>/', restaurant_detail, name='restaurant_detail'),
    path('my-restaurants/', my_restaurants, name='my_restaurants'), 

    ```

    ### **Template**

    **home.html**

    ```html
    <a href="{% url 'restaurant_create' %}" class="btn btn-primary">Cadastrar Meu Restaurante</a>
    ```

    **base.html Navbar**

    ```python
    <!-- Meus Restaurantes -->
    {% if user.is_authenticated and user.restaurant_set.exists %}
    <li class="nav-item">
        <a class="nav-link" href="#my_restaurants">
            <i class="fas fa-utensils"></i> Meus Restaurantes
        </a>
    </li>
    {% endif %}
    ```

    home.html

    ```tsx
    <a href="{% url 'restaurant_detail' pk=restaurant.pk %}" class="btn btn-outline-primary btn-sm">Ver Detalhes</a>
    ```
</details>

<details>
    <summary>Restaurante - Menu Itens</summary>

    ### forms

    ```python
    class MenuItemForm(forms.ModelForm):
        class Meta:
            model = MenuItem
            fields = ['name', 'description', 'price', 'category', 'image', 'available']
            widgets = {
                'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
                'description': forms.Textarea(attrs={'rows': 3}),
            }

        def __init__(self, *args, **kwargs):
            super(MenuItemForm, self).__init__(*args, **kwargs)

            self.helper = FormHelper()
            self.helper.form_method = 'post'
            self.helper.attrs = {'enctype': 'multipart/form-data', 'novalidate': ''}
            self.helper.layout = Layout(
                Row( 
                    Column(
                        HTML(''' 
                            <div class="mb-3">
                                <p class="fw-bold">Imagem atual:</p>
                                <img src="{% if form.instance.image %}{{ form.instance.image.url }}{% else %}https://placehold.co/400x300{% endif %}" 
                                    alt="Preview" 
                                    class="img-thumbnail image-preview w-100" 
                                    style="height: 200px; object-fit: cover;"> 
                            </div> 
                        '''),
                        'image',
                        css_class='col-md-4 mb-3'
                    ), 
                    Column( 
                        'name',
                        'description',
                        Row(
                            Column('category', css_class='col-md-6'), 
                            Column('price', css_class='col-md-6'),
                        ),
                        'available',
                        css_class='col-md-8 mb-3'
                    ),
                ), 
                Row(
                    Column(
                        HTML('<a href="{% url \'restaurant_detail\' pk=restaurant.pk %}" class="btn btn-secondary"><i class="fas fa-arrow-left"></i> Voltar</a>'),
                        css_class='col-auto'
                    ),
                    Column(
                        Submit('submit', '{% if form.instance.pk %}Salvar Alterações{% else %}Adicionar Item{% endif %}', css_class='btn btn-primary'),
                        css_class='col-auto ms-auto'
                    ),
                ),
            )
    ```

    ### Views

    ```python
    from .forms import MenuItemForm

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

    ```

    **Templates**

    templates/menu_item_form.html

    ```html
    {% extends 'base.html' %}
    {% load crispy_forms_tags %}
    {% block title %}{% if form.instance.pk %}Editar{% else %}Adicionar{% endif %} Item ao Cardápio{% endblock %}

    {% block content %}
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <h2 class="mb-4">{% if form.instance.pk %}Editar{% else %}Adicionar{% endif %} Item ao Cardápio</h2>
            {% crispy form %}
        </div>
    </div>
    {% endblock %}

    {% block extra_js %}
    <script type="text/javascript">
        // Preview da imagem antes do upload
        document.addEventListener('DOMContentLoaded', function() {
            const imageInput = document.getElementById('id_image');
            const imagePreview = document.querySelector('.image-preview');
            
            if (imageInput) {
                imageInput.addEventListener('change', function(e) {
                    const file = e.target.files[0];
                    if (file) {
                        const reader = new FileReader();
                        reader.onload = function(e) {
                            if (imagePreview) {
                                imagePreview.src = e.target.result;
                            } else {
                                // Cria preview se não existir
                                const preview = document.createElement('img');
                                preview.src = e.target.result;
                                preview.className = 'img-thumbnail image-preview mt-2';
                                preview.style.maxHeight = '200px';
                                imageInput.parentElement.appendChild(preview);
                            }
                        }
                        reader.readAsDataURL(file);
                    }
                });
            }
        });
    </script>
    {% endblock %}
    ```

    ### Urls.py

    ```python
    path('restaurant/<int:restaurant_pk>/menu/add/', menu_item_create, name='menu_item_create'), 
    ```

    restaurant_detail.html

    ```python
    <h2 class="mb-4">Cardápio</h2>
    {% if user == restaurant.owner %}
        <a href="{% url 'menu_item_create' restaurant_pk=restaurant.pk %}" class="btn btn-success mb-3">
            <i class="fas fa-plus"></i> Adicionar Item ao Cardápio
        </a>
    {% endif %}
    ```

    **Alterações:** 

    Adicionar uma lista na pagina de detalhes do restaurante.

    **Views.py** 

    ```python
    from .models import MenuItem

    def restaurant_detail(request, pk):
        restaurant = get_object_or_404(Restaurant, pk=pk)
        menu_items = MenuItem.objects.filter(restaurant=restaurant)

        menu_by_category = {}
        for item in menu_items:
            if item.category not in menu_by_category:
                menu_by_category[item.category] = []
            menu_by_category[item.category].append(item)

        context = {
            'restaurant': restaurant,
            'menu_by_category': menu_by_category,
        }
        return render(request, 'restaurant_detail.html', context)
    ```

    **Template**

    E no template a gente adiciona um **`{% for category, items in menu_by_category.items %}`** para ****listar os itens.

    restaurant_detail.html

    ```html
    {% if menu_by_category %}
    {% for category, items in menu_by_category.items %}
    <h4 class="mt-4 mb-3">{{ category|title }}</h4>
    <div class="row g-2">
        {% for item in items %}
            <div class="col-md-3">
                <div class="d-flex bg-light p-3 rounded"> 
                    <img src="{% if item.image %}{{ item.image.url }}{% else %}https://placehold.co/400x300{% endif %}"
                            class="rounded mb-2" 
                            alt="{{ item.name }}" 
                            style="width: 100px; height: 100px; object-fit: cover;">
                    
                    <div class="ms-4">
                        <h6 class="mb-1">{{ item.name }}</h6>
                        <p class="text-muted small mb-2">{{ item.description|truncatewords:10 }}</p>
                        <div class="mt-auto">
                            <strong class="text-success">R$ {{ item.price }}</strong>
                            {% if not item.available %}
                                <span class="badge bg-danger ms-2">Indisponível</span>
                            {% endif %}
                        </div>
                        
                    </div>
                </div>
            </div>
        {% endfor %}
    </div>
    {% endfor %}
    {% else %}
        <p class="text-muted">Cardápio em breve...</p>
    {% endif %}   
    ```
</details>

<details>
    <summary>Reserva</summary> 

    ### Forms

    ```python
    class ReservationForm(forms.ModelForm):
        class Meta:
            model = Reservation
            fields = ['date', 'time', 'guests', 'notes']
            widgets = {
                'date': forms.DateInput(attrs={'type': 'date'}),
                'time': forms.TimeInput(attrs={'type': 'time'}),
            } 

        def __init__(self, *args, **kwargs):
            super(ReservationForm, self).__init__(*args, **kwargs)

            self.helper = FormHelper()
            self.helper.form_method = 'post'
            self.helper.layout = Layout(
                Row(
                    Column('date', css_class='col-md-6'),
                ),
                Row(
                    Column('time', css_class='col-md-6'),
                    Column('guests', css_class='col-md-6'),
                ), 
                Field('notes', rows=3), 
                Row(
                    Column(
                        HTML('<a href="{% url \'restaurant_detail\' pk=restaurant.pk %}" class="btn btn-secondary"><i class="fas fa-arrow-left"></i> Voltar</a>'),
                        css_class='col-auto'
                    ),
                    Column(
                        Submit('submit', '{% if form.instance.pk %}Salvar Alterações{% else %}Adicionar Reserva{% endif %}', css_class='btn btn-primary'),
                        css_class='col-auto ms-auto'
                    ),
                ),
            )
    ```

    ### Views

    ```python
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
                    reservation.table = available_table
                    reservation.save()
                    messages.success(request, 'Reserva realizada com sucesso!')
                    return redirect('reservation_detail', pk=reservation.pk)
                else:
                    messages.error(request, 'Não há mesas disponíveis para o número de pessoas solicitado.')
        else:
            form = ReservationForm()
        return render(request, 'reservation_form.html', {'form': form, 'restaurant': restaurant})
    
        
    @login_required
    def reservation_detail(request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)
        return render(request, 'reservation_detail.html', {'reservation': reservation})
    
    ```

    ### Template

    templates>reservation_form.html

    ```html
    {% extends 'base.html' %}
    {% block title %}Fazer Reserva{% endblock %} 
    {% load crispy_forms_tags %} 
    {% block content %}  
    <div class="col-md-8 offset-md-2">
        <h2 class="text-center mb-4">Fazer Reserva - {{ restaurant.name }}</h2>
        {% crispy form %}
    </div>
    {% endblock %}
    ```

    templates>reservation_detail.html

    ```html
    {% extends 'base.html' %}
    {% block title %}Detalhes da Reserva{% endblock %}
    {% block content %}

    <div class="row">
        <div class="col-md-8 offset-md-2">
            <h2 class="mb-4">ID: {{ reservation.id }} - Detalhes da Reserva</h2>
            
            <div class="mb-4">
                <h4>{{ reservation.restaurant.name }}</h4>
                <p class="text-muted">
                    <i class="fas fa-map-marker-alt"></i> {{ reservation.restaurant.address }}
                </p>
            </div>

            <div class="row mb-4">
                <div class="col-md-6">
                    <p><i class="fas fa-calendar"></i> {{ reservation.date|date:"d/m/Y" }}</p>
                    <p><i class="fas fa-clock"></i> {{ reservation.time|time:"H:i" }}</p>
                </div>
                <div class="col-md-6">
                    <p><i class="fas fa-users"></i> {{ reservation.guests }} pessoas</p>
                    <p><i class="fas fa-chair"></i> Mesa {{ reservation.table.number }}</p>
                </div>
            </div>

            <div class="mb-4">
                <span class="badge {% if reservation.status == 'confirmada' %}bg-success{% elif reservation.status == 'pendente' %}bg-warning{% else %}bg-danger{% endif %}">
                    {{ reservation.get_status_display }}
                </span>
            </div>

            {% if reservation.notes %}
            <div class="mb-4">
                <strong>Observações:</strong>
                <p>{{ reservation.notes }}</p>
            </div>
            {% endif %}

            <div class="d-flex justify-content-between">
                <a href="javascript:history.back()" class="btn btn-secondary">
                    <i class="fas fa-arrow-left"></i> Voltar
                </a>

                {% if user == reservation.restaurant.owner and reservation.status == 'pendente' %}
                <div>
                    <a href="#" class="btn btn-success">
                        <i class="fas fa-check"></i> Confirmar
                    </a>
                    <a href="#" class="btn btn-danger">
                        <i class="fas fa-times"></i> Cancelar
                    </a>
                </div>
                {% endif %}
            </div>
        </div>
    </div>

    {% endblock %}
    ```

    ### Urls.py

    ```python
    path('restaurant/<int:restaurant_pk>/reserve/', reservation_create, name='reservation_create'), 
    path('reservation/<int:pk>/', reservation_detail, name='reservation_detail'), 
    ```

    templates>restaurant_detail.html

    ```tsx
    <a href="{% url 'reservation_create' restaurant.pk %}" class="btn btn-primary btn-lg w-100 mb-2">
        <i class="fas fa-calendar-plus"></i> Fazer Reserva
    </a>
    ```
    </details>

    <details>
    <summary>Reserva - Gerenciar pelo usuário</summary> 

    Para o usuario que criou uma reserva precisa aparecer para ele as reservas feitas. 

    ### Views

    ```python
    @login_required
    def my_reservations(request):
        reservations = Reservation.objects.filter(user=request.user).order_by('-date', '-time')
        return render(request, 'my_reservations.html', {'reservations': reservations})
    ```

    ### Template

    templates/my_reservations.html

    ```html
    {% extends 'base.html' %}
    {% block title %}Minhas Reservas{% endblock %}
    {% block content %}
    <h2 class="mb-4">Minhas Reservas</h2>
    {% if reservations %}
    <div class="row">
        {% for reservation in reservations %}
        <div class="col-md-6 mb-3">
            <div class="border border-3 rounded p-3 h-100 d-flex flex-column
                {% if reservation.status == 'confirmada' %}border-success
                {% elif reservation.status == 'pendente' %}border-warning
                {% elif reservation.status == 'cancelada' %}border-danger{% endif %}">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h5>{{ reservation.restaurant.name }}</h5>
                    <span class="badge 
                        {% if reservation.status == 'confirmada' %}bg-success
                        {% elif reservation.status == 'pendente' %}bg-warning
                        {% elif reservation.status == 'cancelada' %}bg-danger{% endif %}">
                        {{ reservation.get_status_display }}
                    </span>
                </div>
                
                <p class="mb-1">
                    <i class="fas fa-calendar"></i> 
                    {{ reservation.date|date:"d/m/Y" }} às {{ reservation.time|time:"H:i" }}
                </p>
                
                <p class="mb-1">
                    <i class="fas fa-users"></i> 
                        {{ reservation.guests }} pessoas - Mesa {{ reservation.table.number }}
                    </p>
                
                {% if reservation.notes %}
                <p class="text-muted small mb-2">{{ reservation.notes }}</p>
                {% endif %}
                
                <div class="d-flex justify-content-end gap-2 align-items-center mt-auto">
                    <a href="{% url 'reservation_detail' pk=reservation.pk %}" class="btn btn-sm btn-primary">
                        <i class="fas fa-eye"></i> Ver Detalhes
                    </a>
                    {% if reservation.status == 'confirmada' %}
                    <a href="#create_order" class="btn btn-sm btn-success">
                        <i class="fas fa-utensils"></i> Fazer Pedido
                    </a>
                    {% endif %}
                </div> 
            </div>
        </div>
        {% endfor %}
    </div>
    {% else %}
    <div class="alert alert-info">
        <p class="mb-2">Você ainda não tem reservas.</p>
        <a href="{% url 'home' %}" class="btn btn-primary">Encontrar Restaurantes</a>
    </div>
    {% endif %}
    {% endblock %}
    ```

    ### Urls

    ```python
    path('reservations/', views.my_reservations, name='my_reservations'),
    ```

    base>

    ```tsx
    <a class="dropdown-item" href="{% url 'my_reservations' %}">
        <i class="fas fa-calendar"></i> Minhas Reservas
    </a>
    ```
</details>

<details> 
    <summary>Reserva - Gerenciar</summary>  

    ### Views

    ```python
    @login_required
    def reservation_manage(request, restaurant_pk):
        restaurant = get_object_or_404(Restaurant, pk=restaurant_pk)

        # Verifica se o usuário é o dono do restaurante
        if request.user != restaurant.owner:
            messages.error(request, 'Você não tem permissão para gerenciar as reservas deste restaurante.')
            return redirect('restaurant_detail', pk=restaurant_pk)

        # Filtro por status
        status_filter = request.GET.get('status')
        reservations = Reservation.objects.filter(restaurant=restaurant)

        if status_filter:
            reservations = reservations.filter(status=status_filter)

        # Contadores para o menu
        pending_count = Reservation.objects.filter(restaurant=restaurant, status='pendente').count()
        confirmed_count = Reservation.objects.filter(restaurant=restaurant, status='confirmada').count()
        cancelled_count = Reservation.objects.filter(restaurant=restaurant, status='cancelada').count()

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
            new_status = request.POST.get('status')
            if new_status in ['confirmada', 'cancelada']:
                reservation.status = new_status
                reservation.save()

                # Enviar notificação ao cliente
                status_display = 'confirmada' if new_status == 'confirmada' else 'rejeitada'
                messages.success(request, f'Reserva {status_display} com sucesso!')
            else:
                messages.error(request, 'Status inválido.')

        return redirect('reservation_detail', pk=pk)
    ```

    ### Template

    É meio longo por que precisamos ter controle com base no status do pedido, **pendente, confirmado, cancelado, preparando e entrega**. então acabo fazendo esse tratamento no template mesmo. O proprio bootstrap tem umas classes de manage de abas que ajuda muito.

    templates/reservation_manage.html

    ```html
    {% extends 'base.html' %}
    {% block title %}Gerenciar Reservas{% endblock %}
    {% block content %}

    <h2 class="mb-4">Reservas - {{ restaurant.name }}</h2>

    <!-- Abas de filtro -->
    <ul class="nav nav-tabs mb-4">
        <li class="nav-item">
            <a class="nav-link {% if not status_filter %}active{% endif %}" href="?">
                Todas
            </a>
        </li>
        <li class="nav-item">
            <a class="nav-link {% if status_filter == 'pendente' %}active{% endif %}" href="?status=pendente">
                Pendentes <span class="badge bg-warning">{{ pending_count }}</span>
            </a>
        </li>
        <li class="nav-item">
            <a class="nav-link {% if status_filter == 'confirmada' %}active{% endif %}" href="?status=confirmada">
                Confirmadas <span class="badge bg-success">{{ confirmed_count }}</span>
            </a>
        </li>
        <li class="nav-item">
            <a class="nav-link {% if status_filter == 'cancelada' %}active{% endif %}" href="?status=cancelada">
                Canceladas <span class="badge bg-danger">{{ cancelled_count }}</span>
            </a>
        </li>
    </ul>

    <!-- Tabela de reservas -->
    <table class="table">
        <thead>
            <tr>
                <th>Cliente</th>
                <th>Data</th>
                <th>Hora</th>
                <th>Mesa</th>
                <th>Pessoas</th>
                <th>Status</th>
                <th>Ações</th>
            </tr>
        </thead>
        <tbody>
            {% for reservation in reservations %}
            <tr>
                <td>{{ reservation.user.get_full_name }}</td>
                <td>{{ reservation.date|date:"d/m/Y" }}</td>
                <td>{{ reservation.time|time:"H:i" }}</td>
                <td>Mesa {{ reservation.table.number }}</td>
                <td>{{ reservation.guests }}</td>
                <td>
                    <span class="badge {% if reservation.status == 'confirmada' %}bg-success{% elif reservation.status == 'pendente' %}bg-warning{% else %}bg-danger{% endif %}">
                        {{ reservation.get_status_display }}
                    </span>
                </td>
                <td>
                        <div class="d-flex gap-1">
                        <a href="{% url 'reservation_detail' pk=reservation.pk %}" class="btn btn-sm btn-primary">
                            <i class="fas fa-eye"></i> Ver
                        </a>
                        {% if reservation.status == 'pendente' %}
                        <form method="post" action="{% url 'reservation_update_status' pk=reservation.pk %}" class="d-inline">
                            {% csrf_token %}
                            <input type="hidden" name="status" value="confirmada">
                            <button type="submit" class="btn btn-sm btn-success">
                                <i class="fas fa-check"></i>
                            </button>
                        </form>
                        <form method="post" action="{% url 'reservation_update_status' pk=reservation.pk %}" class="d-inline">
                            {% csrf_token %}
                            <input type="hidden" name="status" value="cancelada">
                            <button type="submit" class="btn btn-sm btn-danger">
                                <i class="fas fa-times"></i>
                            </button>
                        </form>
                        {% endif %}
                    </div>
                </td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="7" class="text-center text-muted">Nenhuma reserva encontrada.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    {% endblock %}
    ```

    ### Urls.py

    ```python
    path('reservation/<int:pk>/update-status/', reservation_update_status, name='reservation_update_status'),
    path('restaurant/<int:restaurant_pk>/reservations/', reservation_manage, name='reservation_manage'), 
    ```

    templates>reservation_detail.html

    ```tsx
    {% if user == reservation.restaurant.owner and reservation.status == 'pendente' %}
    <div>
        <form method="post" action="{% url 'reservation_update_status' pk=reservation.pk %}" class="d-inline">
            {% csrf_token %}
            <input type="hidden" name="status" value="confirmada">
            <button type="submit" class="btn btn-success">
                <i class="fas fa-check"></i> Confirmar Reserva
            </button>
        </form>
        <form method="post" action="{% url 'reservation_update_status' pk=reservation.pk %}" class="d-inline ms-2">
            {% csrf_token %}
            <input type="hidden" name="status" value="cancelada">
            <button type="submit" class="btn btn-danger">
                <i class="fas fa-times"></i> Rejeitar Reserva
            </button>
        </form>
    </div>
    {% endif %}
    ```

    templates/my_restaurants.html

    ```tsx
    {% url 'reservation_manage' restaurant_pk=restaurant.pk %}
    ```
</details>

<details>
    <summary>Ordem</summary> 

    E onde o usuario ou cliente mesmo do restaurante consegue adicionar pedido referente a mesa. Esse pedido é a lista de Items que restaurante tem. Então essa parte é um pouco trabalho de fazer mas não é dificil. Vamos ver por partes como vai ficar ok.

    ### Views

    ```python
    def add_items_in_order(order, menu_items, quantities):
        """Adiciona itens ao pedido e retorna o total"""
        total = 0
        for item_id, quantity in zip(menu_items, quantities):
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
            menu_items = request.POST.getlist('menu_items')
            quantities = request.POST.getlist('quantities')

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
                messages.error(request, 'Selecione pelo menos um item para fazer o pedido.')

        menu_items = MenuItem.objects.filter(restaurant=reservation.restaurant, available=True)
        return render(request, 'order_create.html', {
            'reservation': reservation,
            'menu_items': menu_items
        })

    @login_required
    def order_detail(request, pk):
        order = get_object_or_404(Order, pk=pk)
        return render(request, 'order_detail.html', {'order': order})
    ```

    ### Templates

    templates/order_create.html

    ```html
    {% extends 'base.html' %}
    {% block title %}Fazer Pedido{% endblock %}
    {% block content %}
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <h2 class="mb-3">Fazer Pedido - {{ reservation.restaurant.name }}</h2>
            
            <p class="text-muted mb-4">
                <i class="fas fa-calendar"></i> {{ reservation.date|date:"d/m/Y" }} às {{ reservation.time|time:"H:i" }} - 
                Mesa {{ reservation.table.number }}
            </p>

            <form method="post">
                {% csrf_token %}
                
                {% regroup menu_items by category as category_list %}
                
                {% for category in category_list %}
                <h4 class="mt-4 mb-3">{{ category.grouper|title }}</h4>
                
                {% for item in category.list %}
                <div class="border rounded p-3 mb-2">
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="d-flex align-items-center">
                            <img src="{% if item.image %}{{ item.image.url }}{% else %}https://via.placeholder.com/80{% endif %}" 
                                alt="{{ item.name }}" 
                                class="rounded me-3" 
                                style="width: 80px; height: 80px; object-fit: cover;">
                            <div>
                                <h6 class="mb-1">{{ item.name }}</h6>
                                <p class="text-muted small mb-1">{{ item.description|truncatewords:15 }}</p>
                                <strong class="text-success">R$ {{ item.price }}</strong>
                            </div>
                        </div>
                        <div style="text-align: center; width: 100px;">
                            <label class="small">Quantidade</label>
                            <input type="number" 
                                name="quantities" 
                                class="form-control form-control-sm" 
                                value="0" 
                                min="0" 
                                max="20">
                            <input type="hidden" name="menu_items" value="{{ item.id }}">
                        </div>
                    </div>
                </div>
                {% endfor %}
                {% endfor %}

                <div class="mt-4 mb-4">
                    <label>Observações:</label>
                    <textarea name="notes" class="form-control" rows="2" placeholder="Alguma observação?"></textarea>
                </div>

                <div class="d-flex justify-content-between">
                    <a href="{% url 'reservation_detail' pk=reservation.pk %}" class="btn btn-secondary">
                        <i class="fas fa-arrow-left"></i> Voltar
                    </a>
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-check"></i> Confirmar Pedido
                    </button>
                </div>
            </form>
        </div>
    </div>

    {% endblock %}
    ```

    templates/order_detail.html

    ```html
    {% extends 'base.html' %}
    {% block title %}Pedido #{{ order.id }}{% endblock %}
    {% block content %}
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <h2 class="mb-3">Pedido #{{ order.id }}</h2>
            
            <div class="mb-4">
                <h4>{{ order.restaurant.name }}</h4>
                <span class="badge 
                    {% if order.status == 'pronto' %}bg-success
                    {% elif order.status == 'preparando' %}bg-info
                    {% elif order.status == 'cancelado' %}bg-danger
                    {% elif order.status == 'pendente' %}bg-warning
                    {% elif order.status == 'entregue' %}bg-secondary{% endif %}">
                    {{ order.get_status_display }}
                </span>
            </div>

            <h5 class="mb-3">Itens do pedido</h5>
            {% for order_item in order.orderitem_set.all %}
            <div class="border rounded p-2 mb-2">
                <div class="d-flex justify-content-between">
                    <span>{{ order_item.quantity }}x {{ order_item.item.name }}</span>
                    <strong>R$ {{ order_item.price }}</strong>
                </div>
            </div>
            {% endfor %}
            
            <div class="border-top pt-3 mt-3">
                <div class="d-flex justify-content-between">
                    <h5>Total:</h5>
                    <h5>R$ {{ order.total }}</h5>
                </div>
            </div>

            {% if order.reservation %}
            <div class="mt-4">
                <p class="mb-1"><i class="fas fa-calendar"></i> {{ order.reservation.date|date:"d/m/Y" }} às {{ order.reservation.time|time:"H:i" }}</p>
                <p class="mb-1"><i class="fas fa-chair"></i> Mesa {{ order.reservation.table.number }}</p>
            </div>
            {% endif %}

            {% if order.notes %}
            <div class="mt-3">
                <strong>Observações:</strong>
                <p>{{ order.notes }}</p>
            </div>
            {% endif %}

            <p class="text-muted small mt-3">Pedido realizado em {{ order.created_at|date:"d/m/Y H:i" }}</p>

            <div class="d-flex justify-content-between">
                <a href="#" class="btn btn-secondary">
                    <i class="fas fa-arrow-left"></i> Voltar para Meus Pedidos
                </a>

                {% if order.status == 'pendente' %}
                <form method="post" action="#update_order_status" class="d-inline">
                    {% csrf_token %}
                    <input type="hidden" name="status" value="cancelado">
                    <button type="submit" class="btn btn-danger" onclick="return confirm('Tem certeza que deseja cancelar este pedido?')">
                        <i class="fas fa-times"></i> Cancelar Pedido
                    </button>
                </form>
                {% endif %}
                
            </div>
        </div>
    </div>

    {% endblock %}
    ```

    ### Urls

    ```python
    path('reservation/<int:reservation_pk>/order/', create_order, name='create_order'),
    path('order/<int:pk>/', order_deail, name='order_detail'),  
    ```

    templates>my_reservation.html

    ```tsx
    {% if reservation.status == 'confirmada' %}
    <a href="{% url 'create_order' reservation_pk=reservation.pk %}" class="btn btn-success">
        <i class="fas fa-utensils"></i> Fazer Pedido
    </a>
    {% endif %}
    ```

    templates>reservation_detail.html

    ```tsx
    {% if reservation.status == 'confirmada' %}
    <a href="{% url 'create_order' reservation_pk=reservation.pk %}" class="btn btn-primary">
        <i class="fas fa-utensils"></i> Fazer Pedido
    </a>
    {% endif %}
    ```

    **Melhorar o create_order**

    ```tsx
    # Subistitui escolha
    <div style="text-align: center; width: 150px;"> 
    <div class="d-flex">
        <button type="button" class="btn btn-outline-secondary" onclick="diminuir({{ item.id }})">−</button>
        <input type="tex" 
                id="qtd_{{ item.id }}"
                name="quantities" 
                class="form-control text-center" 
                value="0" 
                min="0" 
                max="20"
                onchange="calcularTotal()">
        <button type="button" class="btn btn-outline-secondary" onclick="aumentar({{ item.id }})">+</button>
    </div>
    <input type="hidden" name="menu_items" value="{{ item.id }}">
    <input type="hidden" id="preco_{{ item.id }}" value="{{ item.price }}">
    <input type="hidden" id="nome_{{ item.id }}" value="{{ item.name }}">
    </div>

    # Colocor depois do col-md-8
    <!-- Resumo do Pedido -->
    <div class="col-md-4">
        <div class="border rounded p-3 mb-4 bg-light">
            <h4>Resumo do Pedido</h5>
            <div id="resumo">
                <p class="text-muted">Nenhum item selecionado</p>
            </div>
            <hr>
            <div class="d-flex justify-content-between">
                <h5>Total:</h5>
                <h5 class="text-success">R$ <span id="total">0,00</span></h5>
            </div>
        </div>
    </div>

    scripts

    {% block extra_js %}
    <script>
    // Função 1: Aumentar quantidade
    function aumentar(itemId) {
        var input = document.getElementById('qtd_' + itemId);
        input.value = parseInt(input.value) + 1;
        calcularTotal();
    }

    // Função 2: Diminuir quantidade
    function diminuir(itemId) {
        var input = document.getElementById('qtd_' + itemId);
        if (parseInt(input.value) > 0) {
            input.value = parseInt(input.value) - 1;
            calcularTotal();
        }
    }

    // Função 3: Calcular total e mostrar resumo
    function calcularTotal() {
        var total = 0;
        var resumoHTML = '';
        
        // Pega todos os inputs de quantidade
        var inputs = document.querySelectorAll('input[name="quantities"]');
        
        inputs.forEach(function(input) {
            var itemId = input.id.replace('qtd_', '');
            var quantidade = parseInt(input.value);
            
            if (quantidade > 0) {
                var preco = parseFloat(document.getElementById('preco_' + itemId).value);
                var nome = document.getElementById('nome_' + itemId).value;
                var subtotal = quantidade * preco;
                
                total += subtotal;
                
                // Adiciona linha no resumo
                resumoHTML += '<div class="d-flex justify-content-between mb-1">';
                resumoHTML += '<span>' + quantidade + 'x ' + nome + '</span>';
                resumoHTML += '<span>R$ ' + subtotal.toFixed(2) + '</span>';
                resumoHTML += '</div>';
            }
        });
        
        // Atualiza o resumo
        if (resumoHTML === '') {
            document.getElementById('resumo').innerHTML = '<p class="text-muted">Nenhum item selecionado</p>';
        } else {
            document.getElementById('resumo').innerHTML = resumoHTML;
        }
        
        // Atualiza o total
        document.getElementById('total').textContent = total.toFixed(2).replace('.', ',');
    }
    </script>
    {% endblock %}

    ```
</details> 

<details>
    <summary>Ordem - Gerenciar</summary> 

    ### Order Manage Views

    ```python
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
            new_status = request.POST.get('status')
            
            # Lista de status válidos
            valid_statuses = ['pendente', 'preparando', 'pronto', 'entregue', 'cancelado']
            
            if new_status in valid_statuses:
                order.status = new_status
                order.save()
                messages.success(request, f'Pedido atualizado para: {order.get_status_display()}')
            else:
                messages.error(request, 'Status inválido.')

        return redirect('order_manage', restaurant_pk=order.restaurant.pk)
    ```

    ### Templates

    templates/order_manage.html

    ```html
    {% extends 'base.html' %}
    {% block title %}Gerenciar Pedidos{% endblock %}
    {% block content %}

    <h2 class="mb-4">Pedidos - {{ restaurant.name }}</h2>

    <!-- Abas de filtro -->
    <ul class="nav nav-tabs mb-4">
        <li class="nav-item">
            <a class="nav-link {% if not status_filter %}active{% endif %}" href="?">Todos</a>
        </li>
        <li class="nav-item">
            <a class="nav-link {% if status_filter == 'pendente' %}active{% endif %}" href="?status=pendente">
                Pendentes <span class="badge bg-warning">{{ pending_count }}</span>
            </a>
        </li>
        <li class="nav-item">
            <a class="nav-link {% if status_filter == 'preparando' %}active{% endif %}" href="?status=preparando">
                Preparando <span class="badge bg-info">{{ preparing_count }}</span>
            </a>
        </li>
        <li class="nav-item">
            <a class="nav-link {% if status_filter == 'pronto' %}active{% endif %}" href="?status=pronto">
                Prontos <span class="badge bg-success">{{ ready_count }}</span>
            </a>
        </li>
        <li class="nav-item">
            <a class="nav-link {% if status_filter == 'entregue' %}active{% endif %}" href="?status=entregue">
                Entregues <span class="badge bg-secondary">{{ delivered_count }}</span>
            </a>
        </li>
        <li class="nav-item">
            <a class="nav-link {% if status_filter == 'cancelado' %}active{% endif %}" href="?status=cancelado">
                Cancelados <span class="badge bg-danger">{{ cancelled_count }}</span>
            </a>
        </li>
    </ul>

    <!-- Tabela de pedidos -->
    <table class="table">
        <thead>
            <tr>
                <th>#</th>
                <th>Cliente</th>
                <th>Mesa</th>
                <th>Total</th>
                <th>Status</th>
                <th>Data/Hora</th>
                <th>Ações</th>
            </tr>
        </thead>
        <tbody>
            {% for order in orders %}
            <tr>
                <td>{{ order.id }}</td>
                <td>{{ order.user.get_full_name }}</td>
                <td>{% if order.reservation %}Mesa {{ order.reservation.table.number }}{% else %}-{% endif %}</td>
                <td>R$ {{ order.total }}</td>
                <td>
                    <span class="badge {% if order.status == 'pendente' %}bg-warning{% elif order.status == 'preparando' %}bg-info{% elif order.status == 'pronto' %}bg-success{% elif order.status == 'entregue' %}bg-secondary{% else %}bg-danger{% endif %}">
                        {{ order.get_status_display }}
                    </span>
                </td>
                <td>{{ order.created_at|date:'d/m/Y H:i' }}</td>
                <td>
                    <div class="d-flex gap-1">
                        <a href="{% url 'order_detail' pk=order.pk %}" class="btn btn-circle btn-primary">
                            <i class="fas fa-eye"></i>
                        </a>
                        
                        {% if order.status == 'pendente' %}
                        <form method="post" action="{% url 'order_update_status' pk=order.pk %}" class="d-inline">
                            {% csrf_token %}
                            <input type="hidden" name="status" value="preparando">
                            <button type="submit" class="btn btn-circle btn-info" title="Iniciar preparo">
                                <i class="fas fa-utensils"></i>
                            </button>
                        </form>
                        <form method="post" action="{% url 'order_update_status' pk=order.pk %}" class="d-inline">
                            {% csrf_token %}
                            <input type="hidden" name="status" value="cancelado">
                            <button type="submit" class="btn btn-circle btn-danger" title="Cancelar">
                                <i class="fas fa-times"></i>
                            </button>
                        </form>
                        
                        {% elif order.status == 'preparando' %}
                        <form method="post" action="{% url 'order_update_status' pk=order.pk %}" class="d-inline">
                            {% csrf_token %}
                            <input type="hidden" name="status" value="pronto">
                            <button type="submit" class="btn btn-circle btn-success" title="Marcar como pronto">
                                <i class="fas fa-check"></i>
                            </button>
                        </form>
                        
                        {% elif order.status == 'pronto' %}
                        <form method="post" action="{% url 'order_update_status' pk=order.pk %}" class="d-inline">
                            {% csrf_token %}
                            <input type="hidden" name="status" value="entregue">
                            <button type="submit" class="btn btn-circle btn-secondary" title="Marcar como entregue">
                                <i class="fas fa-check-double"></i>
                            </button>
                        </form>
                        {% endif %}
                    </div>
                </td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="7" class="text-center text-muted">Nenhum pedido encontrado.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    {% endblock %}
    ```

    ```tsx
    .btn-circle {
        width: 40px!important;
        height: 40px!important; 
        padding: 0!important;
        border-radius: 50%; 
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 5px;
    }

    ```

    ### Urls.py

    ```python
        path('restaurant/<int:restaurant_pk>/orders/', order_manage, name='order_manage'),
        path('order/<int:pk>/update-status/', order_update_status, name='order_update_status'),
    ```

    templates>my_restaurants.html

    ```tsx
    <a href="{% url 'order_manage' restaurant.pk %}" class="btn btn-sm btn-outline-success">
        <i class="fas fa-shopping-cart"></i> Pedidos
    </a>
    ```

    templates>order_detail.html

    ```tsx
    {% if order.status == 'pendente' %}
    <form method="post" action="{% url 'order_update_status' order.pk %}" class="d-inline">
        {% csrf_token %}
        <input type="hidden" name="status" value="cancelado">
        <button type="submit" class="btn btn-danger" onclick="return confirm('Tem certeza que deseja cancelar este pedido?')">
            <i class="fas fa-times"></i> Cancelar Pedido
        </button>
    </form>
    {% endif %}
    ```
</details>

<details>
    <summary>Ordem - Gerenciar pelo usuáro</summary>

    ### Order User Views

    ```python
    @login_required
    def my_orders(request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'my_orders.html', {'orders': orders})
    ```

    ### Template

    templates/my_orders.html

    ```html
    {% extends 'base.html' %}
    {% block title %}Meus Pedidos{% endblock %}
    {% block content %}
    <h2 class="mb-4">Meus Pedidos</h2>

    {% if orders %}
    <div class="row">
        {% for order in orders %}
        <div class="col-md-6 mb-3">
            <div class="border 
                    {% if order.status == 'pronto' %}border-success
                    {% elif order.status == 'preparando' %}border-info
                    {% elif order.status == 'cancelado' %}border-danger
                    {% elif order.status == 'pendente' %}border-warning
                    {% elif order.status == 'entregue' %}border-secondary{% endif %} 
                border-3 rounded p-3 h-100 d-flex flex-column">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <div>
                        <h5>Pedido #{{ order.id }}</h5>
                        <p class="mb-1">{{ order.restaurant.name }}</p>
                    </div>
                    <span class="badge  
                        {% if order.status == 'pronto' %}bg-success
                        {% elif order.status == 'preparando' %}bg-info
                        {% elif order.status == 'cancelado' %}bg-danger
                        {% elif order.status == 'pendente' %}bg-warning
                        {% elif order.status == 'entregue' %}bg-secondary{% endif %}">
                        {{ order.get_status_display }}
                    </span>
                </div>
                
                <div class="mb-2">
                    {% for order_item in order.orderitem_set.all %}
                    <div class="d-flex justify-content-between small">
                        <span>{{ order_item.quantity }}x {{ order_item.item.name }}</span>
                        <span>R$ {{ order_item.price }}</span>
                    </div>
                    {% endfor %}
                </div>
                
                <div class="border-top pt-2 mb-2">
                    <div class="d-flex justify-content-between">
                        <strong>Total:</strong>
                        <strong class="text-success">R$ {{ order.total }}</strong>
                    </div>
                </div>
                
                <div class="d-flex justify-content-between align-items-center mt-auto">
                    <small class="text-muted">{{ order.created_at|date:"d/m/Y H:i" }}</small>
                    <a href="{% url 'order_detail' pk=order.pk %}" class="btn btn-sm btn-primary">
                        <i class="fas fa-eye"></i> Ver Detalhes
                    </a>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
    {% else %}
    <div class="alert alert-info">
        <p class="mb-2">Você ainda não fez nenhum pedido.</p>
        <a href="{% url 'home' %}" class="btn btn-primary">
            <i class="fas fa-utensils"></i> Explorar Restaurantes
        </a>
    </div>
    {% endif %}

    {% endblock %}
    ```

    ### Urls.py

    ```python
    path('orders/', my_orders, name='my_orders'), 
    ```

    base>

    ```tsx
    <li>
    <a class="dropdown-item" href="{% url 'my_orders' %}">
        <i class="fas fa-shopping-bag"></i> Meus Pedidos
    </a>
    </li>
    ```

    ### **Usuário Empresa X Usuário Padrão**

    ### Models

    ```tsx
    from django.db.models.signals import post_save
    from django.dispatch import receiver

    # Perfil do Usuário (Empresa ou Cliente)
    class UserProfile(models.Model):
        user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
        is_business = models.BooleanField('É Empresa?', default=False)
        
        def __str__(self):
            return f'{self.user.username} - {"Empresa" if self.is_business else "Cliente"}'
        
        class Meta:
            verbose_name = 'Perfil de Usuário'
            verbose_name_plural = 'Perfis de Usuários'

    # Cria perfil automaticamente quando um usuário é criado
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        """
        Signal que cria um perfil automaticamente quando:
        1. Um novo usuário é criado (created=True)
        2. Um usuário antigo faz login e não tem perfil
        """
        if created:
            # Novo usuário → cria perfil
            UserProfile.objects.create(user=instance)
        else:
            # Usuário existente → verifica se tem perfil
            try:
                instance.profile
            except UserProfile.DoesNotExist:
                # Não tem perfil → cria (para usuários antigos)
                UserProfile.objects.create(user=instance)
    ```

    ```tsx
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver
    ```

    ### Admin

    ```tsx
    @admin.register(UserProfile)
    class UserProfileAdmin(admin.ModelAdmin):
        list_display = ['user', 'is_business']
        list_filter = ['is_business']
        search_fields = ['user__username']
    ```

    ### Forms

    ```tsx
    class UserRegistrationForm(UserCreationForm):   
        ...
        is_business = forms.BooleanField(
            required=False,
            label="Sou uma empresa",
            help_text="Marque esta opção se você deseja cadastrar um restaurante"
        )
        ...

    Layout    
    Row(
            Column('is_business', css_class='col-md-6'),
        ),
    ```

    ### Views

    ```tsx
    def register(request):
        if request.method == 'POST':
            form = UserRegistrationForm(request.POST)
            if form.is_valid():
                user = form.save()
                
                # Atualiza o perfil com is_business
                user.profile.is_business = form.cleaned_data.get('is_business', False)
                user.profile.save()
                
                ...
    ```

    Templates

    base>

    ```tsx
    <ul class="dropdown-menu dropdown-menu-end">
    {% if user.profile.is_business %}
    <li>
        <a class="dropdown-item" href="{% url 'my_restaurants' %}">
            <i class="fas fa-store"></i> Meus Restaurantes
        </a>
    </li>
    {% endif %}
    ...
    ```

    home

    ```tsx
    <div class="bg-light rounded-3 p-5 mb-5 text-center">
        <h1 class="display-5 fw-bold">Bem-vindo(a) 
            {% if user.is_authenticated %}
                {{ user.get_full_name|default:user.username }}
            {% else %}
                ao OrderUP
            {% endif %}
        </h1> 
        
        <p class="lead text-muted">Sistema de reservas para restaurantes</p>
        
        {% if user.is_authenticated %}
            {% if user.profile.is_business %}
            <a href="{% url 'restaurant_create' %}" class="btn btn-primary btn-lg mt-3">
                <i class="fas fa-plus-circle"></i> Cadastrar Restaurante
            </a>
            {% else %}
            <p class="lead bg-success text-white rounded-3 p-2" style="display: inline-block;">
                Selecione um restaurante para fazer uma reserva
                <i class="fas fa-arrow-down"></i>
            </p>
            {% endif %}
        {% else %}
            <a href="{% url 'register' %}" class="btn btn-primary btn-lg mt-3">
                <i class="fas fa-rocket"></i> Começar Agora
            </a>
        {% endif %}
    </div> 
    ```

    **A gente pode referenciar por data de criação e agendamento OU por codigo aleatorio acho que ficaria legal.**

    templates/my_reservations.html

    ```tsx
    # Total de Pedidos solicitados
    <p class="mb-1"><i class="fas fa-utensils"></i> Pedidos solicitados: {{ reservation.order_set.count }}</p>

    # Informação importante quando pedido foi criado
    <p class="text-muted small mt-3">Reserva realizada em {{ reservation.created_at|date:"d/m/Y H:i" }}</p>
    ```

    templates/reservation_detail.html

    ```tsx
    
    <div class="col-md-6">
        Pedidos agendados: {{ reservation.order_set.count }}
    </div>

    <p class="text-muted small mt-3">Reserva realizada em {{ reservation.created_at|date:"d/m/Y H:i" }}</p>
    ```

    templates/my_order.html

    ```tsx
    <h4><i class="fas fa-circle"></i> Pedido #{{ order.id }}</h4> 

    <div class="mb-2">
        <p class="mb-1"><i class="fas fa-chair"></i> Mesa {{ order.reservation.table.number }}</p>
        <p class="mb-1 small text-muted"><i class="fas fa-calendar"></i> Referência da reserva: {{ order.reservation.date|date:"d/m/Y" }} às {{ order.reservation.time|time:"H:i" }}</p>
    </div>

    <small class="text-muted">Pedido realizado em: {{ order.created_at|date:"d/m/Y H:i" }}</small>
    ```

    templates/order_detail.html

    ```tsx
    <p class="mb-1"><i class="fas fa-calendar"></i> Reserva: {{ order.reservation.date|date:"d/m/Y" }} às {{ order.reservation.time|time:"H:i" }}</p>

    ```
</details>
</details>

<details> 
    <summary>🔧 Comandos Úteis</summary> 

    ### Migração do Banco de Dados

    ```bash
    python manage.py makemigrations
    python manage.py migrate

    ```

    ### Criar Superusuário

    ```bash
    python manage.py createsuperuser

    ```

    ### Carregar Dados Iniciais

    ```bash
    python manage.py loaddata fixtures/fixture.data.json

    ```

    ### Coletar Arquivos Estáticos

    ```bash
    python manage.py collectstatic

    ```

    ### Rodar o Servidor

    ```bash
    python manage.py runserver
    ```
</details>

<details> 
    <summary>📱 Próximos Passos - Sugestão de Melhoria (Estudo)</summary> 

    **Melhorias Sugeridas para Comercialização** :

    - Fazer parte do Garçom
    - Sistema de pagamentos online
    - API REST para integração com outros sistemas
    - Painel de análise de dados
    - Sistema de avaliações
    - Gestão de estoque
    - Sistema de delivery
    - Aplicativo mobile

    **Aspectos Legais** :

    - Registre sua propriedade intelectual
    - Crie termos de serviço e política de privacidade
    - Considere aspectos de LGPD para dados pessoais
    - Prepare contratos de licenciamento/uso 
</details>