from django.shortcuts import render
from django.db.models import Q, F, Value, IntegerField
from django.db.models.functions import Length
from .models import Product
from .forms import ProductRecommendationForm
from fuzzywuzzy import process, fuzz
from django.http import JsonResponse
import requests


# Définitions de vos vues existantes
def accueil(request):
    return render(request, 'monapp/accueil.html')


def index(request):
    return render(request, 'monapp/index.html')


def recherche(request):
    return render(request, 'monapp/recherche.html')


def equipe(request):
    return render(request, 'monapp/equipe.html')


# Déplacez la classe ProductService au niveau principal
class ProductService:
    """Service class for handling product-related operations"""

# monapp/chatbot
from django.http import JsonResponse
from .chatbot import NutritionChatbot

chatbot = NutritionChatbot()




def chat_response(request):
    if request.method == 'POST':
        message = request.POST.get('message', '')
        if message:
            response = chatbot.get_response(message)
            return JsonResponse({'response': response})
    return JsonResponse({'error': 'Invalid request'}, status=400)


from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.db.models import Q
from django.db.models.functions import Length
from .models import Product
from .forms import ProductSearchForm, ProductRecommendationForm
from sklearn.feature_extraction.text import TfidfVectorizer
import uuid
import numpy as np
import pickle
import matplotlib

matplotlib.use('Agg')  # Utiliser le backend non interactif
import matplotlib.pyplot as plt
import os
from sklearn.metrics.pairwise import cosine_similarity
import scipy.sparse as sparse


class ProductService:

    # 2- le formulaire de "/filter" envoie ici une fois validé.
    def filter_products(self, query=None, criteria=None):
        products = Product.objects.all()

        if query:
            # Diviser la requête en mots
            search_terms = query.lower().split()
            # Pour chaque terme, créer une condition qui vérifie sa présence
            for term in search_terms:
                term_filter = Q(name_ml_clean__icontains=term)
                products = products.filter(term_filter)
        return products


def search_products(request):
    """View for product search with filtering"""
    form = ProductSearchForm(request.GET or None)
    service = ProductService()
    context = {'form': form}

    if form.is_valid():
        query = form.cleaned_data.get('search_query')
        if query:
            products = service.filter_products(
                query=query,
                criteria=form.cleaned_data
            )[:10]  # Limite à 10 résultats

            context.update({
                'products': products,
                'query': query
            })

    return render(request, "product_list.html", context)


# 1- on commence par demander le type de produit recherché, ça envoie vers la fonction filter_products
def recommend_products(request):
    if request.method == 'POST':
        form = ProductRecommendationForm(request.POST)
        if form.is_valid():
            service = ProductService()
            products = list(service.filter_products(
                query=form.cleaned_data['product_type'],
                criteria=form.cleaned_data
            ))  # Convertit en liste pour manipulation

            # Trier les produits selon le nombre de champs renseignés (valeurs non NaN)
            products.sort(key=lambda p: sum(1 for field in p.__dict__.values() if field not in [None, '', []]),
                          reverse=True)

            return render(request, 'monapp/recommendations.html', {'products': products[:6]})  # Garde les 6 premiers
    else:
        form = ProductRecommendationForm()

    return render(request, 'form.html', {'form': form})


