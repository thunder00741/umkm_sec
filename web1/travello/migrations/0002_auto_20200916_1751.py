# Generated by Django 3.0.8 on 2020-09-16 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travello', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='buat_survey_fashion',
            name='Segmen',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='buat_survey_makanan_layan_antar',
            name='Segmen',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='buat_survey_makanan_penyedia_jasa',
            name='Segmen',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='buat_survey_makanan_resto',
            name='Segmen',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='buat_survey_makanan_saji',
            name='Segmen',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='buat_survey_umum',
            name='Segmen',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]