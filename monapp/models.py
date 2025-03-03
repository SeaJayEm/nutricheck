from django.db import models
import uuid
from django.contrib.postgres.indexes import GinIndex
       
class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #url = models.URLField(max_length=500)
    product_name = models.CharField(max_length=400)
    #quantity = models.CharField(max_length=100, null=True, blank=True)
    brands = models.CharField(max_length=400, null=True, blank=True)
    categories = models.TextField(null=True, blank=True)
    #labels = models.TextField(null=True, blank=True)
    stores = models.TextField(null=True, blank=True)
    #ingredients_text = models.TextField(null=True, blank=True)
    cleaned_ingredients = models.TextField(null=True, blank=True)
    ingredients_analysis_tags = models.TextField(null=True, blank=True)
    nutriscore_score = models.FloatField(null=True, blank=True)
    nutriscore_grade = models.CharField(max_length=10, null=True, blank=True)
    #nova_group = models.FloatField(null=True, blank=True)
    ecoscore_score = models.FloatField(null=True, blank=True)
    ecoscore_grade = models.CharField(max_length=10, null=True, blank=True)
    nutrient_levels_tags = models.TextField(null=True, blank=True)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    #image_ingredients_url = models.URLField(max_length=500, null=True, blank=True)
    #image_nutrition_url = models.URLField(max_length=500, null=True, blank=True)
    fiber_100g = models.FloatField(null=True, blank=True)
    proteins_100g = models.FloatField(null=True, blank=True)
    salt_100g = models.FloatField(null=True, blank=True)
    #alcohol_100g = models.FloatField(null=True, blank=True)
    fruits_vegetables_nuts_estimate_from_ingredients_100g = models.FloatField(null=True, blank=True)
    energy_kcal_100g = models.FloatField(null=True, blank=True)
    fat_100g = models.FloatField(null=True, blank=True)
    saturated_fat_100g = models.FloatField(null=True, blank=True)
    carbohydrates_100g = models.FloatField(null=True, blank=True)
    sugars_100g = models.FloatField(null=True, blank=True)
    name_ml_clean = models.TextField(null=True, blank=True)
    name_concat_clean = models.TextField(null=True, blank=True)
    combined_text = models.TextField(null=True, blank=True)


    def to_feature_vector(self):
        """Convertit le produit en vecteur de caractéristiques pour le ML"""
        return {
            'category': self.categories,
            'ingredients': self.ingredients_text,
            'ecoscore': self.ecoscore_score,
            'nutriscore': self.nutriscore_score,
            'sugar': self.salt_100g,
            'protein': self.proteins_100g,
            'salt': self.salt_100g
        }

    class Meta:
        ordering = ['product_name']
        indexes = [
            GinIndex(fields=["name_ml_clean"], name="name_ml_clean_trgm", opclasses=["gin_trgm_ops"])
        ]

    def __str__(self):
        return f"{self.product_name} ({self.brands})"
