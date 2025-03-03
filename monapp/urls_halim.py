from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('index/', views.index, name='index'),
    path('api/search/', views.search_products, name='search_products'),
    path('recherche/', views.recherche, name='recherche'),
    path('equipe/', views.equipe, name='equipe'),
    path('filter/', views.recommend_products, name='recommend_products'),
    path('chat/', views.chat_response, name='chat_response'),
    path('product/<uuid:product_id>/', views.product_detail, name='product_detail'),
]
