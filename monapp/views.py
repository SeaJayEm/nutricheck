from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.db.models.functions import Length, Lower
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
from django.http import JsonResponse
from .chatbot import NutritionChatbot
from django.db.models import F, ExpressionWrapper, FloatField, Q, Value, Func, CharField
import random
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def accueil(request):
    return render(request, 'monapp/accueil.html')


def index(request):
    return render(request, 'monapp/index.html')


def recherche(request):
    return render(request, 'monapp/recherche.html')


def equipe(request):
    return render(request, 'monapp/equipe.html')

chatbot = NutritionChatbot()

def chat_response(request):
    if request.method == 'POST':
        message = request.POST.get('message', '')
        if message:
            response = chatbot.get_response(message)
            return JsonResponse({'response': response})
    return JsonResponse({'error': 'Invalid request'}, status=400)

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
            products.sort(key=lambda p: sum(1 for field in p.__dict__.values() if field not in [None, '', []]), reverse=True)

            # Mélanger les produits ayant le même nombre de champs renseignés
            grouped_products = {}
            for product in products:
                count = sum(1 for field in product.__dict__.values() if field not in [None, '', []])
                if count not in grouped_products:
                    grouped_products[count] = []
                grouped_products[count].append(product)

            # Mélanger chaque groupe
            for key in grouped_products:
                random.shuffle(grouped_products[key])

            # Aplatir la liste des produits mélangés
            shuffled_products = [product for group in grouped_products.values() for product in group]

            return render(request, 'recommendations.html', {'products': shuffled_products[:6]})  # Garde les 6 premiers
    else:
        form = ProductRecommendationForm()

    return render(request, 'form.html', {'form': form})

