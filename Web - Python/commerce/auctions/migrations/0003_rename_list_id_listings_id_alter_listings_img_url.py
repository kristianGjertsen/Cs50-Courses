# Generated by Django 5.1.4 on 2025-01-01 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0002_listings_comments"),
    ]

    operations = [
        migrations.RenameField(
            model_name="listings", old_name="list_id", new_name="id",
        ),
        migrations.AlterField(
            model_name="listings",
            name="img_url",
            field=models.CharField(blank=True, max_length=100000),
        ),
    ]
