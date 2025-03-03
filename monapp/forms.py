from django import forms

class ProductRecommendationForm(forms.Form):
    product_type = forms.CharField(label="Type de produit", required=True)

class ProductSearchForm(forms.Form):
    search_query = forms.CharField(
        label="Nom ou type de produit",
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    low_salt = forms.BooleanField(label="Faible en sel", required=False)
    good_for_environment = forms.BooleanField(label="Bon pour l'environnement", required=False)
    low_nutriscore = forms.BooleanField(label="Faible nutriscore", required=False)
    low_energy = forms.BooleanField(label="Faible en calories", required=False)
    high_proteins = forms.BooleanField(label="Riche en protéines", required=False)
    high_fiber = forms.BooleanField(label="Riche en fibres", required=False)
    high_fruits_veggies = forms.BooleanField(label="Riche en fruits et légumes", required=False)
