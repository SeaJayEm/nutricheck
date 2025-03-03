import os
import django
from django.conf import settings
import scipy.sparse as sparse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projet_nut.settings')
django.setup()

from monapp.models import Product
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

products = list(Product.objects.all())

# Combiner les colonnes sans duplication
combined_texts = [
    f"{product.product_name} {product.brands} {product.categories}"
    for product in products
]

# Réduire le nombre de features
vectorizer = TfidfVectorizer(max_features=5000)  # Réduit à 5000
product_vectors = vectorizer.fit_transform(combined_texts)

# Créer le répertoire
vectors_path = 'C:/Users/clair/OneDrive/Documents/Wild/Projet_3/projet_nut/faiss_index/product_vectors.npz'
os.makedirs(os.path.dirname(vectors_path), exist_ok=True)

# Sauvegarder en format sparse
sparse.save_npz(vectors_path, product_vectors)

# Sauvegarder le vectorizer
import pickle
vectorizer_path = 'C:/Users/clair/OneDrive/Documents/Wild/Projet_3/projet_nut/faiss_index/vectorizer_french.pkl'
with open(vectorizer_path, 'wb') as f:
    pickle.dump(vectorizer, f)

print(f"Vecteurs et vectorizer sauvegardés à {vectors_path} et {vectorizer_path}")