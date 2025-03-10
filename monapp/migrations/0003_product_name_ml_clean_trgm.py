# Generated by Django 5.1.5 on 2025-02-19 18:20

import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("monapp", "0002_remove_product_additives_en_and_more"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="product",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["name_ml_clean"],
                name="name_ml_clean_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ),
    ]
