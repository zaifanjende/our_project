# Generated by Django 5.2.3 on 2025-07-04 04:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web_app', '0017_customuser_full_name_alter_customuser_user_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='farm',
            name='primary_plant_type',
            field=models.ForeignKey(blank=True, help_text='The main or default plant type grown on this farm.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='farms_with_this_primary_type', to='web_app.planttype'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='full_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
