# Generated by Django 2.0.3 on 2018-04-08 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('_project', '0005_auto_20180408_0000'),
    ]

    operations = [
        migrations.CreateModel(
            name='CountMins',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('today_date', models.DateField(auto_now_add=True)),
                ('count_mins', models.IntegerField()),
            ],
        ),
    ]
