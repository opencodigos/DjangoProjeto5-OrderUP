from django.contrib import admin 
from django.utils.html import format_html
from .models import (
    UserProfile,
	Restaurant, 
    Table, 
    MenuItem, 
    Reservation, 
    Order, 
    OrderItem)

# admin.site.register(Restaurant)
# admin.site.register(Table)
# admin.site.register(MenuItem)
# admin.site.register(Reservation)
# admin.site.register(Order)
# admin.site.register(OrderItem) 

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_business']
    list_filter = ['is_business']
    search_fields = ['user__username']


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