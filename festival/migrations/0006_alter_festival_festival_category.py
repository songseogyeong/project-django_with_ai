# Generated by Django 5.0.2 on 2024-03-16 21:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('festival', '0005_festival_festival_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='festival',
            name='festival_category',
            field=models.IntegerField(),
        ),
    ]
