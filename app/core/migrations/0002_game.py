# Generated by Django 4.0.10 on 2024-06-24 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('developer', models.CharField(max_length=255)),
                ('duration', models.PositiveSmallIntegerField(help_text='Average number of hours taken to finish the game.', null=True)),
                ('release_date', models.DateField(null=True)),
                ('in_early_access', models.BooleanField(default=False)),
                ('has_multiplayer', models.BooleanField(default=False)),
            ],
        ),
    ]