class ProductRecommender:

    def __init__(self):
        vectors_path = '/Users/mhalim/PycharmProjects/Racine_nutri/pythonProject/app_nutri/faiss_index/product_vectors.npz'
        self.product_vectors = sparse.load_npz(vectors_path)
        vectorizer_path = '/Users/mhalim/PycharmProjects/Racine_nutri/pythonProject/app_nutri/faiss_index/vectorizer_french.pkl'
        with open(vectorizer_path, 'rb') as f:
            self.vectorizer = pickle.load(f)

        # Charger la liste des produits
        self.products = list(Product.objects.all())

    def get_recommendations(self, product_id, preferences, k=20):
        try:
            base_product_index = next(i for i, product in enumerate(self.products) if product.id == product_id)
            base_product = self.products[base_product_index]
        except (StopIteration, IndexError):
            print(f"Product with ID {product_id} not found.")
            return []

        # Utiliser le vecteur précalculé pour le produit de base
        product_vec = self.product_vectors[base_product_index].reshape(1, -1)

        # Calculer la similarité cosinus entre le produit de base et tous les autres produits
        cosine_similarities = cosine_similarity(product_vec, self.product_vectors).flatten()

        # Obtenir les indices des produits les plus similaires
        similar_indices = cosine_similarities.argsort()[-(k + 1):][::-1]

        # Récupération des produits similaires
        candidates = [self.products[i] for i in similar_indices if i != base_product_index]

        preference_weights = {
            'less_sugar': lambda x: x.sugars_100g,
            'more_protein': lambda x: -x.proteins_100g,
            'better_nutriscore': lambda x: x.nutriscore_score,
            'better_ecoscore': lambda x: -x.ecoscore_score
        }

        active_weights = [preference_weights[key] for key in preferences if preferences[key]]

        if active_weights:
            candidates.sort(key=lambda x: tuple(weight(x) for weight in active_weights))

        return candidates[:4]  # Retourne les 5 meilleures recommandations

    def plot_histogram(self, recommendations, preferences):
        # Déterminer les catégories et récupérer les données
        categories = []
        data = {}

        if preferences.get('less_sugar'):
            categories.append('Sugar')
            data['Sugar'] = [rec.sugars_100g for rec in recommendations]
        if preferences.get('more_protein'):
            categories.append('Protein')
            data['Protein'] = [rec.proteins_100g for rec in recommendations]
        if preferences.get('better_nutriscore'):
            categories.append('Nutriscore')
            data['Nutriscore'] = [rec.nutriscore_score for rec in recommendations]

        categories_no_ecoscore = categories.copy()  # Liste des catégories sans l'écoscore
        categories.append('Ecoscore')  # Toujours afficher l'écoscore
        data['Ecoscore'] = [rec.ecoscore_score for rec in recommendations]

        product_names = [rec.product_name for rec in recommendations]
        num_products = len(recommendations)
        num_categories = len(categories)

        # Indices pour chaque catégorie sur l'axe X
        x = np.arange(len(categories_no_ecoscore))  # Sans l'écoscore pour l'axe principal
        bar_width = 0.15  # Largeur des barres

        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Définir un second axe pour l'écoscore
        ax2 = ax1.twinx()

        # Définir des couleurs uniques pour chaque produit
        colors = plt.cm.tab10(np.linspace(0, 1, num_products))

        # Tracer les barres des autres catégories sur l'axe principal (ax1)
        for i, rec in enumerate(recommendations):
            values = [data[category][i] for category in categories_no_ecoscore]  # Sans l'écoscore
            ax1.bar(x + i * bar_width, values, bar_width, label=rec.product_name, color=colors[i])

        # Tracer l'écoscore sur l'axe secondaire (ax2)
        x_ecoscore = np.array([len(categories_no_ecoscore)])  # Position X pour l'écoscore
        for i, rec in enumerate(recommendations):
            ax2.bar(x_ecoscore + i * bar_width, [data['Ecoscore'][i]], bar_width, color=colors[i], alpha=0.6)

        # Configurer les axes
        ax1.set_xlabel("Categories")
        ax1.set_ylabel("Values (Sucre, Protéines, Nutriscore)")
        ax2.set_ylabel("Ecoscore")
        ax1.set_title("Comparison of Selected Parameters")

        # Ajuster les ticks de l'axe X
        ax1.set_xticks(np.append(x, x_ecoscore))
        ax1.set_xticklabels(categories)  # Ajouter "Ecoscore" en plus

        ax1.legend(title="Products", loc='upper center', bbox_to_anchor=(0.5, -0.15))

        # Sauvegarder le graphique
        chart_path = f"histogram.png"
        full_path = os.path.join("static", chart_path)
        plt.savefig(full_path, bbox_inches='tight')
        plt.close(fig)

        return chart_path


def product_detail(request, product_id):
    # Convertir product_id en UUID
    try:
        product_uuid = uuid.UUID(str(product_id))
    except ValueError:
        raise Http404("Invalid product ID")

    product = get_object_or_404(Product, id=product_uuid)

    if request.method == 'POST':
        preferences = {
            'less_sugar': request.POST.get('less_sugar'),
            'more_protein': request.POST.get('more_protein'),
            'better_nutriscore': request.POST.get('better_nutriscore'),
            'better_ecoscore': request.POST.get('better_ecoscore')
        }

        recommender = ProductRecommender()
        recommendations = recommender.get_recommendations(product_id, preferences)

        # Générer l'histogramme pour les produits recommandés
        chart_path = recommender.plot_histogram(recommendations, preferences)

        return render(request, 'products/recommendations.html', {
            'base_product': product,
            'recommendations': recommendations,
            'chart_path': chart_path
        })

    return render(request, 'products/detail.html', {'product': product})