# Generated by Django 3.2.5 on 2022-08-17 06:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_list',
            name='academy',
            field=models.SmallIntegerField(choices=[(2, '电子信息工程学院'), (6, '计算机学院'), (21, '软件学院')], default=21, verbose_name='学院'),
        ),
    ]
