from django.contrib import admin
from .models import buat_survey_umum,buat_survey_fashion,buat_survey_makanan_resto,buat_survey_makanan_saji,buat_survey_makanan_layan_antar,buat_survey_makanan_penyedia_jasa

# Register your models here.
admin.site.register(buat_survey_umum)
admin.site.register(buat_survey_fashion)
admin.site.register(buat_survey_makanan_resto)
admin.site.register(buat_survey_makanan_saji)
admin.site.register(buat_survey_makanan_layan_antar)
admin.site.register(buat_survey_makanan_penyedia_jasa)