# Generated by Django 2.0.3 on 2018-04-17 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0009_auto_20180417_1057'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='number',
        ),
        migrations.AddField(
            model_name='order',
            name='id',
            field=models.AutoField(auto_created=True, default=0, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
    ]
