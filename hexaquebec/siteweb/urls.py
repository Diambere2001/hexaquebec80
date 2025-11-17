from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('contact/', views.contact_view, name='contact'),
    path('produit/<int:pk>/', views.product_detail, name='product_detail'),
    
    path('portfolio/', views.portfolio_list, name='portfolio'),

    # Page courte (aperçu des services)
    path('services/', views.services, name='services'),
    path('annonce/<int:annonce_id>/', views.annonce_detail, name='annonce_detail'),

    # Page détaillée (celle que tu as montrée)
    path('services/detail/', views.services_view, name='services_detail'),
    path('developpement/', views.developp_detail, name='developp_detail'),
    path("produits/", views.produits_list, name="produits_list"),
    path("paiement/<int:produit_id>/", views.paiement_stripe, name="paiement_stripe"),
    path("paiement/success/", views.paiement_success, name="paiement_success"),
    path("paiement/cancel/", views.paiement_cancel, name="paiement_cancel"),
   
    path("produit/<int:id>/", views.produit_detail, name="produit_detail"),
    path("commande/<int:id>/", views.passer_commande, name="passer_commande"),
    path('urgence/', views.urgence_view, name='urgence'),


    
    

    path("chatbot_ai/", views.chatbot_ai, name="chatbot_ai"),
]
