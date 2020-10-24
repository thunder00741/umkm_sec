from django.urls import path
from . import views

urlpatterns = [
    path("", views.home,name="home"),
    path("home", views.index,name="index"),
    path("responden", views.pelanggan,name="pelanggan"),
    path("kebijakan_syarat_dan_privasi", views.kebijakan,name="kebijakan"),
    path("responden/form", views.umum,name="umum"),
    path("responden/done", views.donesurvey,name="donesurvey"),
    path("owner", views.ownerpage_umum,name="owner_umum"),
    path("owner/rangkuman", views.rangkuman_umum,name="rangkuman_umum"),
    path("owner/rincian", views.rincian_umum,name="rincian_umum"),
    path("fashion", views.fashion,name="fashion"),
    path("makananresto", views.makananresto,name="makananresto"),
    path("makanansaji", views.makanansaji,name="makanansaji"),
    path("makananlayanantar", views.makananlayanantar,name="makananlayanantar"),
    path("makananpenyediasaja", views.makananpenyediasaja,name="makananpenyediasaja"),
    path("owner/hasil_segmentasi/", views.hasil_segmentasi_umum,name="hasil_segmentasi_umum"),
    path("fashion/hasil_segmentasi/", views.hasil_segmentasi_fashion,name="hasil_segmentasi_fashion"),
    path("makananresto/hasil_segmentasi/", views.hasil_segmentasi_makananresto,name="hasil_segmentasi_makananresto"),
    path("makanansaji/hasil_segmentasi/", views.hasil_segmentasi_makanansaji,name="hasil_segmentasi_makanansaji"),
    path("makananlayanantar/hasil_segmentasi/", views.hasil_segmentasi_makananlayanantar,name="hasil_segmentasi_makananlayanantar"),
    path("makananpenyediasaja/hasil_segmentasi/", views.hasil_segmentasi_makananpenyediasaja,name="hasil_segmentasi_makananpenyediasaja"),
]