class ProductRecommender:
    
    def __init__(self):

        vectors_path = os.path.join(settings.BASE_DIR, 'faiss_index', 'product_vectors.npz')
        vectorizer_path = os.path.join(settings.BASE_DIR, 'faiss_index', 'vectorizer_french.pkl')
        self.product_vectors = sparse.load_npz(vectors_path)

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
            'better_ecoscore': lambda x: -x.ecoscore_score,
            'more_fiber': lambda x: -x.fiber_100g,
            'less_fat': lambda x: x.fat_100g,
            'less_saturated_fat': lambda x: x.saturated_fat_100g,
            'less_salt': lambda x: x.salt_100g
        }

        active_weights = [preference_weights[key] for key in preferences if preferences[key]]

        if active_weights:
            candidates.sort(key=lambda x: tuple(weight(x) for weight in active_weights))

        return candidates[:4]  # Retourne les 4 meilleures recommandations

    def plot_histogram(self, recommendations, preferences):
        # Déterminer les catégories et récupérer les données
        categories = []
        data = {}

        print("Preferences:", preferences)  # Debug: Affiche les préférences

        if preferences.get('less_sugar'):
            categories.append('Sucre (%)')
            data['Sucre (%)'] = [rec.sugars_100g for rec in recommendations]
        if preferences.get('more_protein'):
            categories.append('Protéines (%)')
            data['Protéines (%)'] = [rec.proteins_100g for rec in recommendations]
        if preferences.get('better_ecoscore'):
            categories.append('Ecoscore')
            data['Ecoscore'] = [rec.ecoscore_score for rec in recommendations]
            print("Ecoscore data:", data['Ecoscore'])  # Debug: Affiche les données de l'écoscore
        if preferences.get('more_fiber'):
            categories.append('Fibres (%)')
            data['Fibres (%)'] = [rec.fiber_100g for rec in recommendations]
            print("Fibres data:", data['Fibres (%)'])  # Debug: Affiche les données des fibres
        if preferences.get('less_fat'):
            categories.append('Graisses (%)')
            data['Graisses (%)'] = [rec.fat_100g for rec in recommendations]
            print("Graisses data:", data['Graisses (%)'])  # Debug: Affiche les données des graisses
        if preferences.get('less_saturated_fat'):
            categories.append('Graisses saturées (%)')
            data['Graisses saturées (%)'] = [rec.saturated_fat_100g for rec in recommendations]
        if preferences.get('less_salt'):
            categories.append('Sel (%)')
            data['Sel (%)'] = [rec.salt_100g for rec in recommendations]

        product_names = [f"{rec.product_name} ({rec.brands})" if rec.brands else rec.product_name for rec in recommendations]
        num_products = len(recommendations)

        # Indices pour chaque catégorie sur l'axe X
        x = np.arange(len(categories))  # Pour toutes les catégories
        bar_width = 0.15  # Largeur des barres

        fig, ax1 = plt.subplots(figsize=(14, 8))

        # Définir des couleurs uniques pour chaque produit
        colors = plt.cm.Greens(np.linspace(0.3, 1, num_products))

        # Tracer les barres pour chaque produit
        for i, rec in enumerate(recommendations):
            values = [data[category][i] for category in categories]
            ax1.bar(x + i * bar_width, values, bar_width, label=product_names[i], color=colors[i])

        # Configurer les axes
        ax1.set_xlabel("Catégories", fontsize=18)
        ax1.set_ylabel("Valeurs", fontsize=18)
        ax1.set_title("Comparaison des produits", fontsize=20)

        # Ajuster les ticks de l'axe X
        ax1.set_xticks(x + bar_width * (num_products - 1) / 2)
        ax1.set_xticklabels(categories, fontsize=16)
        ax1.tick_params(axis='both', labelsize=16)

        # Ajouter l'écoscore sur un axe secondaire si demandé
        if 'Ecoscore' in data:
            ax2 = ax1.twinx()
            ax2.set_ylabel("Ecoscore", fontsize=18)
            x_ecoscore = np.array([categories.index('Ecoscore')])  # Position X pour l'écoscore
            for i, rec in enumerate(recommendations):
                ax2.bar(x_ecoscore + i * bar_width, [data['Ecoscore'][i]], bar_width, color=colors[i])
            ax2.tick_params(axis='both', labelsize=16)

        ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), fontsize=16)

        # Utiliser Seaborn pour améliorer l'esthétique
        sns.despine(ax=ax1)

        # Sauvegarder le graphique
        chart_path = f"histogram.png"
        full_path = os.path.join(settings.MEDIA_ROOT, chart_path)

        # Créez le dossier s'il n'existe pas
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        plt.savefig(full_path, bbox_inches='tight')
        plt.close(fig)

        # Créer le graphique des jauges
        self.plot_nutriscore_gauges(recommendations[:4])  # Limité aux 4 premiers produits

        return chart_path


    def plot_nutriscore_gauges(self, recommendations):
        # Créer une figure avec 4 jauges en deux lignes
        fig_jauges = make_subplots(
            rows=2, cols=2,  # 2 lignes, 2 colonnes
            specs=[[{"type": "indicator"}, {"type": "indicator"}],
                   [{"type": "indicator"}, {"type": "indicator"}]],
            vertical_spacing=0.4,  # Ajouter plus d'espace vertical entre les jauges
            horizontal_spacing=0.15  # Ajouter de l'espace horizontal entre les jauges
        )

        # Ajouter les jauges
        for i, rec in enumerate(recommendations):
            # Diviser le nom du produit en deux lignes
            nom_ligne1 = rec.product_name
            nom_ligne2 = f"({rec.brands})" if rec.brands else ""
            score = rec.nutriscore_score
            grade = self.get_nutriscore_grade(score).upper()  # Obtenir le grade en majuscule

            row = i // 2 + 1  # Calculer la ligne
            col = i % 2 + 1  # Calculer la colonne

            # Ajuster le domaine pour ajouter de l'espace en haut
            fig_jauges.update_yaxes(domain=[0.4, 1], row=row, col=col)

            fig_jauges.add_trace(
                go.Indicator(
                    mode="gauge",
                    value=score,
                    title={'text': f"{nom_ligne1}<br>{nom_ligne2} - {grade}", 'font': {'size': 12}},
                    gauge={
                        'axis': {'range': [40, -15], 'tickprefix': '', 'tickfont': {'size': 8}},
                        'bar': {'color': "black", 'thickness': 0.2},
                        'steps': [
                            {'range': [40, 19], 'color': "red"},
                            {'range': [18, 11], 'color': "orange"},
                            {'range': [10, 0], 'color': "yellow"},
                            {'range': [-1, -15], 'color': "lightgreen"}
                        ],
                        'borderwidth': 1,
                        'bordercolor': "white"
                    },

                ),
                row=row, col=col
            )

        # Mise en page du dashboard jauges
        fig_jauges.update_layout(
            title_text="Nutri-Score",
            title_x=0.5,  # Centrer le titre
            title_y=0.95,  # Déplacer le titre vers le haut
            margin=dict(t=100, b=20, l=10, r=10)  # Ajuster les marges
        )

        # Sauvegarder le graphique des jauges
        gauges_path = f"nutriscore_gauges.html"
        full_gauges_path = os.path.join("static", gauges_path)
        fig_jauges.write_html(full_gauges_path)

    def get_nutriscore_grade(self, score):
        # Définir les grades en fonction du score Nutri-Score
        if score <= -1:
            return "a"
        elif score <= 10:
            return "b"
        elif score <= 18:
            return "c"
        elif score <= 40:
            return "d"
        else:
            return "e"

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
            'better_ecoscore': request.POST.get('better_ecoscore'),
            'more_fiber': request.POST.get('more_fiber'),
            'less_fat': request.POST.get('less_fat'),
            'less_saturated_fat': request.POST.get('less_saturated_fat'),
            'less_salt': request.POST.get('less_salt')
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