"""
urls.py — Rutas de la API de Gift Cards.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/stats/', views.DashboardStatsView.as_view(), name='dashboard-stats'),
    
    # Clientes
    path('clients/', views.ClientListView.as_view(), name='client-list'),
    path('clients/<int:client_id>/', views.ClientDetailView.as_view(), name='client-detail'),
    
    # Gift Cards
    path('giftcards/', views.GiftCardListView.as_view(), name='giftcard-list'),
    path('giftcards/lookup/', views.GiftCardLookupView.as_view(), name='giftcard-lookup'),
    path('giftcards/activate/', views.ActivateGiftCardView.as_view(), name='giftcard-activate'),
    path('giftcards/movimientos/', views.ClientMovimientosView.as_view(), name='giftcard-movimientos'),
    path('giftcards/<int:giftcard_id>/', views.GiftCardDetailView.as_view(), name='giftcard-detail'),
    path('giftcards/<int:giftcard_id>/transactions/', views.GiftCardTransactionsView.as_view(), name='giftcard-transactions'),
    
    # Auth (clientes)
    path('auth/login/', views.AuthLoginView.as_view(), name='auth-login'),
    path('auth/logout/', views.AuthLogoutView.as_view(), name='auth-logout'),
    path('auth/check/', views.AuthCheckView.as_view(), name='auth-check'),

    # Caja (PIN de cajeras)
    path('caja/login/', views.CajaLoginView.as_view(), name='caja-login'),

    # Vendedores
    path('vendedor/login/', views.VendedorLoginView.as_view(), name='vendedor-login'),
    path('vendedor/giftcards/', views.VendedorGiftCardListView.as_view(), name='vendedor-giftcards'),
    path('vendedor/lotes/', views.VendedorLoteListView.as_view(), name='vendedor-lotes'),

    # Card Templates (público)
    path('card-templates/active/', views.ActiveCardTemplateView.as_view(), name='card-template-active'),

    # Admin
    path('admin/login/', views.AdminLoginView.as_view(), name='admin-login'),
    path('admin/templates/', views.CardTemplateListView.as_view(), name='admin-templates'),
    path('admin/templates/<int:template_id>/activate/', views.CardTemplateActivateView.as_view(), name='admin-template-activate'),
    path('admin/templates/<int:template_id>/', views.CardTemplateDeleteView.as_view(), name='admin-template-delete'),

    # Diseñador IA
    path('admin/designs/', views.SaveDesignView.as_view(), name='admin-save-design'),

    # Logos de empresas compradoras
    path('admin/companies/', views.CompanyLogoListView.as_view(), name='admin-companies'),
    path('admin/companies/<int:company_id>/', views.CompanyLogoDetailView.as_view(), name='admin-company-detail'),
    path('admin/lotes/', views.LoteListView.as_view(), name='admin-lotes'),

    # Vendedores (gestión desde el panel admin)
    path('admin/vendedores/', views.VendedorAdminListView.as_view(), name='admin-vendedores'),
    path('admin/vendedores/<int:user_id>/', views.VendedorAdminDetailView.as_view(), name='admin-vendedor-detail'),
]
