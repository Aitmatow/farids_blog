# Generated by Django 2.2.6 on 2019-10-15 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0005_auto_20191015_2015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='articles', to='webapp.Tag', verbose_name='Теги'),
        ),
    ]
