# Generated by Django 4.0.6 on 2022-07-17 20:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('code', models.IntegerField(unique=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=5)),
                ('mileage', models.IntegerField(default=0)),
                ('is_rented', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Rent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('distance', models.IntegerField(default=0)),
                ('bike', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rents', to='rent.bike')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rents', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='bike',
            name='tenants',
            field=models.ManyToManyField(related_name='bikes', through='rent.Rent', to=settings.AUTH_USER_MODEL),
        ),
    ]
