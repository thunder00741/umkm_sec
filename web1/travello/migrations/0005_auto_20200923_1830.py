# Generated by Django 3.0.8 on 2020-09-23 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travello', '0004_auto_20200923_1706'),
    ]

    operations = [
        migrations.AlterField(
            model_name='akses_kode',
            name='username',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='buat_survey_fashion',
            name='username',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='buat_survey_makanan_layan_antar',
            name='username',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='buat_survey_makanan_penyedia_jasa',
            name='username',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='buat_survey_makanan_resto',
            name='username',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='buat_survey_makanan_saji',
            name='username',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='buat_survey_umum',
            name='username',
            field=models.IntegerField(),
        ),
    ]