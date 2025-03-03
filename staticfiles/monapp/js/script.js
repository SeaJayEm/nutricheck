async function searchProduct() {
    const searchInput = document.getElementById('searchInput');
    const resultsDiv = document.getElementById('results');

    // Afficher un message de chargement
    resultsDiv.innerHTML = '<p>Recherche en cours...</p>';

    // Utiliser l'API v2 avec une URL modifiée
    const baseUrl = "https://fr.openfoodfacts.org/cgi/search.pl";
    const params = new URLSearchParams({
        search_terms: searchInput.value,
        json: 1,
        action: 'process',
        page_size: 10

    });

    try {
        console.log("Envoi de la requête à :", `${baseUrl}?${params}`);

        const response = await fetch(`${baseUrl}?${params}`, {
            method: 'GET',
            headers: {
                'User-Agent': 'NutriScanApp - Application éducative'
            }
        });

        console.log("Statut de la réponse :", response.status);

        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }

        const data = await response.json();
        console.log("Nombre de produits trouvés :", data.products?.length);

        if (data.products && data.products.length > 0) {
            resultsDiv.innerHTML = data.products.map(product => `
                <div class="product-card">
                    <img src="${product.image_front_url || product.image_url || ''}"
                         alt="${product.product_name}"
                         class="product-image"
                         onerror="this.style.display='none'">

                    <h3 class="product-title">${product.product_name || 'Inconnu'}</h3>

                    <div class="product-details">
                        <p>Marque: ${product.brands || 'Non spécifié'}</p>
                        <p>Quantité: ${product.quantity || 'Non spécifié'}</p>
                        <p>Magasin: ${product.stores || 'Non spécifié'}</p>
                    </div>

                    <div class="nutrients-box">
                        <h4>Nutriments pour 100g</h4>
                        <p>Énergie: ${product.nutriments?.energy_100g || '0'} kcal</p>
                        <p>Protéines: ${product.nutriments?.proteins_100g || '0'} g</p>
                        <p>Sucres: ${product.nutriments?.sugars_100g || '0'} g</p>
                        <p>Sel: ${product.nutriments?.salt_100g || '0'} g</p>
                    </div>

                    <div class="scores">
                        <div class="score-item">
                            <div class="score-circle ${product.nutriscore_grade || 'unknown'}">${product.nutriscore_grade || '?'}</div>
                            <span>Nutri-Score</span>
                        </div>
                        <div class="score-item">
                            <div class="score-circle ${product.ecoscore_grade || 'unknown'}">${product.ecoscore_grade || '?'}</div>
                            <span>Eco-Score</span>
                        </div>
                    </div>
                </div>
            `).join('');
        } else {
            resultsDiv.innerHTML = "<p>Aucun produit trouvé.</p>";
        }
    } catch (error) {
        console.error("Erreur détaillée :", error);
        resultsDiv.innerHTML = `<p class="error">Erreur lors de la recherche : ${error.message}</p>`;
    }
}

// Ajouter les écouteurs d'événements
document.addEventListener('DOMContentLoaded', () => {
    console.log('Script chargé !');

    // Écouteur pour la touche Entrée
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            searchProduct();
        }
    });
});