# Generated by Django 3.2.5 on 2022-08-17 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0002_user_list_academy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_list',
            name='name',
            field=models.CharField(max_length=32, verbose_name='用户名'),
        ),
    ]
