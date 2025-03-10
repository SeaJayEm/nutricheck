# Generated by Django 5.1.5 on 2025-02-18 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("monapp", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="additives_en",
        ),
        migrations.RemoveField(
            model_name="product",
            name="alcohol_100g",
        ),
        migrations.RemoveField(
            model_name="product",
            name="allergens",
        ),
        migrations.RemoveField(
            model_name="product",
            name="cholesterol_100g",
        ),
        migrations.RemoveField(
            model_name="product",
            name="image_ingredients_url",
        ),
        migrations.RemoveField(
            model_name="product",
            name="image_nutrition_url",
        ),
        migrations.RemoveField(
            model_name="product",
            name="ingredients_text",
        ),
        migrations.RemoveField(
            model_name="product",
            name="labels",
        ),
        migrations.RemoveField(
            model_name="product",
            name="name",
        ),
        migrations.RemoveField(
            model_name="product",
            name="name_concat",
        ),
        migrations.RemoveField(
            model_name="product",
            name="name_ml",
        ),
        migrations.RemoveField(
            model_name="product",
            name="name_split",
        ),
        migrations.RemoveField(
            model_name="product",
            name="name_unique",
        ),
        migrations.RemoveField(
            model_name="product",
            name="nova_group",
        ),
        migrations.RemoveField(
            model_name="product",
            name="origins",
        ),
        migrations.RemoveField(
            model_name="product",
            name="quantity",
        ),
        migrations.RemoveField(
            model_name="product",
            name="serving_size",
        ),
        migrations.RemoveField(
            model_name="product",
            name="traces",
        ),
        migrations.RemoveField(
            model_name="product",
            name="url",
        ),
        migrations.AddField(
            model_name="product",
            name="cleaned_ingredients",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="combined_text",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="name_concat_clean",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="name_ml_clean",
            field=models.TextField(blank=True, null=True),
        ),
    ]
