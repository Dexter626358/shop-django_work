# Generated by Django 2.0.3 on 2018-04-17 15:39

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0013_auto_20180417_1538'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('coming_date', models.DateField(blank=True, null=True)),
                ('payed', models.BooleanField(default=False)),
                ('received', models.BooleanField(default=False)),
                ('guest', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='shop.Guest')),
            ],
        ),
        migrations.CreateModel(
            name='Ordered_product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.Order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='shop.Product')),
            ],
        ),
    ]
