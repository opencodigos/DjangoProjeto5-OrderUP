from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout, Row, Column, Field, Submit, Button, HTML
)
from .models import Restaurant, MenuItem, Reservation

class UserRegistrationForm(UserCreationForm):   
    email = forms.EmailField(required=True, label="Endereço de Email")
    first_name = forms.CharField(required=True, label="Primeiro Nome")
    last_name = forms.CharField(required=True, label="Sobrenome")
    
    is_business = forms.BooleanField(
        required=False,
        label="Sou uma empresa",
        help_text="Marque esta opção se você deseja cadastrar um restaurante"
    )

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
        self.helper.enctype = 'multipart/form-data'
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
                Column('is_business', css_class='col-md-6'),
            ),
            Row(
                Column('password1', css_class='col-md-6'),
                Column('password2', css_class='col-md-6'),
            ),
            Submit('submit', 'Registrar', css_class='btn btn-primary w-100'),
        )


class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'description', 'address', 
                  'phone', 'opening_time', 'closing_time', 'image']
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
                    'available', # Ativo ou Inativo
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