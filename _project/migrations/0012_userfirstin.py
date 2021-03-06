# Generated by Django 2.0.3 on 2018-04-12 00:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('_project', '0011_userin'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserFirstIn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('is_first_in', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='_project.User')),
            ],
        ),
    ]
