import os
import django
import pandas as pd
import uuid

# Configure Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projet_nut.settings")
django.setup()

from monapp.models import Product

def import_products(csv_file_path):
    # Lire le fichier CSV
    df = pd.read_csv(csv_file_path)

    # Vérifiez les noms des colonnes
    print("Colonnes disponibles :", df.columns)

    # Remplacer 'NaN' et nan par None
    df = df.replace({'NaN': None})
    df = df.where(pd.notnull(df), None)

    products_created = 0
    for _, row in df.iterrows():
        try:

            Product.objects.create(
                id=uuid.uuid4(),
                #url=row['url'],
                product_name=row['product_name'],
                brands=row['brands'],
                #quantity=row['quantity'],
                categories=row['categories'],
                #labels=row['labels'],
                stores=row['stores'],
                #ingredients_text=row['ingredients_text'],
                cleaned_ingredients=row['cleaned_ingredients'],
                ingredients_analysis_tags=row['ingredients_analysis_tags'],
                nutriscore_score=pd.to_numeric(row.get('nutriscore_score'), errors='coerce'),
                nutriscore_grade=row.get('nutriscore_grade', None),
                #nova_group=pd.to_numeric(row.get('nova_group'), errors='coerce'),
                ecoscore_score=pd.to_numeric(row.get('ecoscore_score'), errors='coerce'),
                ecoscore_grade=row.get('ecoscore_grade', None),
                nutrient_levels_tags=row.get('nutrient_levels_tags', None),
                image_url=row.get('image_url', None),
                #image_ingredients_url=row.get('image_ingredients_url', None),
                #image_nutrition_url=row.get('image_nutrition_url', None),
                fiber_100g=pd.to_numeric(row.get('fiber_100g'), errors='coerce'),
                proteins_100g=pd.to_numeric(row.get('proteins_100g'), errors='coerce'),
                salt_100g=pd.to_numeric(row.get('salt_100g'), errors='coerce'),
                #alcohol_100g=pd.to_numeric(row.get('alcohol_100g'), errors='coerce'),
                #fruits_vegetables_nuts_estimate_from_ingredients_100g=pd.to_numeric(row.get('fruits-vegetables-nuts-estimate-from-ingredients_100g'), errors='coerce'),
                energy_kcal_100g=pd.to_numeric(row.get('energy-kcal_100g'), errors='coerce'),
                fat_100g=pd.to_numeric(row.get('fat_100g'), errors='coerce'),
                saturated_fat_100g=pd.to_numeric(row.get('saturated-fat_100g'), errors='coerce'),
                carbohydrates_100g=pd.to_numeric(row.get('carbohydrates_100g'), errors='coerce'),
                sugars_100g=pd.to_numeric(row.get('sugars_100g'), errors='coerce'),
                name_ml_clean=row.get('name_ml_clean', None),
                name_concat_clean=row.get('name_concat_clean', None),
                combined_text=row.get('combined_text', None),
            )
            products_created += 1
            if products_created % 1000 == 0:
                print(f"{products_created} produits importés...")

        except Exception as e:
            print(f"Erreur lors de l'import de la ligne {_}: {str(e)}")

    return products_created

if __name__ == '__main__':
    csv_path = r'C:\Users\clair\OneDrive\Documents\Wild\Projet_3\projet_nut\data\combined_data.csv'

    print("Début de l'import...")
    nb_products = import_products(csv_path)
    print(f"Import terminé ! {nb_products} produits ont été importés avec succès.")
