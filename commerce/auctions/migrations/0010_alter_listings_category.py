# Generated by Django 4.2.3 on 2023-07-11 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_comments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listings',
            name='category',
            field=models.CharField(choices=[('1', 'Fashion'), ('2', 'Toys'), ('3', 'Electronics'), ('4', 'Home'), ('5', 'Other')], max_length=1),
        ),
    ]