from django.shortcuts import render, redirect
from .models import akses_kode, buat_survey_umum,buat_survey_fashion,buat_survey_makanan_layan_antar,buat_survey_makanan_penyedia_jasa,buat_survey_makanan_resto,buat_survey_makanan_saji
from django.contrib.auth.decorators import login_required
from sklearn.cluster import KMeans
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from kmodes.kmodes import KModes
from sklearn.metrics import silhouette_samples, silhouette_score
import matplotlib.cm as cm
from django.contrib import messages
from django.contrib.auth.models import User, auth
import math
# Create your views here.
pd.set_option('display.max_columns',1000000000000)

def index(request):
    return render(request, "index.html")

def home(request):
    return render(request, "home.html")

def pelanggan(request):
    if request.method == 'POST':
        id_bisnis = int(request.POST['tipe_bisnis'])
        kode = request.POST['kode']
        aduhai = akses_kode.objects.get(username=id_bisnis)
        if kode == aduhai.kode_akses:
            all_id_owner = User.objects.all().values()
            all_id_owner=pd.DataFrame(all_id_owner)
            id_owner = all_id_owner[all_id_owner['id']==id_bisnis]
            tipe_bisnis = np.array(id_owner['last_name'])
            id_owner = id_owner[['id','first_name','last_name']]
            id_owner = id_owner.reset_index(drop=True)
            allData=[]
            for i in range(id_owner.shape[0]):
                temp = id_owner.loc[i]
                allData.append(dict(temp))
            context = {'data': allData}
            print(context)
            if np.any(tipe_bisnis == 'Umum'):
                return render(request, "umum.html", context)
            elif tipe_bisnis == 'Fashion':
                return render(request, "fesyen.html", context)
            elif tipe_bisnis == 'Makanan - restoran & pesan antar':
                return render(request, "makananresto.html", context)
            elif tipe_bisnis == 'Makanan - saji di tempat saja':
                return render(request, "makanansaji.html", context)
            elif tipe_bisnis == 'Makanan - layan antar saja':
                return render(request, "makananlayanantar.html", context)
            elif tipe_bisnis == 'Makanan - penyedia saja (layan antar oleh Gojek/Grab)':
                return render(request, "makanananpenyediajasa.html", context)
        else:
            userdata = User.objects.all().values()
            userdata = pd.DataFrame(userdata)
            userdata = userdata[['first_name', 'id']]
            allData = []
            for i in range(userdata.shape[0]):
                temp = userdata.loc[i]
                allData.append(dict(temp))
            context = {'data': allData}
            return render(request, "pelanggan.html", context)
    else:
        userdata = User.objects.all().values()
        userdata = pd.DataFrame(userdata)
        userdata = userdata[['first_name','id']]
        allData = []
        for i in range(userdata.shape[0]):
            temp = userdata.loc[i]
            allData.append(dict(temp))
        context = {'data': allData}
        return render(request, "pelanggan.html", context)

def kebijakan(request):
    return render(request, "terms.html")

@login_required(login_url="/accounts/login/")

def owner_umum(request):
    username = request.user.id
    megen = akses_kode.objects.get(username=username)
    millyeu = [megen.kode_akses]
    context = {'data': millyeu}
    return render(request, "ownerpage_umum.html",context)

def ownerpage_umum(request):
    if request.method == 'POST':
        username = request.user.id
        kode = request.POST['kode']
        obj = akses_kode.objects.all().values()
        data = pd.DataFrame(obj)
        if username in data['username'].values:
            aduhai = akses_kode.objects.get(username=username)
            aduhai.kode_akses = kode
            aduhai.save()
        else:
            Akses_Kode = akses_kode(username=username, kode_akses=kode)
            Akses_Kode.save()
        megen = akses_kode.objects.get(username=username)
        millyeu = [megen.kode_akses]
        context = {'data': millyeu}
        return render(request, "ownerpage_umum.html",context)
    else:
        username = request.user.id
        try:
            megen = akses_kode.objects.get(username=username)
            millyeu = [megen.kode_akses]
        except:
            millyeu=[]
        context = {'data': millyeu}
        return render(request, "ownerpage_umum.html",context)

def rangkuman_umum(request):
    username = request.user.id
    if request.user.last_name == 'Umum':
        obj = buat_survey_umum.objects.all().values()
    elif request.user.last_name == 'Fashion':
        obj = buat_survey_fashion.objects.all().values()
    elif request.user.last_name == 'Makanan - restoran & pesan antar':
        obj = buat_survey_makanan_resto.objects.all().values()
    elif request.user.last_name == 'Makanan - saji di tempat saja':
        obj = buat_survey_makanan_saji.objects.all().values()
    elif request.user.last_name == 'Makanan - layan antar saja':
        obj = buat_survey_makanan_layan_antar.objects.all().values()
    elif request.user.last_name == 'Makanan - penyedia saja (layan antar oleh Gojek/Grab)':
        obj = buat_survey_makanan_penyedia_jasa.objects.all().values()
    data = pd.DataFrame(obj)
    data = data[data['username'] == username]
    if data.shape[0] <= 4:
        messages.error(request, 'Data Tidak Mencukupi, minimal data adalah 12')
        return redirect('/owner')
    id_data= data['id']
    id_data = id_data.reset_index(drop=True)
    temp = data.drop(['id', 'username', 'responden_name','Segmen'], axis=1)
    temp = temp.reset_index(drop=True)
    webapp = data.drop(['id', 'username', 'responden_name'], axis=1)
    umur = temp['umur']
    njai = []
    for i in range(0,len(umur),1):
        print(umur[i])
        if umur[i] == '<18 Tahun':
            njai.append(1)
        elif umur[i] == '18-23 Tahun':
            njai.append(2)
        elif umur[i] == '24-30 Tahun':
            njai.append(3)
        elif umur[i] == '31-35 Tahun':
            njai.append(4)
        elif umur[i] == '36-40 Tahun':
            njai.append(5)
        elif umur[i] == '41-45 Tahun':
            njai.append(6)
        elif umur[i] == '>45 Tahun':
            njai.append(7)
    temp['umur'] = pd.DataFrame(njai)
    umur = temp['pendapatan']
    njai = []
    for i in range(0, len(umur), 1):
        if umur[i] == '< Rp2.500.000':
            njai.append(1)
        elif umur[i] == 'Rp2.500.000 - Rp5.000.000':
            njai.append(2)
        elif umur[i] == 'Rp5.000.000 - Rp10.000.000':
            njai.append(3)
        elif umur[i] == 'Rp10.000.000 - Rp15.000.000':
            njai.append(4)
        elif umur[i] == 'Rp15.000.000 - Rp25.000.000':
            njai.append(5)
        elif umur[i] == '>Rp25.000.000':
            njai.append(6)
    temp['pendapatan'] = pd.DataFrame(njai)
    if request.user.last_name == 'Umum' or request.user.last_name == 'Fashion':
        umur = temp['frekuensi_pembelian_produk_per_tahun']
        njai = []
        for i in range(0, len(umur), 1):
            if umur[i] == '1 - 2 kali':
                njai.append(1)
            elif umur[i] == '3 - 5 kali':
                njai.append(2)
            elif umur[i] == '> 5 kali':
                njai.append(3)
        temp['frekuensi_pembelian_produk_per_tahun'] = pd.DataFrame(njai)

        umur = temp['jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian']
        njai = []
        for i in range(0, len(umur), 1):
            if umur[i] == 'Rp100.000 - Rp200.000':
                njai.append(1)
            elif umur[i] == 'Rp200.000 - Rp500.000':
                njai.append(2)
            elif umur[i] == 'Rp500.000 - Rp1.000.000':
                njai.append(3)
            elif umur[i] == 'Rp1.000.000 - Rp1.500.000':
                njai.append(4)
            elif umur[i] == '> Rp1.500.000':
                njai.append(5)
        temp['jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'] = pd.DataFrame(njai)

    data = pd.get_dummies(temp)
    if data.shape[0] <= 15:
        range_n_clusters = [2, 3]
    elif data.shape[0] > 15 and data.shape[0] <= 24:
        range_n_clusters = [2, 3, 4]
    elif data.shape[0] > 24 and data.shape[0] <= 35:
        range_n_clusters = [2, 3, 4, 5]
    elif data.shape[0] > 35:
        range_n_clusters = [2, 3, 4, 5, 6]
    print(data)
    cost = []
    klust = []
    for klaster in range_n_clusters:
        clusterer = KModes(n_clusters=klaster, init='Huang', n_init=11, verbose=1)
        preds = clusterer.fit_predict(data)

        score = silhouette_score(data, preds)
        cost.append(score)
        klust.append(klaster)

    cost = pd.DataFrame(cost)
    cost.index = klust
    n_cluster = int(cost.idxmax())

    # define the k-modes model
    km = KModes(n_clusters=n_cluster, init='Huang', n_init=11, verbose=1)
    # fit the clusters to the skills dataframe
    clusters = km.fit_predict(data)
    # get an array of cluster modes
    kmodes = km.cluster_centroids_
    shape = kmodes.shape

    #webapp['Segmen'] = clusters
    #temp['Segmen'] = clusters
    for i in range(0,len(id_data)):
        bleguk=id_data[i]
        if request.user.last_name == 'Umum':
            aduhai = buat_survey_umum.objects.get(id=bleguk)
        elif request.user.last_name == 'Fashion':
            aduhai = buat_survey_fashion.objects.get(id=bleguk)
        elif request.user.last_name == 'Makanan - restoran & pesan antar':
            aduhai = buat_survey_makanan_resto.objects.get(id=bleguk)
        elif request.user.last_name == 'Makanan - saji di tempat saja':
            aduhai = buat_survey_makanan_saji.objects.get(id=bleguk)
        elif request.user.last_name == 'Makanan - layan antar saja':
            aduhai = buat_survey_makanan_layan_antar.objects.get(id=bleguk)
        elif request.user.last_name == 'Makanan - penyedia saja (layan antar oleh Gojek/Grab)':
            aduhai = buat_survey_makanan_penyedia_jasa.objects.get(id=bleguk)
        aduhai.Segmen = clusters[i]
        aduhai.save()

    if request.user.last_name == 'Umum':
        liatin = buat_survey_umum.objects.all().values()
    elif request.user.last_name == 'Fashion':
        liatin = buat_survey_fashion.objects.all().values()
    elif request.user.last_name == 'Makanan - restoran & pesan antar':
        liatin = buat_survey_makanan_resto.objects.all().values()
    elif request.user.last_name == 'Makanan - saji di tempat saja':
        liatin = buat_survey_makanan_saji.objects.all().values()
    elif request.user.last_name == 'Makanan - layan antar saja':
        liatin = buat_survey_makanan_layan_antar.objects.all().values()
    elif request.user.last_name == 'Makanan - penyedia saja (layan antar oleh Gojek/Grab)':
        liatin = buat_survey_makanan_penyedia_jasa.objects.all().values()
    data = pd.DataFrame(liatin)
    if request.user.last_name == 'Umum' or request.user.last_name == 'Fashion':
        data = data[['gender','responden_name','umur','pekerjaan','status','pendapatan','sumber_informasi_mengenai_produk',
                     'frekuensi_pembelian_produk_per_tahun','jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian',
                     'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk',
                     'tempat_penayangan_iklan_atau_placement_yang_paling_menarik','bentuk_iklan_yang_paling_menarik',
                     'konten_iklan_yang_paling_menarik','Segmen']]
        data_column = ['gender','persen_gender', 'responden_name', 'umur','persen_umur', 'pekerjaan','persen_pekerjaan',
                 'status', 'persen_status', 'pendapatan', 'persen_pendapatan', 'sumber_informasi_mengenai_produk', 'persen_sumber_informasi_mengenai_produk',
                              'frekuensi_pembelian_produk_per_tahun', 'persen_frekuensi_pembelian_produk_per_tahun',
                              'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian', 'persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian',
                              'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk', 'persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk',
                              'tempat_penayangan_iklan_atau_placement_yang_paling_menarik', 'persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik',
                              'bentuk_iklan_yang_paling_menarik', 'persen_bentuk_iklan_yang_paling_menarik', 'konten_iklan_yang_paling_menarik', 'persen_konten_iklan_yang_paling_menarik','Segmen']
    elif request.user.last_name == 'Makanan - restoran & pesan antar' or request.user.last_name == 'Makanan - saji di tempat saja' or request.user.last_name == 'Makanan - layan antar saja' or request.user.last_name == 'Makanan - penyedia saja (layan antar oleh Gojek/Grab)':
        data = data[['gender', 'responden_name', 'umur', 'pekerjaan', 'status', 'pendapatan','Segmen']]
        data_column = ['gender','persen_gender', 'responden_name', 'umur','persen_umur', 'pekerjaan','persen_pekerjaan',
                 'status', 'persen_status', 'pendapatan', 'persen_pendapatan', 'Segmen']

    def round_up(n, decimals=0):
        multiplier = 10 ** decimals
        return math.ceil(n * multiplier) / multiplier
    if n_cluster==2:
        data=data.drop(['responden_name'],axis=1)
        clust0=data[data['Segmen']==0]
        ukuran_data0 = clust0.shape[0]
        clust1=data[data['Segmen']==1]
        ukuran_data1 = clust1.shape[0]
        gender0 = clust0['gender'].value_counts().idxmax()
        persen_gender0 = round_up((clust0['gender'].value_counts().max()/ ukuran_data0) * 100,2)
        umur0 = clust0['umur'].value_counts().idxmax()
        persen_umur0 = round_up((clust0['umur'].value_counts().max() / ukuran_data0) * 100,2)
        pekerjaan0 = clust0['pekerjaan'].value_counts().idxmax()
        persen_pekerjaan0 = round_up((clust0['pekerjaan'].value_counts().max() / ukuran_data0) * 100,2)
        status0 = clust0['status'].value_counts().idxmax()
        persen_status0 = round_up((clust0['status'].value_counts().max() / ukuran_data0) * 100,2)
        pendapatan0 = clust0['pendapatan'].value_counts().idxmax()
        persen_pendapatan0 = round_up((clust0['pendapatan'].value_counts().max() / ukuran_data0) * 100,2)
        gender1 = clust1['gender'].value_counts().idxmax()
        persen_gender1 = round_up((clust1['gender'].value_counts().max()/ ukuran_data1) * 100,2)
        umur1 = clust1['umur'].value_counts().idxmax()
        persen_umur1 = round_up((clust1['umur'].value_counts().max() / ukuran_data1) * 100,2)
        pekerjaan1 = clust1['pekerjaan'].value_counts().idxmax()
        persen_pekerjaan1 = round_up((clust1['pekerjaan'].value_counts().max() / ukuran_data1) * 100,2)
        status1 = clust1['status'].value_counts().idxmax()
        persen_status1 = round_up((clust1['status'].value_counts().max() / ukuran_data1) * 100,2)
        pendapatan1 = clust1['pendapatan'].value_counts().idxmax()
        persen_pendapatan1 = round_up((clust1['pendapatan'].value_counts().max() / ukuran_data1) * 100,2)
        if request.user.last_name == 'Umum' or request.user.last_name == 'Fashion':
            sumber_informasi_mengenai_produk0 = clust0['sumber_informasi_mengenai_produk'].value_counts().idxmax()
            persen_sumber_informasi_mengenai_produk0 = round_up((clust0['sumber_informasi_mengenai_produk'].value_counts().max() / ukuran_data0) * 100,2)
            frekuensi_pembelian_produk_per_tahun0 = clust0[
                'frekuensi_pembelian_produk_per_tahun'].value_counts().idxmax()
            persen_frekuensi_pembelian_produk_per_tahun0 = round_up((clust0['frekuensi_pembelian_produk_per_tahun'].value_counts().max() / ukuran_data0) * 100,2)
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian0 = clust0[
                'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().idxmax()
            persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian0 = round_up((clust0['jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().max() / ukuran_data0) * 100,2)
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk0 = clust0[
                'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().idxmax()
            persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk0 = round_up((clust0[
                                                                               'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().max() / ukuran_data0) * 100,2)
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik0 = clust0[
                'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().idxmax()
            persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik0 = round_up((clust0[
                                                                               'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().max() / ukuran_data0) * 100,2)
            bentuk_iklan_yang_paling_menarik0 = clust0['bentuk_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_bentuk_iklan_yang_paling_menarik0 = round_up((clust0['bentuk_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data0) * 100,2)
            konten_iklan_yang_paling_menarik0 = clust0['konten_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_konten_iklan_yang_paling_menarik0 = round_up((clust0[
                                                            'konten_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data0) * 100,2)
            sumber_informasi_mengenai_produk1 = clust1['sumber_informasi_mengenai_produk'].value_counts().idxmax()
            persen_sumber_informasi_mengenai_produk1 = round_up((clust1[
                                                            'sumber_informasi_mengenai_produk'].value_counts().max() / ukuran_data1) * 100,2)
            frekuensi_pembelian_produk_per_tahun1 = clust1[
                'frekuensi_pembelian_produk_per_tahun'].value_counts().idxmax()
            persen_frekuensi_pembelian_produk_per_tahun1 = round_up((clust1[
                                                                'frekuensi_pembelian_produk_per_tahun'].value_counts().max() / ukuran_data1) * 100,2)
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian1 = clust1[
                'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().idxmax()
            persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian1 = round_up((clust1[
                                                                               'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().max() / ukuran_data1) * 100,2)
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk1 = clust1[
                'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().idxmax()
            persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk1 = round_up((clust1[
                                                                                         'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().max() / ukuran_data1) * 100,2)
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik1 = clust1[
                'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().idxmax()
            persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik1 = round_up((clust1[
                                                                                      'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().max() / ukuran_data1) * 100,2)
            bentuk_iklan_yang_paling_menarik1 = clust1['bentuk_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_bentuk_iklan_yang_paling_menarik1 = round_up((clust1[
                                                            'bentuk_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data1) * 100,2)
            konten_iklan_yang_paling_menarik1 = clust1['konten_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_konten_iklan_yang_paling_menarik1 = round_up((clust1[
                                                            'konten_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data1) * 100,2)
        segmen0 = clust0['Segmen'].value_counts().idxmax()
        jumlah_segmen0= clust0['Segmen'].value_counts().max()
        segmen1 = clust1['Segmen'].value_counts().idxmax()
        jumlah_segmen1 = clust1['Segmen'].value_counts().max()

        print('Check Point....')
        gender=pd.DataFrame(np.hstack([gender0,gender1]))
        persen_gender=pd.DataFrame(np.hstack([persen_gender0,persen_gender1]))
        jumlah_segmen=pd.DataFrame(np.hstack([jumlah_segmen0,jumlah_segmen1]))
        umur=pd.DataFrame(np.hstack([umur0,umur1]))
        persen_umur=pd.DataFrame(np.hstack([persen_umur0,persen_umur1]))
        pekerjaan=pd.DataFrame(np.hstack([pekerjaan0,pekerjaan1]))
        persen_pekerjaan=pd.DataFrame(np.hstack([persen_pekerjaan0,persen_pekerjaan1]))
        status=pd.DataFrame(np.hstack([status0,status1]))
        persen_status=pd.DataFrame(np.hstack([persen_status0,persen_status1]))
        pendapatan=pd.DataFrame(np.hstack([pendapatan0,pendapatan1]))
        persen_pendapatan=pd.DataFrame(np.hstack([persen_pendapatan0,persen_pendapatan1]))
        if request.user.last_name == 'Umum' or request.user.last_name == 'Fashion':
            sumber_informasi_mengenai_produk=pd.DataFrame(np.hstack([sumber_informasi_mengenai_produk0,sumber_informasi_mengenai_produk1]))
            persen_sumber_informasi_mengenai_produk=pd.DataFrame(np.hstack([persen_sumber_informasi_mengenai_produk0,persen_sumber_informasi_mengenai_produk1]))
            frekuensi_pembelian_produk_per_tahun=pd.DataFrame(np.hstack([frekuensi_pembelian_produk_per_tahun0,frekuensi_pembelian_produk_per_tahun1]))
            persen_frekuensi_pembelian_produk_per_tahun = pd.DataFrame(
                np.hstack([persen_frekuensi_pembelian_produk_per_tahun0, persen_frekuensi_pembelian_produk_per_tahun1]))
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian=pd.DataFrame(np.hstack([jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian0,jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian1]))
            persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian = pd.DataFrame(
                np.hstack([persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian0, persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian1]))
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk=pd.DataFrame(np.hstack([strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk0,strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk1]))
            persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk = pd.DataFrame(
                np.hstack([persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk0, persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk1]))
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik=pd.DataFrame(np.hstack([tempat_penayangan_iklan_atau_placement_yang_paling_menarik0,tempat_penayangan_iklan_atau_placement_yang_paling_menarik1]))
            persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik = pd.DataFrame(
                np.hstack([persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik0, persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik1]))
            bentuk_iklan_yang_paling_menarik=pd.DataFrame(np.hstack([bentuk_iklan_yang_paling_menarik0,bentuk_iklan_yang_paling_menarik1]))
            persen_bentuk_iklan_yang_paling_menarik = pd.DataFrame(
                np.hstack([persen_bentuk_iklan_yang_paling_menarik0, persen_bentuk_iklan_yang_paling_menarik1]))
            konten_iklan_yang_paling_menarik=pd.DataFrame(np.hstack([konten_iklan_yang_paling_menarik0,konten_iklan_yang_paling_menarik1]))
            persen_konten_iklan_yang_paling_menarik = pd.DataFrame(
                np.hstack([persen_konten_iklan_yang_paling_menarik0, persen_konten_iklan_yang_paling_menarik1]))
        segmen=pd.DataFrame(np.hstack([segmen0,segmen1]))


        print('Kehormatan')
        if request.user.last_name == 'Umum' or request.user.last_name == 'Fashion':
            data_new=pd.concat([gender,persen_gender, jumlah_segmen, umur,persen_umur, pekerjaan,persen_pekerjaan,
                 status, persen_status, pendapatan, persen_pendapatan, sumber_informasi_mengenai_produk, persen_sumber_informasi_mengenai_produk,
                              frekuensi_pembelian_produk_per_tahun, persen_frekuensi_pembelian_produk_per_tahun,
                              jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian, persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian,
                              strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk, persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk,
                              tempat_penayangan_iklan_atau_placement_yang_paling_menarik, persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik,
                              bentuk_iklan_yang_paling_menarik, persen_bentuk_iklan_yang_paling_menarik, konten_iklan_yang_paling_menarik, persen_konten_iklan_yang_paling_menarik,segmen],axis=1)
        elif request.user.last_name == 'Makanan - restoran & pesan antar' or request.user.last_name == 'Makanan - saji di tempat saja' or request.user.last_name == 'Makanan - layan antar saja' or request.user.last_name == 'Makanan - penyedia saja (layan antar oleh Gojek/Grab)':
            data_new = pd.concat(
                [gender,persen_gender, jumlah_segmen, umur,persen_umur, pekerjaan,persen_pekerjaan,
                 status, persen_status, pendapatan, persen_pendapatan, segmen], axis=1)
        print(data_new)
        data_new.columns=data_column
        print('Check......')
    elif n_cluster==3:
        data=data.drop(['responden_name'],axis=1)
        clust0=data[data['Segmen']==0]
        ukuran_data0 = clust0.shape[0]
        clust1=data[data['Segmen']==1]
        ukuran_data1 = clust1.shape[0]
        clust2=data[data['Segmen']==2]
        ukuran_data2 = clust2.shape[0]
        gender0=clust0['gender'].value_counts().idxmax()
        persen_gender0 = round_up((clust0['gender'].value_counts().max()/ ukuran_data0) * 100,2)
        jumlah_segmen0 = clust0['Segmen'].value_counts().max()
        umur0=clust0['umur'].value_counts().idxmax()
        persen_umur0 = round_up((clust0['umur'].value_counts().max()/ ukuran_data0) * 100,2)
        pekerjaan0=clust0['pekerjaan'].value_counts().idxmax()
        persen_pekerjaan0 = round_up((clust0['pekerjaan'].value_counts().max()/ ukuran_data0) * 100,2)
        status0=clust0['status'].value_counts().idxmax()
        persen_status0 = round_up((clust0['status'].value_counts().max()/ ukuran_data0) * 100,2)
        pendapatan0=clust0['pendapatan'].value_counts().idxmax()
        persen_pendapatan0 = round_up((clust0['pendapatan'].value_counts().max()/ ukuran_data0) * 100,2)
        gender1 = clust1['gender'].value_counts().idxmax()
        persen_gender1 = round_up((clust1['gender'].value_counts().max()/ ukuran_data1) * 100,2)
        jumlah_segmen1 = clust1['Segmen'].value_counts().max()
        umur1 = clust1['umur'].value_counts().idxmax()
        persen_umur1 = round_up((clust1['umur'].value_counts().max()/ ukuran_data1) * 100,2)
        pekerjaan1 = clust1['pekerjaan'].value_counts().idxmax()
        persen_pekerjaan1 = round_up((clust1['pekerjaan'].value_counts().max()/ ukuran_data1) * 100,2)
        status1 = clust1['status'].value_counts().idxmax()
        persen_status1 = round_up((clust1['status'].value_counts().max()/ ukuran_data1) * 100,2)
        pendapatan1 = clust1['pendapatan'].value_counts().idxmax()
        persen_pendapatan1 = round_up((clust1['pendapatan'].value_counts().max()/ ukuran_data1) * 100,2)
        gender2 = clust2['gender'].value_counts().idxmax()
        persen_gender2 = round_up((clust2['gender'].value_counts().max()/ ukuran_data2) * 100,2)
        jumlah_segmen2 = clust2['Segmen'].value_counts().max()
        umur2 = clust2['umur'].value_counts().idxmax()
        persen_umur2 = round_up((clust2['umur'].value_counts().max()/ ukuran_data2) * 100,2)
        pekerjaan2 = clust2['pekerjaan'].value_counts().idxmax()
        persen_pekerjaan2 = round_up((clust2['pekerjaan'].value_counts().max()/ ukuran_data2) * 100,2)
        status2 = clust2['status'].value_counts().idxmax()
        persen_status2 = round_up((clust2['status'].value_counts().max()/ ukuran_data2) * 100,2)
        pendapatan2 = clust2['pendapatan'].value_counts().idxmax()
        persen_pendapatan2 = round_up((clust2['pendapatan'].value_counts().max()/ ukuran_data2) * 100,2)
        if request.user.last_name == 'Umum' or request.user.last_name == 'Fashion':
            sumber_informasi_mengenai_produk0 = clust0['sumber_informasi_mengenai_produk'].value_counts().idxmax()
            persen_sumber_informasi_mengenai_produk0 = round_up((clust0[
                                                            'sumber_informasi_mengenai_produk'].value_counts().max() / ukuran_data0) * 100,2)
            frekuensi_pembelian_produk_per_tahun0 = clust0[
                'frekuensi_pembelian_produk_per_tahun'].value_counts().idxmax()
            persen_frekuensi_pembelian_produk_per_tahun0 = round_up((clust0[
                                                                'frekuensi_pembelian_produk_per_tahun'].value_counts().max() / ukuran_data0) * 100,2)
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian0 = clust0[
                'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().idxmax()
            persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian0 = round_up((clust0[
                                                                               'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().max() / ukuran_data0) * 100,2)
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk0 = clust0[
                'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().idxmax()
            persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk0 = round_up((clust0[
                                                                                         'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().max() / ukuran_data0) * 100,2)
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik0 = clust0[
                'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().idxmax()
            persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik0 = round_up((clust0[
                                                                                      'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().max() / ukuran_data0) * 100,2)
            bentuk_iklan_yang_paling_menarik0 = clust0['bentuk_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_bentuk_iklan_yang_paling_menarik0 = round_up((clust0[
                                                            'bentuk_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data0) * 100,2)
            konten_iklan_yang_paling_menarik0 = clust0['konten_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_konten_iklan_yang_paling_menarik0 = round_up((clust0[
                                                            'konten_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data0) * 100,2)
            sumber_informasi_mengenai_produk1 = clust1['sumber_informasi_mengenai_produk'].value_counts().idxmax()
            persen_sumber_informasi_mengenai_produk1 = round_up((clust1[
                                                            'sumber_informasi_mengenai_produk'].value_counts().max() / ukuran_data1) * 100,2)
            frekuensi_pembelian_produk_per_tahun1 = clust1[
                'frekuensi_pembelian_produk_per_tahun'].value_counts().idxmax()
            persen_frekuensi_pembelian_produk_per_tahun1 = round_up((clust1[
                                                                'frekuensi_pembelian_produk_per_tahun'].value_counts().max() / ukuran_data1) * 100,2)
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian1 = clust1[
                'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().idxmax()
            persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian1 = round_up((clust1[
                                                                               'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().max() / ukuran_data1) * 100,2)
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk1 = clust1[
                'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().idxmax()
            persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk1 = round_up((clust1[
                                                                                         'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().max() / ukuran_data1) * 100,2)
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik1 = clust1[
                'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().idxmax()
            persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik1 = round_up((clust1[
                                                                                      'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().max() / ukuran_data1) * 100,2)
            bentuk_iklan_yang_paling_menarik1 = clust1['bentuk_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_bentuk_iklan_yang_paling_menarik1 = round_up((clust1[
                                                            'bentuk_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data1) * 100,2)
            konten_iklan_yang_paling_menarik1 = clust1['konten_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_konten_iklan_yang_paling_menarik1 = round_up((clust1[
                                                            'konten_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data1) * 100,2)
            sumber_informasi_mengenai_produk2 = clust2['sumber_informasi_mengenai_produk'].value_counts().idxmax()
            persen_sumber_informasi_mengenai_produk2 = round_up((clust2[
                                                            'sumber_informasi_mengenai_produk'].value_counts().max() / ukuran_data2) * 100,2)
            frekuensi_pembelian_produk_per_tahun2 = clust2[
                'frekuensi_pembelian_produk_per_tahun'].value_counts().idxmax()
            persen_frekuensi_pembelian_produk_per_tahun2 = round_up((clust2[
                                                                'frekuensi_pembelian_produk_per_tahun'].value_counts().max() / ukuran_data2) * 100,2)
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian2 = clust2[
                'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().idxmax()
            persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian2 = round_up((clust2[
                                                                               'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().max() / ukuran_data2) * 100,2)
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk2 = clust2[
                'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().idxmax()
            persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk2 = round_up((clust2[
                                                                                         'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().max() / ukuran_data2) * 100,2)
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik2 = clust2[
                'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().idxmax()
            persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik2 = round_up((clust2[
                                                                                      'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().max() / ukuran_data2) * 100,2)
            bentuk_iklan_yang_paling_menarik2 = clust2['bentuk_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_bentuk_iklan_yang_paling_menarik2 = round_up((clust2[
                                                            'bentuk_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data2) * 100,2)
            konten_iklan_yang_paling_menarik2 = clust2['konten_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_konten_iklan_yang_paling_menarik2 = round_up((clust2[
                                                            'konten_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data2) * 100,2)
        segmen0=clust0['Segmen'].value_counts().idxmax()
        segmen1 = clust1['Segmen'].value_counts().idxmax()
        segmen2 = clust2['Segmen'].value_counts().idxmax()


        persen_gender = pd.DataFrame(np.hstack([persen_gender0, persen_gender1, persen_gender2]))
        persen_umur = pd.DataFrame(np.hstack([persen_umur0, persen_umur1, persen_umur2]))
        persen_pekerjaan = pd.DataFrame(np.hstack([persen_pekerjaan0, persen_pekerjaan1, persen_pekerjaan2]))
        persen_status = pd.DataFrame(np.hstack([persen_status0, persen_status1, persen_status2]))
        persen_pendapatan = pd.DataFrame(np.hstack([persen_pendapatan0, persen_pendapatan1, persen_pendapatan2]))
        gender = pd.DataFrame(np.hstack([gender0, gender1, gender2]))
        jumlah_segmen=pd.DataFrame(np.hstack([jumlah_segmen0,jumlah_segmen1,jumlah_segmen2]))
        umur = pd.DataFrame(np.hstack([umur0, umur1, umur2]))
        pekerjaan = pd.DataFrame(np.hstack([pekerjaan0, pekerjaan1, pekerjaan2]))
        status = pd.DataFrame(np.hstack([status0, status1, status2]))
        pendapatan = pd.DataFrame(np.hstack([pendapatan0, pendapatan1, pendapatan2]))
        if request.user.last_name == 'Umum' or request.user.last_name == 'Fashion':
            sumber_informasi_mengenai_produk = pd.DataFrame(
                np.hstack([sumber_informasi_mengenai_produk0, sumber_informasi_mengenai_produk1, sumber_informasi_mengenai_produk2]))
            persen_sumber_informasi_mengenai_produk = pd.DataFrame(
                np.hstack([persen_sumber_informasi_mengenai_produk0, persen_sumber_informasi_mengenai_produk1, persen_sumber_informasi_mengenai_produk2]))
            frekuensi_pembelian_produk_per_tahun = pd.DataFrame(
                np.hstack([frekuensi_pembelian_produk_per_tahun0, frekuensi_pembelian_produk_per_tahun1, frekuensi_pembelian_produk_per_tahun2]))
            persen_frekuensi_pembelian_produk_per_tahun = pd.DataFrame(
                np.hstack(
                    [persen_frekuensi_pembelian_produk_per_tahun0, persen_frekuensi_pembelian_produk_per_tahun1, persen_frekuensi_pembelian_produk_per_tahun2]))
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian = pd.DataFrame(np.hstack(
                [jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian0,
                 jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian1,
                 jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian2]))
            persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian = pd.DataFrame(
                np.hstack([persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian0,
                           persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian1,
                           persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian2]))
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk = pd.DataFrame(np.hstack(
                [strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk0,
                 strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk1,
                 strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk2]))
            persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk = pd.DataFrame(
                np.hstack([persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk0,
                           persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk1,
                           persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk2]))
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik = pd.DataFrame(np.hstack(
                [tempat_penayangan_iklan_atau_placement_yang_paling_menarik0,
                 tempat_penayangan_iklan_atau_placement_yang_paling_menarik1,
                 tempat_penayangan_iklan_atau_placement_yang_paling_menarik2]))
            persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik = pd.DataFrame(
                np.hstack([persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik0,
                           persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik1,
                           persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik2]))
            bentuk_iklan_yang_paling_menarik = pd.DataFrame(
                np.hstack([bentuk_iklan_yang_paling_menarik0, bentuk_iklan_yang_paling_menarik1, bentuk_iklan_yang_paling_menarik2]))
            persen_bentuk_iklan_yang_paling_menarik = pd.DataFrame(
                np.hstack([persen_bentuk_iklan_yang_paling_menarik0, persen_bentuk_iklan_yang_paling_menarik1, persen_bentuk_iklan_yang_paling_menarik2]))
            konten_iklan_yang_paling_menarik = pd.DataFrame(
                np.hstack([konten_iklan_yang_paling_menarik0, konten_iklan_yang_paling_menarik1, konten_iklan_yang_paling_menarik2]))
            persen_konten_iklan_yang_paling_menarik = pd.DataFrame(
                np.hstack([persen_konten_iklan_yang_paling_menarik0, persen_konten_iklan_yang_paling_menarik1, persen_konten_iklan_yang_paling_menarik2]))
        segmen = pd.DataFrame(np.hstack([segmen0, segmen1, segmen2]))

        if request.user.last_name == 'Umum' or request.user.last_name == 'Fashion':
            data_new = pd.concat(
                [gender, persen_gender, jumlah_segmen, umur, persen_umur, pekerjaan, persen_pekerjaan,
                 status, persen_status, pendapatan, persen_pendapatan, sumber_informasi_mengenai_produk,
                 persen_sumber_informasi_mengenai_produk,
                 frekuensi_pembelian_produk_per_tahun, persen_frekuensi_pembelian_produk_per_tahun,
                 jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian,
                 persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian,
                 strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk,
                 persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk,
                 tempat_penayangan_iklan_atau_placement_yang_paling_menarik,
                 persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik,
                 bentuk_iklan_yang_paling_menarik, persen_bentuk_iklan_yang_paling_menarik,
                 konten_iklan_yang_paling_menarik, persen_konten_iklan_yang_paling_menarik, segmen], axis=1)
        elif request.user.last_name == 'Makanan - restoran & pesan antar' or request.user.last_name == 'Makanan - saji di tempat saja' or request.user.last_name == 'Makanan - layan antar saja' or request.user.last_name == 'Makanan - penyedia saja (layan antar oleh Gojek/Grab)':
            data_new = pd.concat(
                [gender, persen_gender, jumlah_segmen, umur, persen_umur, pekerjaan, persen_pekerjaan,
                 status, persen_status, pendapatan, persen_pendapatan, segmen], axis=1)
        print(data_column)
        print(data_new)
        data_new.columns=data_column
    elif n_cluster==4:
        data=data.drop(['responden_name'],axis=1)
        clust0=data[data['Segmen']==0]
        ukuran_data0 = clust0.shape[0]
        clust1=data[data['Segmen']==1]
        ukuran_data1 = clust1.shape[0]
        clust2=data[data['Segmen']==2]
        ukuran_data2 = clust2.shape[0]
        clust3=data[data['Segmen']==3]
        ukuran_data3 = clust3.shape[0]
        gender0=clust0['gender'].value_counts().idxmax()
        persen_gender0 = round_up((clust0['gender'].value_counts().max()/ ukuran_data0) * 100,2)
        jumlah_segmen0 = clust0['Segmen'].value_counts().max()
        umur0=clust0['umur'].value_counts().idxmax()
        persen_umur0 = round_up((clust0['umur'].value_counts().max()/ ukuran_data0) * 100,2)
        pekerjaan0=clust0['pekerjaan'].value_counts().idxmax()
        persen_pekerjaan0 = round_up((clust0['pekerjaan'].value_counts().max()/ ukuran_data0) * 100,2)
        status0=clust0['status'].value_counts().idxmax()
        persen_status0 = round_up((clust0['status'].value_counts().max()/ ukuran_data0) * 100,2)
        pendapatan0=clust0['pendapatan'].value_counts().idxmax()
        persen_pendapatan0 = round_up((clust0['pendapatan'].value_counts().max()/ ukuran_data0) * 100,2)
        gender1 = clust1['gender'].value_counts().idxmax()
        persen_gender1 = round_up((clust1['gender'].value_counts().max()/ ukuran_data1) * 100,2)
        jumlah_segmen1 = clust1['Segmen'].value_counts().max()
        umur1 = clust1['umur'].value_counts().idxmax()
        persen_umur1 = round_up((clust1['umur'].value_counts().max()/ ukuran_data1) * 100,2)
        pekerjaan1 = clust1['pekerjaan'].value_counts().idxmax()
        persen_pekerjaan1 = round_up((clust1['pekerjaan'].value_counts().max()/ ukuran_data1) * 100,2)
        status1 = clust1['status'].value_counts().idxmax()
        persen_status1 = round_up((clust1['status'].value_counts().max()/ ukuran_data1) * 100,2)
        pendapatan1 = clust1['pendapatan'].value_counts().idxmax()
        persen_pendapatan1 = round_up((clust1['pendapatan'].value_counts().max()/ ukuran_data1) * 100,2)
        gender2 = clust2['gender'].value_counts().idxmax()
        persen_gender2 = round_up((clust2['gender'].value_counts().max()/ ukuran_data2) * 100,2)
        jumlah_segmen2 = clust2['Segmen'].value_counts().max()
        umur2 = clust2['umur'].value_counts().idxmax()
        persen_umur2 = round_up((clust2['umur'].value_counts().max()/ ukuran_data2) * 100,2)
        pekerjaan2 = clust2['pekerjaan'].value_counts().idxmax()
        persen_pekerjaan2 = round_up((clust2['pekerjaan'].value_counts().max()/ ukuran_data2) * 100,2)
        status2 = clust2['status'].value_counts().idxmax()
        persen_status2 = round_up((clust2['status'].value_counts().max()/ ukuran_data2) * 100,2)
        pendapatan2 = clust2['pendapatan'].value_counts().idxmax()
        persen_pendapatan2 = round_up((clust2['pendapatan'].value_counts().max()/ ukuran_data2) * 100,2)
        gender3 = clust3['gender'].value_counts().idxmax()
        persen_gender3 = round_up((clust3['gender'].value_counts().max() / ukuran_data3) * 100, 2)
        jumlah_segmen3 = clust3['Segmen'].value_counts().max()
        umur3 = clust3['umur'].value_counts().idxmax()
        persen_umur3 = round_up((clust3['umur'].value_counts().max() / ukuran_data3) * 100, 2)
        pekerjaan3 = clust3['pekerjaan'].value_counts().idxmax()
        persen_pekerjaan3 = round_up((clust3['pekerjaan'].value_counts().max() / ukuran_data3) * 100, 2)
        status3 = clust3['status'].value_counts().idxmax()
        persen_status3 = round_up((clust3['status'].value_counts().max() / ukuran_data3) * 100, 2)
        pendapatan3 = clust3['pendapatan'].value_counts().idxmax()
        persen_pendapatan3 = round_up((clust3['pendapatan'].value_counts().max() / ukuran_data3) * 100, 2)
        if request.user.last_name == 'Umum' or request.user.last_name == 'Fashion':
            sumber_informasi_mengenai_produk0 = clust0['sumber_informasi_mengenai_produk'].value_counts().idxmax()
            persen_sumber_informasi_mengenai_produk0 = round_up((clust0[
                                                            'sumber_informasi_mengenai_produk'].value_counts().max() / ukuran_data0) * 100,2)
            frekuensi_pembelian_produk_per_tahun0 = clust0[
                'frekuensi_pembelian_produk_per_tahun'].value_counts().idxmax()
            persen_frekuensi_pembelian_produk_per_tahun0 = round_up((clust0[
                                                                'frekuensi_pembelian_produk_per_tahun'].value_counts().max() / ukuran_data0) * 100,2)
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian0 = clust0[
                'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().idxmax()
            persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian0 = round_up((clust0[
                                                                               'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().max() / ukuran_data0) * 100,2)
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk0 = clust0[
                'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().idxmax()
            persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk0 = round_up((clust0[
                                                                                         'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().max() / ukuran_data0) * 100,2)
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik0 = clust0[
                'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().idxmax()
            persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik0 = round_up((clust0[
                                                                                      'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().max() / ukuran_data0) * 100,2)
            bentuk_iklan_yang_paling_menarik0 = clust0['bentuk_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_bentuk_iklan_yang_paling_menarik0 = round_up((clust0[
                                                            'bentuk_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data0) * 100,2)
            konten_iklan_yang_paling_menarik0 = clust0['konten_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_konten_iklan_yang_paling_menarik0 = round_up((clust0[
                                                            'konten_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data0) * 100,2)
            sumber_informasi_mengenai_produk1 = clust1['sumber_informasi_mengenai_produk'].value_counts().idxmax()
            persen_sumber_informasi_mengenai_produk1 = round_up((clust1[
                                                            'sumber_informasi_mengenai_produk'].value_counts().max() / ukuran_data1) * 100,2)
            frekuensi_pembelian_produk_per_tahun1 = clust1[
                'frekuensi_pembelian_produk_per_tahun'].value_counts().idxmax()
            persen_frekuensi_pembelian_produk_per_tahun1 = round_up((clust1[
                                                                'frekuensi_pembelian_produk_per_tahun'].value_counts().max() / ukuran_data1) * 100,2)
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian1 = clust1[
                'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().idxmax()
            persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian1 = round_up((clust1[
                                                                               'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().max() / ukuran_data1) * 100,2)
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk1 = clust1[
                'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().idxmax()
            persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk1 = round_up((clust1[
                                                                                         'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().max() / ukuran_data1) * 100,2)
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik1 = clust1[
                'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().idxmax()
            persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik1 = round_up((clust1[
                                                                                      'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().max() / ukuran_data1) * 100,2)
            bentuk_iklan_yang_paling_menarik1 = clust1['bentuk_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_bentuk_iklan_yang_paling_menarik1 = round_up((clust1[
                                                            'bentuk_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data1) * 100,2)
            konten_iklan_yang_paling_menarik1 = clust1['konten_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_konten_iklan_yang_paling_menarik1 = round_up((clust1[
                                                            'konten_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data1) * 100,2)
            sumber_informasi_mengenai_produk2 = clust2['sumber_informasi_mengenai_produk'].value_counts().idxmax()
            persen_sumber_informasi_mengenai_produk2 = round_up((clust2[
                                                            'sumber_informasi_mengenai_produk'].value_counts().max() / ukuran_data2) * 100,2)
            frekuensi_pembelian_produk_per_tahun2 = clust2[
                'frekuensi_pembelian_produk_per_tahun'].value_counts().idxmax()
            persen_frekuensi_pembelian_produk_per_tahun2 = round_up((clust2[
                                                                'frekuensi_pembelian_produk_per_tahun'].value_counts().max() / ukuran_data2) * 100,2)
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian2 = clust2[
                'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().idxmax()
            persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian2 = round_up((clust2[
                                                                               'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().max() / ukuran_data2) * 100,2)
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk2 = clust2[
                'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().idxmax()
            persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk2 = round_up((clust2[
                                                                                         'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().max() / ukuran_data2) * 100,2)
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik2 = clust2[
                'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().idxmax()
            persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik2 = round_up((clust2[
                                                                                      'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().max() / ukuran_data2) * 100,2)
            bentuk_iklan_yang_paling_menarik2 = clust2['bentuk_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_bentuk_iklan_yang_paling_menarik2 = round_up((clust2[
                                                            'bentuk_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data2) * 100,2)
            konten_iklan_yang_paling_menarik2 = clust2['konten_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_konten_iklan_yang_paling_menarik2 = round_up((clust2[
                                                            'konten_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data2) * 100,2)
            sumber_informasi_mengenai_produk3 = clust3['sumber_informasi_mengenai_produk'].value_counts().idxmax()
            persen_sumber_informasi_mengenai_produk3 = round_up((clust3[
                                                                     'sumber_informasi_mengenai_produk'].value_counts().max() / ukuran_data3) * 100,
                                                                2)
            frekuensi_pembelian_produk_per_tahun3 = clust3[
                'frekuensi_pembelian_produk_per_tahun'].value_counts().idxmax()
            persen_frekuensi_pembelian_produk_per_tahun3 = round_up((clust3[
                                                                         'frekuensi_pembelian_produk_per_tahun'].value_counts().max() / ukuran_data3) * 100,
                                                                    2)
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian3 = clust3[
                'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().idxmax()
            persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian3 = round_up((clust3[
                                                                                        'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().max() / ukuran_data3) * 100,
                                                                                   2)
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk3 = clust3[
                'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().idxmax()
            persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk3 = round_up((clust3[
                                                                                                  'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().max() / ukuran_data3) * 100,
                                                                                             2)
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik3 = clust3[
                'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().idxmax()
            persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik3 = round_up((clust3[
                                                                                               'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().max() / ukuran_data3) * 100,
                                                                                          2)
            bentuk_iklan_yang_paling_menarik3 = clust3['bentuk_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_bentuk_iklan_yang_paling_menarik3 = round_up((clust3[
                                                                     'bentuk_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data3) * 100,
                                                                2)
            konten_iklan_yang_paling_menarik3 = clust3['konten_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_konten_iklan_yang_paling_menarik3 = round_up((clust3[
                                                                     'konten_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data3) * 100,
                                                                2)
        segmen0=clust0['Segmen'].value_counts().idxmax()
        segmen1 = clust1['Segmen'].value_counts().idxmax()
        segmen2 = clust2['Segmen'].value_counts().idxmax()
        segmen3 = clust3['Segmen'].value_counts().idxmax()


        persen_gender = pd.DataFrame(np.hstack([persen_gender0, persen_gender1, persen_gender2, persen_gender3]))
        persen_umur = pd.DataFrame(np.hstack([persen_umur0, persen_umur1, persen_umur2, persen_umur3]))
        persen_pekerjaan = pd.DataFrame(np.hstack([persen_pekerjaan0, persen_pekerjaan1, persen_pekerjaan2, persen_pekerjaan3]))
        persen_status = pd.DataFrame(np.hstack([persen_status0, persen_status1, persen_status2, persen_status3]))
        persen_pendapatan = pd.DataFrame(np.hstack([persen_pendapatan0, persen_pendapatan1, persen_pendapatan2, persen_pendapatan3]))
        gender = pd.DataFrame(np.hstack([gender0, gender1, gender2, gender3]))
        jumlah_segmen=pd.DataFrame(np.hstack([jumlah_segmen0,jumlah_segmen1,jumlah_segmen2,jumlah_segmen3]))
        umur = pd.DataFrame(np.hstack([umur0, umur1, umur2, umur3]))
        pekerjaan = pd.DataFrame(np.hstack([pekerjaan0, pekerjaan1, pekerjaan2, pekerjaan3]))
        status = pd.DataFrame(np.hstack([status0, status1, status2, status3]))
        pendapatan = pd.DataFrame(np.hstack([pendapatan0, pendapatan1, pendapatan2, pendapatan3]))
        if request.user.last_name == 'Umum' or request.user.last_name == 'Fashion':
            sumber_informasi_mengenai_produk = pd.DataFrame(
                np.hstack([sumber_informasi_mengenai_produk0, sumber_informasi_mengenai_produk1, sumber_informasi_mengenai_produk2, sumber_informasi_mengenai_produk3]))
            persen_sumber_informasi_mengenai_produk = pd.DataFrame(
                np.hstack([persen_sumber_informasi_mengenai_produk0, persen_sumber_informasi_mengenai_produk1, persen_sumber_informasi_mengenai_produk2, persen_sumber_informasi_mengenai_produk3]))
            frekuensi_pembelian_produk_per_tahun = pd.DataFrame(
                np.hstack([frekuensi_pembelian_produk_per_tahun0, frekuensi_pembelian_produk_per_tahun1, frekuensi_pembelian_produk_per_tahun2, frekuensi_pembelian_produk_per_tahun3]))
            persen_frekuensi_pembelian_produk_per_tahun = pd.DataFrame(
                np.hstack(
                    [persen_frekuensi_pembelian_produk_per_tahun0, persen_frekuensi_pembelian_produk_per_tahun1, persen_frekuensi_pembelian_produk_per_tahun2, persen_frekuensi_pembelian_produk_per_tahun3]))
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian = pd.DataFrame(np.hstack(
                [jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian0,
                 jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian1,
                 jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian2,
                 jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian3]))
            persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian = pd.DataFrame(
                np.hstack([persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian0,
                           persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian1,
                           persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian2,
                           persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian3]))
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk = pd.DataFrame(np.hstack(
                [strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk0,
                 strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk1,
                 strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk2,
                 strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk3]))
            persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk = pd.DataFrame(
                np.hstack([persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk0,
                           persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk1,
                           persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk2,
                           persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk3]))
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik = pd.DataFrame(np.hstack(
                [tempat_penayangan_iklan_atau_placement_yang_paling_menarik0,
                 tempat_penayangan_iklan_atau_placement_yang_paling_menarik1,
                 tempat_penayangan_iklan_atau_placement_yang_paling_menarik2,
                 tempat_penayangan_iklan_atau_placement_yang_paling_menarik3]))
            persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik = pd.DataFrame(
                np.hstack([persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik0,
                           persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik1,
                           persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik2,
                           persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik3]))
            bentuk_iklan_yang_paling_menarik = pd.DataFrame(
                np.hstack([bentuk_iklan_yang_paling_menarik0, bentuk_iklan_yang_paling_menarik1, bentuk_iklan_yang_paling_menarik2, bentuk_iklan_yang_paling_menarik3]))
            persen_bentuk_iklan_yang_paling_menarik = pd.DataFrame(
                np.hstack([persen_bentuk_iklan_yang_paling_menarik0, persen_bentuk_iklan_yang_paling_menarik1, persen_bentuk_iklan_yang_paling_menarik2, persen_bentuk_iklan_yang_paling_menarik3]))
            konten_iklan_yang_paling_menarik = pd.DataFrame(
                np.hstack([konten_iklan_yang_paling_menarik0, konten_iklan_yang_paling_menarik1, konten_iklan_yang_paling_menarik2, konten_iklan_yang_paling_menarik3]))
            persen_konten_iklan_yang_paling_menarik = pd.DataFrame(
                np.hstack([persen_konten_iklan_yang_paling_menarik0, persen_konten_iklan_yang_paling_menarik1, persen_konten_iklan_yang_paling_menarik2, persen_konten_iklan_yang_paling_menarik3]))
        segmen = pd.DataFrame(np.hstack([segmen0, segmen1, segmen2, segmen3]))

        if request.user.last_name == 'Umum' or request.user.last_name == 'Fashion':
            data_new = pd.concat(
                [gender, persen_gender, jumlah_segmen, umur, persen_umur, pekerjaan, persen_pekerjaan,
                 status, persen_status, pendapatan, persen_pendapatan, sumber_informasi_mengenai_produk,
                 persen_sumber_informasi_mengenai_produk,
                 frekuensi_pembelian_produk_per_tahun, persen_frekuensi_pembelian_produk_per_tahun,
                 jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian,
                 persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian,
                 strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk,
                 persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk,
                 tempat_penayangan_iklan_atau_placement_yang_paling_menarik,
                 persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik,
                 bentuk_iklan_yang_paling_menarik, persen_bentuk_iklan_yang_paling_menarik,
                 konten_iklan_yang_paling_menarik, persen_konten_iklan_yang_paling_menarik, segmen], axis=1)
        elif request.user.last_name == 'Makanan - restoran & pesan antar' or request.user.last_name == 'Makanan - saji di tempat saja' or request.user.last_name == 'Makanan - layan antar saja' or request.user.last_name == 'Makanan - penyedia saja (layan antar oleh Gojek/Grab)':
            data_new = pd.concat(
                [gender, persen_gender, jumlah_segmen, umur, persen_umur, pekerjaan, persen_pekerjaan,
                 status, persen_status, pendapatan, persen_pendapatan, segmen], axis=1)
        print(data_column)
        print(data_new)
        data_new.columns=data_column
    elif n_cluster==5:
        data=data.drop(['responden_name'],axis=1)
        clust0=data[data['Segmen']==0]
        ukuran_data0 = clust0.shape[0]
        clust1=data[data['Segmen']==1]
        ukuran_data1 = clust1.shape[0]
        clust2=data[data['Segmen']==2]
        ukuran_data2 = clust2.shape[0]
        clust3=data[data['Segmen']==3]
        ukuran_data3 = clust3.shape[0]
        clust4=data[data['Segmen']==4]
        ukuran_data4 = clust4.shape[0]
        gender0=clust0['gender'].value_counts().idxmax()
        persen_gender0 = round_up((clust0['gender'].value_counts().max()/ ukuran_data0) * 100,2)
        jumlah_segmen0 = clust0['Segmen'].value_counts().max()
        umur0=clust0['umur'].value_counts().idxmax()
        persen_umur0 = round_up((clust0['umur'].value_counts().max()/ ukuran_data0) * 100,2)
        pekerjaan0=clust0['pekerjaan'].value_counts().idxmax()
        persen_pekerjaan0 = round_up((clust0['pekerjaan'].value_counts().max()/ ukuran_data0) * 100,2)
        status0=clust0['status'].value_counts().idxmax()
        persen_status0 = round_up((clust0['status'].value_counts().max()/ ukuran_data0) * 100,2)
        pendapatan0=clust0['pendapatan'].value_counts().idxmax()
        persen_pendapatan0 = round_up((clust0['pendapatan'].value_counts().max()/ ukuran_data0) * 100,2)
        gender1 = clust1['gender'].value_counts().idxmax()
        persen_gender1 = round_up((clust1['gender'].value_counts().max()/ ukuran_data1) * 100,2)
        jumlah_segmen1 = clust1['Segmen'].value_counts().max()
        umur1 = clust1['umur'].value_counts().idxmax()
        persen_umur1 = round_up((clust1['umur'].value_counts().max()/ ukuran_data1) * 100,2)
        pekerjaan1 = clust1['pekerjaan'].value_counts().idxmax()
        persen_pekerjaan1 = round_up((clust1['pekerjaan'].value_counts().max()/ ukuran_data1) * 100,2)
        status1 = clust1['status'].value_counts().idxmax()
        persen_status1 = round_up((clust1['status'].value_counts().max()/ ukuran_data1) * 100,2)
        pendapatan1 = clust1['pendapatan'].value_counts().idxmax()
        persen_pendapatan1 = round_up((clust1['pendapatan'].value_counts().max()/ ukuran_data1) * 100,2)
        gender2 = clust2['gender'].value_counts().idxmax()
        persen_gender2 = round_up((clust2['gender'].value_counts().max()/ ukuran_data2) * 100,2)
        jumlah_segmen2 = clust2['Segmen'].value_counts().max()
        umur2 = clust2['umur'].value_counts().idxmax()
        persen_umur2 = round_up((clust2['umur'].value_counts().max()/ ukuran_data2) * 100,2)
        pekerjaan2 = clust2['pekerjaan'].value_counts().idxmax()
        persen_pekerjaan2 = round_up((clust2['pekerjaan'].value_counts().max()/ ukuran_data2) * 100,2)
        status2 = clust2['status'].value_counts().idxmax()
        persen_status2 = round_up((clust2['status'].value_counts().max()/ ukuran_data2) * 100,2)
        pendapatan2 = clust2['pendapatan'].value_counts().idxmax()
        persen_pendapatan2 = round_up((clust2['pendapatan'].value_counts().max()/ ukuran_data2) * 100,2)
        gender3 = clust3['gender'].value_counts().idxmax()
        persen_gender3 = round_up((clust3['gender'].value_counts().max() / ukuran_data3) * 100, 2)
        jumlah_segmen3 = clust3['Segmen'].value_counts().max()
        umur3 = clust3['umur'].value_counts().idxmax()
        persen_umur3 = round_up((clust3['umur'].value_counts().max() / ukuran_data3) * 100, 2)
        pekerjaan3 = clust3['pekerjaan'].value_counts().idxmax()
        persen_pekerjaan3 = round_up((clust3['pekerjaan'].value_counts().max() / ukuran_data3) * 100, 2)
        status3 = clust3['status'].value_counts().idxmax()
        persen_status3 = round_up((clust3['status'].value_counts().max() / ukuran_data3) * 100, 2)
        pendapatan3 = clust3['pendapatan'].value_counts().idxmax()
        persen_pendapatan3 = round_up((clust3['pendapatan'].value_counts().max() / ukuran_data3) * 100, 2)
        gender4 = clust4['gender'].value_counts().idxmax()
        persen_gender4 = round_up((clust4['gender'].value_counts().max() / ukuran_data4) * 100, 2)
        jumlah_segmen4 = clust4['Segmen'].value_counts().max()
        umur4 = clust4['umur'].value_counts().idxmax()
        persen_umur4 = round_up((clust4['umur'].value_counts().max() / ukuran_data4) * 100, 2)
        pekerjaan4 = clust4['pekerjaan'].value_counts().idxmax()
        persen_pekerjaan4 = round_up((clust4['pekerjaan'].value_counts().max() / ukuran_data4) * 100, 2)
        status4 = clust4['status'].value_counts().idxmax()
        persen_status4 = round_up((clust4['status'].value_counts().max() / ukuran_data4) * 100, 2)
        pendapatan4 = clust4['pendapatan'].value_counts().idxmax()
        persen_pendapatan4 = round_up((clust4['pendapatan'].value_counts().max() / ukuran_data4) * 100, 2)
        if request.user.last_name == 'Umum' or request.user.last_name == 'Fashion':
            sumber_informasi_mengenai_produk0 = clust0['sumber_informasi_mengenai_produk'].value_counts().idxmax()
            persen_sumber_informasi_mengenai_produk0 = round_up((clust0[
                                                            'sumber_informasi_mengenai_produk'].value_counts().max() / ukuran_data0) * 100,2)
            frekuensi_pembelian_produk_per_tahun0 = clust0[
                'frekuensi_pembelian_produk_per_tahun'].value_counts().idxmax()
            persen_frekuensi_pembelian_produk_per_tahun0 = round_up((clust0[
                                                                'frekuensi_pembelian_produk_per_tahun'].value_counts().max() / ukuran_data0) * 100,2)
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian0 = clust0[
                'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().idxmax()
            persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian0 = round_up((clust0[
                                                                               'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().max() / ukuran_data0) * 100,2)
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk0 = clust0[
                'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().idxmax()
            persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk0 = round_up((clust0[
                                                                                         'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().max() / ukuran_data0) * 100,2)
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik0 = clust0[
                'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().idxmax()
            persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik0 = round_up((clust0[
                                                                                      'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().max() / ukuran_data0) * 100,2)
            bentuk_iklan_yang_paling_menarik0 = clust0['bentuk_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_bentuk_iklan_yang_paling_menarik0 = round_up((clust0[
                                                            'bentuk_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data0) * 100,2)
            konten_iklan_yang_paling_menarik0 = clust0['konten_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_konten_iklan_yang_paling_menarik0 = round_up((clust0[
                                                            'konten_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data0) * 100,2)
            sumber_informasi_mengenai_produk1 = clust1['sumber_informasi_mengenai_produk'].value_counts().idxmax()
            persen_sumber_informasi_mengenai_produk1 = round_up((clust1[
                                                            'sumber_informasi_mengenai_produk'].value_counts().max() / ukuran_data1) * 100,2)
            frekuensi_pembelian_produk_per_tahun1 = clust1[
                'frekuensi_pembelian_produk_per_tahun'].value_counts().idxmax()
            persen_frekuensi_pembelian_produk_per_tahun1 = round_up((clust1[
                                                                'frekuensi_pembelian_produk_per_tahun'].value_counts().max() / ukuran_data1) * 100,2)
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian1 = clust1[
                'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().idxmax()
            persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian1 = round_up((clust1[
                                                                               'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().max() / ukuran_data1) * 100,2)
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk1 = clust1[
                'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().idxmax()
            persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk1 = round_up((clust1[
                                                                                         'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().max() / ukuran_data1) * 100,2)
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik1 = clust1[
                'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().idxmax()
            persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik1 = round_up((clust1[
                                                                                      'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().max() / ukuran_data1) * 100,2)
            bentuk_iklan_yang_paling_menarik1 = clust1['bentuk_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_bentuk_iklan_yang_paling_menarik1 = round_up((clust1[
                                                            'bentuk_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data1) * 100,2)
            konten_iklan_yang_paling_menarik1 = clust1['konten_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_konten_iklan_yang_paling_menarik1 = round_up((clust1[
                                                            'konten_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data1) * 100,2)
            sumber_informasi_mengenai_produk2 = clust2['sumber_informasi_mengenai_produk'].value_counts().idxmax()
            persen_sumber_informasi_mengenai_produk2 = round_up((clust2[
                                                            'sumber_informasi_mengenai_produk'].value_counts().max() / ukuran_data2) * 100,2)
            frekuensi_pembelian_produk_per_tahun2 = clust2[
                'frekuensi_pembelian_produk_per_tahun'].value_counts().idxmax()
            persen_frekuensi_pembelian_produk_per_tahun2 = round_up((clust2[
                                                                'frekuensi_pembelian_produk_per_tahun'].value_counts().max() / ukuran_data2) * 100,2)
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian2 = clust2[
                'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().idxmax()
            persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian2 = round_up((clust2[
                                                                               'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().max() / ukuran_data2) * 100,2)
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk2 = clust2[
                'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().idxmax()
            persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk2 = round_up((clust2[
                                                                                         'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().max() / ukuran_data2) * 100,2)
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik2 = clust2[
                'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().idxmax()
            persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik2 = round_up((clust2[
                                                                                      'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().max() / ukuran_data2) * 100,2)
            bentuk_iklan_yang_paling_menarik2 = clust2['bentuk_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_bentuk_iklan_yang_paling_menarik2 = round_up((clust2[
                                                            'bentuk_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data2) * 100,2)
            konten_iklan_yang_paling_menarik2 = clust2['konten_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_konten_iklan_yang_paling_menarik2 = round_up((clust2[
                                                            'konten_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data2) * 100,2)
            sumber_informasi_mengenai_produk3 = clust3['sumber_informasi_mengenai_produk'].value_counts().idxmax()
            persen_sumber_informasi_mengenai_produk3 = round_up((clust3[
                                                                     'sumber_informasi_mengenai_produk'].value_counts().max() / ukuran_data3) * 100,
                                                                2)
            frekuensi_pembelian_produk_per_tahun3 = clust3[
                'frekuensi_pembelian_produk_per_tahun'].value_counts().idxmax()
            persen_frekuensi_pembelian_produk_per_tahun3 = round_up((clust3[
                                                                         'frekuensi_pembelian_produk_per_tahun'].value_counts().max() / ukuran_data3) * 100,
                                                                    2)
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian3 = clust3[
                'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().idxmax()
            persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian3 = round_up((clust3[
                                                                                        'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().max() / ukuran_data3) * 100,
                                                                                   2)
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk3 = clust3[
                'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().idxmax()
            persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk3 = round_up((clust3[
                                                                                                  'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().max() / ukuran_data3) * 100,
                                                                                             2)
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik3 = clust3[
                'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().idxmax()
            persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik3 = round_up((clust3[
                                                                                               'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().max() / ukuran_data3) * 100,
                                                                                          2)
            bentuk_iklan_yang_paling_menarik3 = clust3['bentuk_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_bentuk_iklan_yang_paling_menarik3 = round_up((clust3[
                                                                     'bentuk_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data3) * 100,
                                                                2)
            konten_iklan_yang_paling_menarik3 = clust3['konten_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_konten_iklan_yang_paling_menarik3 = round_up((clust3[
                                                                     'konten_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data3) * 100,
                                                                2)
            sumber_informasi_mengenai_produk4 = clust4['sumber_informasi_mengenai_produk'].value_counts().idxmax()
            persen_sumber_informasi_mengenai_produk4 = round_up((clust4[
                                                                     'sumber_informasi_mengenai_produk'].value_counts().max() / ukuran_data4) * 100,
                                                                2)
            frekuensi_pembelian_produk_per_tahun4 = clust4[
                'frekuensi_pembelian_produk_per_tahun'].value_counts().idxmax()
            persen_frekuensi_pembelian_produk_per_tahun4 = round_up((clust4[
                                                                         'frekuensi_pembelian_produk_per_tahun'].value_counts().max() / ukuran_data4) * 100,
                                                                    2)
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian4 = clust4[
                'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().idxmax()
            persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian4 = round_up((clust4[
                                                                                        'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().max() / ukuran_data4) * 100,
                                                                                   2)
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk4 = clust4[
                'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().idxmax()
            persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk4 = round_up((clust4[
                                                                                                  'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().max() / ukuran_data4) * 100,
                                                                                             2)
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik4 = clust4[
                'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().idxmax()
            persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik4 = round_up((clust4[
                                                                                               'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().max() / ukuran_data4) * 100,
                                                                                          2)
            bentuk_iklan_yang_paling_menarik4 = clust4['bentuk_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_bentuk_iklan_yang_paling_menarik4 = round_up((clust4[
                                                                     'bentuk_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data4) * 100,
                                                                2)
            konten_iklan_yang_paling_menarik4 = clust4['konten_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_konten_iklan_yang_paling_menarik4 = round_up((clust4[
                                                                     'konten_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data4) * 100,
                                                                2)

        segmen0=clust0['Segmen'].value_counts().idxmax()
        segmen1 = clust1['Segmen'].value_counts().idxmax()
        segmen2 = clust2['Segmen'].value_counts().idxmax()
        segmen3 = clust3['Segmen'].value_counts().idxmax()
        segmen4 = clust4['Segmen'].value_counts().idxmax()


        persen_gender = pd.DataFrame(np.hstack([persen_gender0, persen_gender1, persen_gender2, persen_gender3, persen_gender4]))
        persen_umur = pd.DataFrame(np.hstack([persen_umur0, persen_umur1, persen_umur2, persen_umur3, persen_umur4]))
        persen_pekerjaan = pd.DataFrame(np.hstack([persen_pekerjaan0, persen_pekerjaan1, persen_pekerjaan2, persen_pekerjaan3, persen_pekerjaan4]))
        persen_status = pd.DataFrame(np.hstack([persen_status0, persen_status1, persen_status2, persen_status3, persen_status4]))
        persen_pendapatan = pd.DataFrame(np.hstack([persen_pendapatan0, persen_pendapatan1, persen_pendapatan2, persen_pendapatan3, persen_pendapatan4]))
        gender = pd.DataFrame(np.hstack([gender0, gender1, gender2, gender3, gender4]))
        jumlah_segmen=pd.DataFrame(np.hstack([jumlah_segmen0,jumlah_segmen1,jumlah_segmen2,jumlah_segmen3,jumlah_segmen4]))
        umur = pd.DataFrame(np.hstack([umur0, umur1, umur2, umur3, umur4]))
        pekerjaan = pd.DataFrame(np.hstack([pekerjaan0, pekerjaan1, pekerjaan2, pekerjaan3, pekerjaan4]))
        status = pd.DataFrame(np.hstack([status0, status1, status2, status3, status4]))
        pendapatan = pd.DataFrame(np.hstack([pendapatan0, pendapatan1, pendapatan2, pendapatan3, pendapatan4]))
        if request.user.last_name == 'Umum' or request.user.last_name == 'Fashion':
            sumber_informasi_mengenai_produk = pd.DataFrame(
                np.hstack([sumber_informasi_mengenai_produk0, sumber_informasi_mengenai_produk1, sumber_informasi_mengenai_produk2, sumber_informasi_mengenai_produk3, sumber_informasi_mengenai_produk4]))
            persen_sumber_informasi_mengenai_produk = pd.DataFrame(
                np.hstack([persen_sumber_informasi_mengenai_produk0, persen_sumber_informasi_mengenai_produk1, persen_sumber_informasi_mengenai_produk2, persen_sumber_informasi_mengenai_produk3, persen_sumber_informasi_mengenai_produk4]))
            frekuensi_pembelian_produk_per_tahun = pd.DataFrame(
                np.hstack([frekuensi_pembelian_produk_per_tahun0, frekuensi_pembelian_produk_per_tahun1, frekuensi_pembelian_produk_per_tahun2, frekuensi_pembelian_produk_per_tahun3, frekuensi_pembelian_produk_per_tahun4]))
            persen_frekuensi_pembelian_produk_per_tahun = pd.DataFrame(
                np.hstack(
                    [persen_frekuensi_pembelian_produk_per_tahun0, persen_frekuensi_pembelian_produk_per_tahun1, persen_frekuensi_pembelian_produk_per_tahun2, persen_frekuensi_pembelian_produk_per_tahun3, persen_frekuensi_pembelian_produk_per_tahun4]))
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian = pd.DataFrame(np.hstack(
                [jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian0,
                 jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian1,
                 jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian2,
                 jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian3,
                 jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian4]))
            persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian = pd.DataFrame(
                np.hstack([persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian0,
                           persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian1,
                           persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian2,
                           persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian3,
                           persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian4]))
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk = pd.DataFrame(np.hstack(
                [strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk0,
                 strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk1,
                 strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk2,
                 strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk3,
                 strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk4]))
            persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk = pd.DataFrame(
                np.hstack([persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk0,
                           persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk1,
                           persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk2,
                           persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk3,
                           persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk4]))
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik = pd.DataFrame(np.hstack(
                [tempat_penayangan_iklan_atau_placement_yang_paling_menarik0,
                 tempat_penayangan_iklan_atau_placement_yang_paling_menarik1,
                 tempat_penayangan_iklan_atau_placement_yang_paling_menarik2,
                 tempat_penayangan_iklan_atau_placement_yang_paling_menarik3,
                 tempat_penayangan_iklan_atau_placement_yang_paling_menarik4]))
            persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik = pd.DataFrame(
                np.hstack([persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik0,
                           persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik1,
                           persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik2,
                           persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik3,
                           persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik4]))
            bentuk_iklan_yang_paling_menarik = pd.DataFrame(
                np.hstack([bentuk_iklan_yang_paling_menarik0, bentuk_iklan_yang_paling_menarik1, bentuk_iklan_yang_paling_menarik2, bentuk_iklan_yang_paling_menarik3, bentuk_iklan_yang_paling_menarik4]))
            persen_bentuk_iklan_yang_paling_menarik = pd.DataFrame(
                np.hstack([persen_bentuk_iklan_yang_paling_menarik0, persen_bentuk_iklan_yang_paling_menarik1, persen_bentuk_iklan_yang_paling_menarik2, persen_bentuk_iklan_yang_paling_menarik3, persen_bentuk_iklan_yang_paling_menarik4]))
            konten_iklan_yang_paling_menarik = pd.DataFrame(
                np.hstack([konten_iklan_yang_paling_menarik0, konten_iklan_yang_paling_menarik1, konten_iklan_yang_paling_menarik2, konten_iklan_yang_paling_menarik3, konten_iklan_yang_paling_menarik4]))
            persen_konten_iklan_yang_paling_menarik = pd.DataFrame(
                np.hstack([persen_konten_iklan_yang_paling_menarik0, persen_konten_iklan_yang_paling_menarik1, persen_konten_iklan_yang_paling_menarik2, persen_konten_iklan_yang_paling_menarik3, persen_konten_iklan_yang_paling_menarik4]))
        segmen = pd.DataFrame(np.hstack([segmen0, segmen1, segmen2, segmen3, segmen4]))

        if request.user.last_name == 'Umum' or request.user.last_name == 'Fashion':
            data_new = pd.concat(
                [gender, persen_gender, jumlah_segmen, umur, persen_umur, pekerjaan, persen_pekerjaan,
                 status, persen_status, pendapatan, persen_pendapatan, sumber_informasi_mengenai_produk,
                 persen_sumber_informasi_mengenai_produk,
                 frekuensi_pembelian_produk_per_tahun, persen_frekuensi_pembelian_produk_per_tahun,
                 jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian,
                 persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian,
                 strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk,
                 persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk,
                 tempat_penayangan_iklan_atau_placement_yang_paling_menarik,
                 persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik,
                 bentuk_iklan_yang_paling_menarik, persen_bentuk_iklan_yang_paling_menarik,
                 konten_iklan_yang_paling_menarik, persen_konten_iklan_yang_paling_menarik, segmen], axis=1)
        elif request.user.last_name == 'Makanan - restoran & pesan antar' or request.user.last_name == 'Makanan - saji di tempat saja' or request.user.last_name == 'Makanan - layan antar saja' or request.user.last_name == 'Makanan - penyedia saja (layan antar oleh Gojek/Grab)':
            data_new = pd.concat(
                [gender, persen_gender, jumlah_segmen, umur, persen_umur, pekerjaan, persen_pekerjaan,
                 status, persen_status, pendapatan, persen_pendapatan, segmen], axis=1)
        print(data_column)
        print(data_new)
        data_new.columns=data_column
    elif n_cluster==6:
        data=data.drop(['responden_name'],axis=1)
        clust0=data[data['Segmen']==0]
        ukuran_data0 = clust0.shape[0]
        clust1=data[data['Segmen']==1]
        ukuran_data1 = clust1.shape[0]
        clust2=data[data['Segmen']==2]
        ukuran_data2 = clust2.shape[0]
        clust3=data[data['Segmen']==3]
        ukuran_data3 = clust3.shape[0]
        clust4=data[data['Segmen']==4]
        ukuran_data4 = clust4.shape[0]
        clust5=data[data['Segmen']==5]
        ukuran_data5 = clust5.shape[0]
        gender0=clust0['gender'].value_counts().idxmax()
        persen_gender0 = round_up((clust0['gender'].value_counts().max()/ ukuran_data0) * 100,2)
        jumlah_segmen0 = clust0['Segmen'].value_counts().max()
        umur0=clust0['umur'].value_counts().idxmax()
        persen_umur0 = round_up((clust0['umur'].value_counts().max()/ ukuran_data0) * 100,2)
        pekerjaan0=clust0['pekerjaan'].value_counts().idxmax()
        persen_pekerjaan0 = round_up((clust0['pekerjaan'].value_counts().max()/ ukuran_data0) * 100,2)
        status0=clust0['status'].value_counts().idxmax()
        persen_status0 = round_up((clust0['status'].value_counts().max()/ ukuran_data0) * 100,2)
        pendapatan0=clust0['pendapatan'].value_counts().idxmax()
        persen_pendapatan0 = round_up((clust0['pendapatan'].value_counts().max()/ ukuran_data0) * 100,2)
        gender1 = clust1['gender'].value_counts().idxmax()
        persen_gender1 = round_up((clust1['gender'].value_counts().max()/ ukuran_data1) * 100,2)
        jumlah_segmen1 = clust1['Segmen'].value_counts().max()
        umur1 = clust1['umur'].value_counts().idxmax()
        persen_umur1 = round_up((clust1['umur'].value_counts().max()/ ukuran_data1) * 100,2)
        pekerjaan1 = clust1['pekerjaan'].value_counts().idxmax()
        persen_pekerjaan1 = round_up((clust1['pekerjaan'].value_counts().max()/ ukuran_data1) * 100,2)
        status1 = clust1['status'].value_counts().idxmax()
        persen_status1 = round_up((clust1['status'].value_counts().max()/ ukuran_data1) * 100,2)
        pendapatan1 = clust1['pendapatan'].value_counts().idxmax()
        persen_pendapatan1 = round_up((clust1['pendapatan'].value_counts().max()/ ukuran_data1) * 100,2)
        gender2 = clust2['gender'].value_counts().idxmax()
        persen_gender2 = round_up((clust2['gender'].value_counts().max()/ ukuran_data2) * 100,2)
        jumlah_segmen2 = clust2['Segmen'].value_counts().max()
        umur2 = clust2['umur'].value_counts().idxmax()
        persen_umur2 = round_up((clust2['umur'].value_counts().max()/ ukuran_data2) * 100,2)
        pekerjaan2 = clust2['pekerjaan'].value_counts().idxmax()
        persen_pekerjaan2 = round_up((clust2['pekerjaan'].value_counts().max()/ ukuran_data2) * 100,2)
        status2 = clust2['status'].value_counts().idxmax()
        persen_status2 = round_up((clust2['status'].value_counts().max()/ ukuran_data2) * 100,2)
        pendapatan2 = clust2['pendapatan'].value_counts().idxmax()
        persen_pendapatan2 = round_up((clust2['pendapatan'].value_counts().max()/ ukuran_data2) * 100,2)
        gender3 = clust3['gender'].value_counts().idxmax()
        persen_gender3 = round_up((clust3['gender'].value_counts().max() / ukuran_data3) * 100, 2)
        jumlah_segmen3 = clust3['Segmen'].value_counts().max()
        umur3 = clust3['umur'].value_counts().idxmax()
        persen_umur3 = round_up((clust3['umur'].value_counts().max() / ukuran_data3) * 100, 2)
        pekerjaan3 = clust3['pekerjaan'].value_counts().idxmax()
        persen_pekerjaan3 = round_up((clust3['pekerjaan'].value_counts().max() / ukuran_data3) * 100, 2)
        status3 = clust3['status'].value_counts().idxmax()
        persen_status3 = round_up((clust3['status'].value_counts().max() / ukuran_data3) * 100, 2)
        pendapatan3 = clust3['pendapatan'].value_counts().idxmax()
        persen_pendapatan3 = round_up((clust3['pendapatan'].value_counts().max() / ukuran_data3) * 100, 2)
        gender4 = clust4['gender'].value_counts().idxmax()
        persen_gender4 = round_up((clust4['gender'].value_counts().max() / ukuran_data4) * 100, 2)
        jumlah_segmen4 = clust4['Segmen'].value_counts().max()
        umur4 = clust4['umur'].value_counts().idxmax()
        persen_umur4 = round_up((clust4['umur'].value_counts().max() / ukuran_data4) * 100, 2)
        pekerjaan4 = clust4['pekerjaan'].value_counts().idxmax()
        persen_pekerjaan4 = round_up((clust4['pekerjaan'].value_counts().max() / ukuran_data4) * 100, 2)
        status4 = clust4['status'].value_counts().idxmax()
        persen_status4 = round_up((clust4['status'].value_counts().max() / ukuran_data4) * 100, 2)
        pendapatan4 = clust4['pendapatan'].value_counts().idxmax()
        persen_pendapatan4 = round_up((clust4['pendapatan'].value_counts().max() / ukuran_data4) * 100, 2)
        gender5 = clust5['gender'].value_counts().idxmax()
        persen_gender5 = round_up((clust5['gender'].value_counts().max() / ukuran_data5) * 100, 2)
        jumlah_segmen5 = clust5['Segmen'].value_counts().max()
        umur5 = clust5['umur'].value_counts().idxmax()
        persen_umur5 = round_up((clust5['umur'].value_counts().max() / ukuran_data5) * 100, 2)
        pekerjaan5 = clust5['pekerjaan'].value_counts().idxmax()
        persen_pekerjaan5 = round_up((clust5['pekerjaan'].value_counts().max() / ukuran_data5) * 100, 2)
        status5 = clust5['status'].value_counts().idxmax()
        persen_status5 = round_up((clust5['status'].value_counts().max() / ukuran_data5) * 100, 2)
        pendapatan5 = clust5['pendapatan'].value_counts().idxmax()
        persen_pendapatan5 = round_up((clust5['pendapatan'].value_counts().max() / ukuran_data5) * 100, 2)
        if request.user.last_name == 'Umum' or request.user.last_name == 'Fashion':
            sumber_informasi_mengenai_produk0 = clust0['sumber_informasi_mengenai_produk'].value_counts().idxmax()
            persen_sumber_informasi_mengenai_produk0 = round_up((clust0[
                                                            'sumber_informasi_mengenai_produk'].value_counts().max() / ukuran_data0) * 100,2)
            frekuensi_pembelian_produk_per_tahun0 = clust0[
                'frekuensi_pembelian_produk_per_tahun'].value_counts().idxmax()
            persen_frekuensi_pembelian_produk_per_tahun0 = round_up((clust0[
                                                                'frekuensi_pembelian_produk_per_tahun'].value_counts().max() / ukuran_data0) * 100,2)
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian0 = clust0[
                'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().idxmax()
            persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian0 = round_up((clust0[
                                                                               'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().max() / ukuran_data0) * 100,2)
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk0 = clust0[
                'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().idxmax()
            persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk0 = round_up((clust0[
                                                                                         'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().max() / ukuran_data0) * 100,2)
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik0 = clust0[
                'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().idxmax()
            persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik0 = round_up((clust0[
                                                                                      'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().max() / ukuran_data0) * 100,2)
            bentuk_iklan_yang_paling_menarik0 = clust0['bentuk_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_bentuk_iklan_yang_paling_menarik0 = round_up((clust0[
                                                            'bentuk_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data0) * 100,2)
            konten_iklan_yang_paling_menarik0 = clust0['konten_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_konten_iklan_yang_paling_menarik0 = round_up((clust0[
                                                            'konten_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data0) * 100,2)
            sumber_informasi_mengenai_produk1 = clust1['sumber_informasi_mengenai_produk'].value_counts().idxmax()
            persen_sumber_informasi_mengenai_produk1 = round_up((clust1[
                                                            'sumber_informasi_mengenai_produk'].value_counts().max() / ukuran_data1) * 100,2)
            frekuensi_pembelian_produk_per_tahun1 = clust1[
                'frekuensi_pembelian_produk_per_tahun'].value_counts().idxmax()
            persen_frekuensi_pembelian_produk_per_tahun1 = round_up((clust1[
                                                                'frekuensi_pembelian_produk_per_tahun'].value_counts().max() / ukuran_data1) * 100,2)
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian1 = clust1[
                'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().idxmax()
            persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian1 = round_up((clust1[
                                                                               'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().max() / ukuran_data1) * 100,2)
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk1 = clust1[
                'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().idxmax()
            persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk1 = round_up((clust1[
                                                                                         'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().max() / ukuran_data1) * 100,2)
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik1 = clust1[
                'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().idxmax()
            persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik1 = round_up((clust1[
                                                                                      'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().max() / ukuran_data1) * 100,2)
            bentuk_iklan_yang_paling_menarik1 = clust1['bentuk_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_bentuk_iklan_yang_paling_menarik1 = round_up((clust1[
                                                            'bentuk_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data1) * 100,2)
            konten_iklan_yang_paling_menarik1 = clust1['konten_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_konten_iklan_yang_paling_menarik1 = round_up((clust1[
                                                            'konten_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data1) * 100,2)
            sumber_informasi_mengenai_produk2 = clust2['sumber_informasi_mengenai_produk'].value_counts().idxmax()
            persen_sumber_informasi_mengenai_produk2 = round_up((clust2[
                                                            'sumber_informasi_mengenai_produk'].value_counts().max() / ukuran_data2) * 100,2)
            frekuensi_pembelian_produk_per_tahun2 = clust2[
                'frekuensi_pembelian_produk_per_tahun'].value_counts().idxmax()
            persen_frekuensi_pembelian_produk_per_tahun2 = round_up((clust2[
                                                                'frekuensi_pembelian_produk_per_tahun'].value_counts().max() / ukuran_data2) * 100,2)
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian2 = clust2[
                'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().idxmax()
            persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian2 = round_up((clust2[
                                                                               'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().max() / ukuran_data2) * 100,2)
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk2 = clust2[
                'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().idxmax()
            persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk2 = round_up((clust2[
                                                                                         'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().max() / ukuran_data2) * 100,2)
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik2 = clust2[
                'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().idxmax()
            persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik2 = round_up((clust2[
                                                                                      'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().max() / ukuran_data2) * 100,2)
            bentuk_iklan_yang_paling_menarik2 = clust2['bentuk_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_bentuk_iklan_yang_paling_menarik2 = round_up((clust2[
                                                            'bentuk_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data2) * 100,2)
            konten_iklan_yang_paling_menarik2 = clust2['konten_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_konten_iklan_yang_paling_menarik2 = round_up((clust2[
                                                            'konten_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data2) * 100,2)
            sumber_informasi_mengenai_produk3 = clust3['sumber_informasi_mengenai_produk'].value_counts().idxmax()
            persen_sumber_informasi_mengenai_produk3 = round_up((clust3[
                                                                     'sumber_informasi_mengenai_produk'].value_counts().max() / ukuran_data3) * 100,
                                                                2)
            frekuensi_pembelian_produk_per_tahun3 = clust3[
                'frekuensi_pembelian_produk_per_tahun'].value_counts().idxmax()
            persen_frekuensi_pembelian_produk_per_tahun3 = round_up((clust3[
                                                                         'frekuensi_pembelian_produk_per_tahun'].value_counts().max() / ukuran_data3) * 100,
                                                                    2)
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian3 = clust3[
                'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().idxmax()
            persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian3 = round_up((clust3[
                                                                                        'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().max() / ukuran_data3) * 100,
                                                                                   2)
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk3 = clust3[
                'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().idxmax()
            persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk3 = round_up((clust3[
                                                                                                  'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().max() / ukuran_data3) * 100,
                                                                                             2)
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik3 = clust3[
                'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().idxmax()
            persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik3 = round_up((clust3[
                                                                                               'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().max() / ukuran_data3) * 100,
                                                                                          2)
            bentuk_iklan_yang_paling_menarik3 = clust3['bentuk_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_bentuk_iklan_yang_paling_menarik3 = round_up((clust3[
                                                                     'bentuk_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data3) * 100,
                                                                2)
            konten_iklan_yang_paling_menarik3 = clust3['konten_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_konten_iklan_yang_paling_menarik3 = round_up((clust3[
                                                                     'konten_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data3) * 100,
                                                                2)
            sumber_informasi_mengenai_produk5 = clust5['sumber_informasi_mengenai_produk'].value_counts().idxmax()
            persen_sumber_informasi_mengenai_produk5 = round_up((clust5[
                                                                     'sumber_informasi_mengenai_produk'].value_counts().max() / ukuran_data5) * 100,
                                                                2)
            frekuensi_pembelian_produk_per_tahun5 = clust5[
                'frekuensi_pembelian_produk_per_tahun'].value_counts().idxmax()
            persen_frekuensi_pembelian_produk_per_tahun5 = round_up((clust5[
                                                                         'frekuensi_pembelian_produk_per_tahun'].value_counts().max() / ukuran_data5) * 100,
                                                                    2)
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian5 = clust5[
                'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().idxmax()
            persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian5 = round_up((clust5[
                                                                                        'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().max() / ukuran_data5) * 100,
                                                                                   2)
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk5 = clust5[
                'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().idxmax()
            persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk5 = round_up((clust5[
                                                                                                  'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().max() / ukuran_data5) * 100,
                                                                                             2)
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik5 = clust5[
                'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().idxmax()
            persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik5 = round_up((clust5[
                                                                                               'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().max() / ukuran_data5) * 100,
                                                                                          2)
            bentuk_iklan_yang_paling_menarik5 = clust5['bentuk_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_bentuk_iklan_yang_paling_menarik5 = round_up((clust5[
                                                                     'bentuk_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data5) * 100,
                                                                2)
            konten_iklan_yang_paling_menarik5 = clust5['konten_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_konten_iklan_yang_paling_menarik5 = round_up((clust5[
                                                                     'konten_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data5) * 100,
                                                                2)
            sumber_informasi_mengenai_produk5 = clust5['sumber_informasi_mengenai_produk'].value_counts().idxmax()
            persen_sumber_informasi_mengenai_produk5 = round_up((clust5[
                                                                     'sumber_informasi_mengenai_produk'].value_counts().max() / ukuran_data5) * 100,
                                                                2)
            frekuensi_pembelian_produk_per_tahun5 = clust5[
                'frekuensi_pembelian_produk_per_tahun'].value_counts().idxmax()
            persen_frekuensi_pembelian_produk_per_tahun5 = round_up((clust5[
                                                                         'frekuensi_pembelian_produk_per_tahun'].value_counts().max() / ukuran_data5) * 100,
                                                                    2)
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian5 = clust5[
                'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().idxmax()
            persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian5 = round_up((clust5[
                                                                                        'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'].value_counts().max() / ukuran_data5) * 100,
                                                                                   2)
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk5 = clust5[
                'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().idxmax()
            persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk5 = round_up((clust5[
                                                                                                  'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'].value_counts().max() / ukuran_data5) * 100,
                                                                                             2)
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik5 = clust5[
                'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().idxmax()
            persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik5 = round_up((clust5[
                                                                                               'tempat_penayangan_iklan_atau_placement_yang_paling_menarik'].value_counts().max() / ukuran_data5) * 100,
                                                                                          2)
            bentuk_iklan_yang_paling_menarik5 = clust5['bentuk_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_bentuk_iklan_yang_paling_menarik5 = round_up((clust5[
                                                                     'bentuk_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data5) * 100,
                                                                2)
            konten_iklan_yang_paling_menarik5 = clust5['konten_iklan_yang_paling_menarik'].value_counts().idxmax()
            persen_konten_iklan_yang_paling_menarik5 = round_up((clust5[
                                                                     'konten_iklan_yang_paling_menarik'].value_counts().max() / ukuran_data5) * 100,
                                                                2)
        segmen0=clust0['Segmen'].value_counts().idxmax()
        segmen1 = clust1['Segmen'].value_counts().idxmax()
        segmen2 = clust2['Segmen'].value_counts().idxmax()
        segmen3 = clust3['Segmen'].value_counts().idxmax()
        segmen4 = clust4['Segmen'].value_counts().idxmax()
        segmen5 = clust5['Segmen'].value_counts().idxmax()


        persen_gender = pd.DataFrame(np.hstack([persen_gender0, persen_gender1, persen_gender2, persen_gender3, persen_gender4, persen_gender5]))
        persen_umur = pd.DataFrame(np.hstack([persen_umur0, persen_umur1, persen_umur2, persen_umur3, persen_umur4, persen_umur5]))
        persen_pekerjaan = pd.DataFrame(np.hstack([persen_pekerjaan0, persen_pekerjaan1, persen_pekerjaan2, persen_pekerjaan3, persen_pekerjaan4, persen_pekerjaan5]))
        persen_status = pd.DataFrame(np.hstack([persen_status0, persen_status1, persen_status2, persen_status3, persen_status4, persen_status5]))
        persen_pendapatan = pd.DataFrame(np.hstack([persen_pendapatan0, persen_pendapatan1, persen_pendapatan2, persen_pendapatan3, persen_pendapatan4, persen_pendapatan5]))
        gender = pd.DataFrame(np.hstack([gender0, gender1, gender2, gender3, gender4, gender5]))
        jumlah_segmen=pd.DataFrame(np.hstack([jumlah_segmen0,jumlah_segmen1,jumlah_segmen2,jumlah_segmen3,jumlah_segmen4,jumlah_segmen5]))
        umur = pd.DataFrame(np.hstack([umur0, umur1, umur2, umur3, umur4, umur5]))
        pekerjaan = pd.DataFrame(np.hstack([pekerjaan0, pekerjaan1, pekerjaan2, pekerjaan3, pekerjaan4, pekerjaan5]))
        status = pd.DataFrame(np.hstack([status0, status1, status2, status3, status4, status5]))
        pendapatan = pd.DataFrame(np.hstack([pendapatan0, pendapatan1, pendapatan2, pendapatan3, pendapatan4, pendapatan5]))
        if request.user.last_name == 'Umum' or request.user.last_name == 'Fashion':
            sumber_informasi_mengenai_produk = pd.DataFrame(
                np.hstack([sumber_informasi_mengenai_produk0, sumber_informasi_mengenai_produk1, sumber_informasi_mengenai_produk2, sumber_informasi_mengenai_produk3, sumber_informasi_mengenai_produk4, sumber_informasi_mengenai_produk5]))
            persen_sumber_informasi_mengenai_produk = pd.DataFrame(
                np.hstack([persen_sumber_informasi_mengenai_produk0, persen_sumber_informasi_mengenai_produk1, persen_sumber_informasi_mengenai_produk2, persen_sumber_informasi_mengenai_produk3, persen_sumber_informasi_mengenai_produk4, persen_sumber_informasi_mengenai_produk5]))
            frekuensi_pembelian_produk_per_tahun = pd.DataFrame(
                np.hstack([frekuensi_pembelian_produk_per_tahun0, frekuensi_pembelian_produk_per_tahun1, frekuensi_pembelian_produk_per_tahun2, frekuensi_pembelian_produk_per_tahun3, frekuensi_pembelian_produk_per_tahun4, frekuensi_pembelian_produk_per_tahun5]))
            persen_frekuensi_pembelian_produk_per_tahun = pd.DataFrame(
                np.hstack(
                    [persen_frekuensi_pembelian_produk_per_tahun0, persen_frekuensi_pembelian_produk_per_tahun1, persen_frekuensi_pembelian_produk_per_tahun2, persen_frekuensi_pembelian_produk_per_tahun3, persen_frekuensi_pembelian_produk_per_tahun4, persen_frekuensi_pembelian_produk_per_tahun5]))
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian = pd.DataFrame(np.hstack(
                [jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian0,
                 jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian1,
                 jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian2,
                 jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian3,
                 jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian4,
                 jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian5]))
            persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian = pd.DataFrame(
                np.hstack([persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian0,
                           persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian1,
                           persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian2,
                           persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian3,
                           persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian4,
                           persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian5]))
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk = pd.DataFrame(np.hstack(
                [strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk0,
                 strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk1,
                 strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk2,
                 strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk3,
                 strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk4,
                 strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk5]))
            persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk = pd.DataFrame(
                np.hstack([persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk0,
                           persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk1,
                           persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk2,
                           persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk3,
                           persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk4,
                           persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk5]))
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik = pd.DataFrame(np.hstack(
                [tempat_penayangan_iklan_atau_placement_yang_paling_menarik0,
                 tempat_penayangan_iklan_atau_placement_yang_paling_menarik1,
                 tempat_penayangan_iklan_atau_placement_yang_paling_menarik2,
                 tempat_penayangan_iklan_atau_placement_yang_paling_menarik3,
                 tempat_penayangan_iklan_atau_placement_yang_paling_menarik4,
                 tempat_penayangan_iklan_atau_placement_yang_paling_menarik5]))
            persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik = pd.DataFrame(
                np.hstack([persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik0,
                           persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik1,
                           persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik2,
                           persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik3,
                           persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik4,
                           persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik5]))
            bentuk_iklan_yang_paling_menarik = pd.DataFrame(
                np.hstack([bentuk_iklan_yang_paling_menarik0, bentuk_iklan_yang_paling_menarik1, bentuk_iklan_yang_paling_menarik2, bentuk_iklan_yang_paling_menarik3, bentuk_iklan_yang_paling_menarik4, bentuk_iklan_yang_paling_menarik5]))
            persen_bentuk_iklan_yang_paling_menarik = pd.DataFrame(
                np.hstack([persen_bentuk_iklan_yang_paling_menarik0, persen_bentuk_iklan_yang_paling_menarik1, persen_bentuk_iklan_yang_paling_menarik2, persen_bentuk_iklan_yang_paling_menarik3, persen_bentuk_iklan_yang_paling_menarik4, persen_bentuk_iklan_yang_paling_menarik5]))
            konten_iklan_yang_paling_menarik = pd.DataFrame(
                np.hstack([konten_iklan_yang_paling_menarik0, konten_iklan_yang_paling_menarik1, konten_iklan_yang_paling_menarik2, konten_iklan_yang_paling_menarik3, konten_iklan_yang_paling_menarik4, konten_iklan_yang_paling_menarik5]))
            persen_konten_iklan_yang_paling_menarik = pd.DataFrame(
                np.hstack([persen_konten_iklan_yang_paling_menarik0, persen_konten_iklan_yang_paling_menarik1, persen_konten_iklan_yang_paling_menarik2, persen_konten_iklan_yang_paling_menarik3, persen_konten_iklan_yang_paling_menarik4, persen_konten_iklan_yang_paling_menarik5]))
        segmen = pd.DataFrame(np.hstack([segmen0, segmen1, segmen2, segmen3, segmen4, segmen5]))

        if request.user.last_name == 'Umum' or request.user.last_name == 'Fashion':
            data_new = pd.concat(
                [gender, persen_gender, jumlah_segmen, umur, persen_umur, pekerjaan, persen_pekerjaan,
                 status, persen_status, pendapatan, persen_pendapatan, sumber_informasi_mengenai_produk,
                 persen_sumber_informasi_mengenai_produk,
                 frekuensi_pembelian_produk_per_tahun, persen_frekuensi_pembelian_produk_per_tahun,
                 jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian,
                 persen_jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian,
                 strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk,
                 persen_strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk,
                 tempat_penayangan_iklan_atau_placement_yang_paling_menarik,
                 persen_tempat_penayangan_iklan_atau_placement_yang_paling_menarik,
                 bentuk_iklan_yang_paling_menarik, persen_bentuk_iklan_yang_paling_menarik,
                 konten_iklan_yang_paling_menarik, persen_konten_iklan_yang_paling_menarik, segmen], axis=1)
        elif request.user.last_name == 'Makanan - restoran & pesan antar' or request.user.last_name == 'Makanan - saji di tempat saja' or request.user.last_name == 'Makanan - layan antar saja' or request.user.last_name == 'Makanan - penyedia saja (layan antar oleh Gojek/Grab)':
            data_new = pd.concat(
                [gender, persen_gender, jumlah_segmen, umur, persen_umur, pekerjaan, persen_pekerjaan,
                 status, persen_status, pendapatan, persen_pendapatan, segmen], axis=1)
        print(data_column)
        print(data_new)
        data_new.columns=data_column
    newsegmen = data_new['Segmen']
    temp=[]
    for i in range(0,len(newsegmen),1):
        if newsegmen[i] >= 0 and newsegmen[i] < 1:
            temp.append(1)
        elif newsegmen[i] >= 1 and newsegmen[i] < 2:
            temp.append(2)
        elif newsegmen[i] >= 2 and newsegmen[i] < 3:
            temp.append(3)
        elif newsegmen[i] >= 3 and newsegmen[i] < 4:
            temp.append(4)
        elif newsegmen[i] >= 4 and newsegmen[i] < 5:
            temp.append(5)
        elif newsegmen[i] >= 5 and newsegmen[i] < 6:
            temp.append(6)
    data_new['segmen_baru'] = pd.DataFrame(temp)
    allData = []
    for i in range(data_new.shape[0]):
        temp = data_new.loc[i]
        allData.append(dict(temp))
    context = {'data': allData}

    if request.user.last_name == 'Umum' or request.user.last_name == 'Fashion':
        return render(request, "rangkuman_umum.html",context)
    elif request.user.last_name == 'Makanan - restoran & pesan antar' or request.user.last_name == 'Makanan - saji di tempat saja' or request.user.last_name == 'Makanan - layan antar saja' or request.user.last_name == 'Makanan - penyedia saja (layan antar oleh Gojek/Grab)':
        return render(request, "rangkuman_makanan.html", context)



def rincian_umum(request):
    try:
        username = request.user.id
        if request.user.last_name == 'Umum':
            obj = buat_survey_umum.objects.all().values()
        elif request.user.last_name == 'Fashion':
            obj = buat_survey_fashion.objects.all().values()
        elif request.user.last_name == 'Makanan - restoran & pesan antar':
            obj = buat_survey_makanan_resto.objects.all().values()
        elif request.user.last_name == 'Makanan - saji di tempat saja':
            obj = buat_survey_makanan_saji.objects.all().values()
        elif request.user.last_name == 'Makanan - layan antar saja':
            obj = buat_survey_makanan_layan_antar.objects.all().values()
        elif request.user.last_name == 'Makanan - penyedia saja (layan antar oleh Gojek/Grab)':
            obj = buat_survey_makanan_penyedia_jasa.objects.all().values()
        data = pd.DataFrame(obj)
        data = data[data['username'] == username]
        if data.shape[0] <= 4:
            messages.error(request, 'Data Tidak Mencukupi, minimal data adalah 12')
            return redirect('/owner')
        data = data.reset_index(drop=True)
        if request.user.last_name == 'Umum' or request.user.last_name == 'Fashion':
            data = data[['responden_name','gender', 'umur', 'pekerjaan', 'status', 'pendapatan', 'sumber_informasi_mengenai_produk',
                         'frekuensi_pembelian_produk_per_tahun', 'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian',
                         'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk',
                         'tempat_penayangan_iklan_atau_placement_yang_paling_menarik', 'bentuk_iklan_yang_paling_menarik',
                         'konten_iklan_yang_paling_menarik', 'Segmen']]
        elif request.user.last_name == 'Makanan - restoran & pesan antar' or request.user.last_name == 'Makanan - saji di tempat saja' or request.user.last_name == 'Makanan - layan antar saja' or request.user.last_name == 'Makanan - penyedia saja (layan antar oleh Gojek/Grab)':
            data = data[['responden_name', 'gender', 'umur', 'pekerjaan', 'status', 'pendapatan', 'Segmen']]
        data = data.sort_values(['Segmen'])
        newsegmen = data['Segmen']
        temp=[]
        for i in range(0,len(newsegmen),1):
            if newsegmen[i] >= 0 and newsegmen[i] < 1:
                temp.append(1)
            elif newsegmen[i] >= 1 and newsegmen[i] < 2:
                temp.append(2)
            elif newsegmen[i] >= 2 and newsegmen[i] < 3:
                temp.append(3)
            elif newsegmen[i] >= 3 and newsegmen[i] < 4:
                temp.append(4)
            elif newsegmen[i] >= 4 and newsegmen[i] < 5:
                temp.append(5)
            elif newsegmen[i] >= 5 and newsegmen[i] < 6:
                temp.append(6)
        data['segmen_baru'] = pd.DataFrame(temp)
        allData=[]
        for i in range(data.shape[0]):
            temp=data.loc[i]
            allData.append(dict(temp))
        context= {'data':allData}
        if request.user.last_name == 'Umum' or request.user.last_name == 'Fashion':
            return render(request, 'rincian_umum.html',context)
        elif request.user.last_name == 'Makanan - restoran & pesan antar' or request.user.last_name == 'Makanan - saji di tempat saja' or request.user.last_name == 'Makanan - layan antar saja' or request.user.last_name == 'Makanan - penyedia saja (layan antar oleh Gojek/Grab)':
            return render(request, 'rincian_makanan.html', context)
    except:
        messages.error(request, 'Data Tidak Mencukupi, minimal data adalah 12')
        return redirect('/owner')

def donesurvey(request):
    if request.method =='POST':
        if request.POST['tipe_bisnis'] == 'Umum':
            username=int(request.POST['id_bisnis'])
            responden_name = request.POST['responden_name']
            umur = request.POST['umur']
            gender = request.POST['gender']
            pekerjaan = request.POST['pekerjaan']
            status = request.POST['status']
            pendapatan = request.POST['pendapatan']
            sumber_informasi_mengenai_produk = request.POST['sumber_informasi_mengenai_produk']
            frekuensi_pembelian_produk_per_tahun = request.POST['frekuensi_pembelian_produk_per_tahun']
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian = request.POST[
                'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian']
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk = request.POST[
                'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk']
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik = request.POST[
                'tempat_penayangan_iklan_atau_placement_yang_paling_menarik']
            bentuk_iklan_yang_paling_menarik = request.POST['bentuk_iklan_yang_paling_menarik']
            konten_iklan_yang_paling_menarik = request.POST['konten_iklan_yang_paling_menarik']
            saya_senang_mengikuti_komunitas_terdiri_dari_banyak_orang = request.POST[
                'saya_senang_mengikuti_komunitas_terdiri_dari_banyak_orang']
            saya_senang_menghabiskan_waktu_bersama_teman_teman = request.POST[
                'saya_senang_menghabiskan_waktu_bersama_teman_teman']
            Saya_senang_terlibat_dalam_sebuah_proyek = request.POST['Saya_senang_terlibat_dalam_sebuah_proyek']
            Saya_senang_merawat_kuku_rambut_dan_berbagai_bagian_tubuh_saya = request.POST[
                'Saya_senang_merawat_kuku_rambut_dan_berbagai_bagian_tubuh_saya']
            Saya_sering_membeli_peralatan_kosmetik = request.POST['Saya_sering_membeli_peralatan_kosmetik']
            Saya_senang_pergi_ke_salon_untuk_melakukan_perawatan_diri = request.POST[
                'Saya_senang_pergi_ke_salon_untuk_melakukan_perawatan_diri']
            Saya_senang_menjelajahi_tempat_baru_saat_berlibur = request.POST[
                'Saya_senang_menjelajahi_tempat_baru_saat_berlibur']
            Saya_mempunyai_keinginan_untuk_dapat_pergi_ke_seluruh_dunia = request.POST[
                'Saya_mempunyai_keinginan_untuk_dapat_pergi_ke_seluruh_dunia']
            Menghabiskan_waktu_berlibur_dengan_travelling = request.POST[
                'Menghabiskan_waktu_berlibur_dengan_travelling']
            Keluarga_merupakan_hal_yang_sangat_penting_bagi_saya = request.POST[
                'Keluarga_merupakan_hal_yang_sangat_penting_bagi_saya']
            Saya_peduli_terhadap_keluarga_saya = request.POST['Saya_peduli_terhadap_keluarga_saya']
            Saya_selalu_ingin_memenuhi_kebutuhan_keluarga_saya = request.POST[
                'Saya_selalu_ingin_memenuhi_kebutuhan_keluarga_saya']
            Saat_waktu_senggang_saya_melakukan_hobi_saya = request.POST['Saat_waktu_senggang_saya_melakukan_hobi_saya']
            Saya_mencari_hiburan_yang_saya_sukai_saat_waktu_senggang = request.POST[
                'Saya_mencari_hiburan_yang_saya_sukai_saat_waktu_senggang']
            Saya_mempunyai_aktivitas_rutin_di_luar_pekerjaan_utama_saya = request.POST[
                'Saya_mempunyai_aktivitas_rutin_di_luar_pekerjaan_utama_saya']

            Survey_Umum = buat_survey_umum(username=username, responden_name=responden_name, gender=gender, umur=umur,
                                           pekerjaan=pekerjaan,
                                           status=status,
                                           pendapatan=pendapatan,
                                           sumber_informasi_mengenai_produk=sumber_informasi_mengenai_produk,
                                           frekuensi_pembelian_produk_per_tahun=frekuensi_pembelian_produk_per_tahun,
                                           jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian=jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian,
                                           strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk=strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk,
                                           tempat_penayangan_iklan_atau_placement_yang_paling_menarik=tempat_penayangan_iklan_atau_placement_yang_paling_menarik,
                                           bentuk_iklan_yang_paling_menarik=bentuk_iklan_yang_paling_menarik,
                                           konten_iklan_yang_paling_menarik=konten_iklan_yang_paling_menarik,
                                           saya_senang_mengikuti_komunitas_terdiri_dari_banyak_orang=saya_senang_mengikuti_komunitas_terdiri_dari_banyak_orang,
                                           saya_senang_menghabiskan_waktu_bersama_teman_teman=saya_senang_menghabiskan_waktu_bersama_teman_teman,
                                           Saya_senang_terlibat_dalam_sebuah_proyek=Saya_senang_terlibat_dalam_sebuah_proyek,
                                           Saya_senang_merawat_kuku_rambut_dan_berbagai_bagian_tubuh_saya=Saya_senang_merawat_kuku_rambut_dan_berbagai_bagian_tubuh_saya,
                                           Saya_sering_membeli_peralatan_kosmetik=Saya_sering_membeli_peralatan_kosmetik,
                                           Saya_senang_pergi_ke_salon_untuk_melakukan_perawatan_diri=Saya_senang_pergi_ke_salon_untuk_melakukan_perawatan_diri,
                                           Saya_senang_menjelajahi_tempat_baru_saat_berlibur=Saya_senang_menjelajahi_tempat_baru_saat_berlibur,
                                           Saya_mempunyai_keinginan_untuk_dapat_pergi_ke_seluruh_dunia=Saya_mempunyai_keinginan_untuk_dapat_pergi_ke_seluruh_dunia,
                                           Menghabiskan_waktu_berlibur_dengan_travelling=Menghabiskan_waktu_berlibur_dengan_travelling,
                                           Keluarga_merupakan_hal_yang_sangat_penting_bagi_saya=Keluarga_merupakan_hal_yang_sangat_penting_bagi_saya,
                                           Saya_peduli_terhadap_keluarga_saya=Saya_peduli_terhadap_keluarga_saya,
                                           Saya_selalu_ingin_memenuhi_kebutuhan_keluarga_saya=Saya_selalu_ingin_memenuhi_kebutuhan_keluarga_saya,
                                           Saat_waktu_senggang_saya_melakukan_hobi_saya=Saat_waktu_senggang_saya_melakukan_hobi_saya,
                                           Saya_mencari_hiburan_yang_saya_sukai_saat_waktu_senggang=Saya_mencari_hiburan_yang_saya_sukai_saat_waktu_senggang,
                                           Saya_mempunyai_aktivitas_rutin_di_luar_pekerjaan_utama_saya=Saya_mempunyai_aktivitas_rutin_di_luar_pekerjaan_utama_saya)
            Survey_Umum.save()
        elif request.POST['tipe_bisnis'] == 'Fashion':
            username=int(request.POST['id_bisnis'])
            responden_name = request.POST['responden_name']
            umur = request.POST['umur']
            gender = request.POST['gender']
            pekerjaan = request.POST['pekerjaan']
            status = request.POST['status']
            pendapatan = request.POST['pendapatan']
            sumber_informasi_mengenai_produk = request.POST['sumber_informasi_mengenai_produk']
            frekuensi_pembelian_produk_per_tahun = request.POST['frekuensi_pembelian_produk_per_tahun']
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian = request.POST[
                'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian']
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk = request.POST[
                'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk']
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik = request.POST[
                'tempat_penayangan_iklan_atau_placement_yang_paling_menarik']
            bentuk_iklan_yang_paling_menarik = request.POST['bentuk_iklan_yang_paling_menarik']
            konten_iklan_yang_paling_menarik = request.POST['konten_iklan_yang_paling_menarik']
            saya_senang_mengikuti_komunitas_terdiri_dari_banyak_orang = request.POST[
                'saya_senang_mengikuti_komunitas_terdiri_dari_banyak_orang']
            saya_senang_menghabiskan_waktu_bersama_teman_teman = request.POST[
                'saya_senang_menghabiskan_waktu_bersama_teman_teman']
            Saya_senang_terlibat_dalam_sebuah_proyek = request.POST['Saya_senang_terlibat_dalam_sebuah_proyek']
            Saya_senang_merawat_kuku_rambut_dan_berbagai_bagian_tubuh_saya = request.POST[
                'Saya_senang_merawat_kuku_rambut_dan_berbagai_bagian_tubuh_saya']
            Saya_sering_membeli_peralatan_kosmetik = request.POST['Saya_sering_membeli_peralatan_kosmetik']
            Saya_senang_pergi_ke_salon_untuk_melakukan_perawatan_diri = request.POST[
                'Saya_senang_pergi_ke_salon_untuk_melakukan_perawatan_diri']
            Saya_senang_menjelajahi_tempat_baru_saat_berlibur = request.POST[
                'Saya_senang_menjelajahi_tempat_baru_saat_berlibur']
            Saya_mempunyai_keinginan_untuk_dapat_pergi_ke_seluruh_dunia = request.POST[
                'Saya_mempunyai_keinginan_untuk_dapat_pergi_ke_seluruh_dunia']
            Menghabiskan_waktu_berlibur_dengan_travelling = request.POST[
                'Menghabiskan_waktu_berlibur_dengan_travelling']
            Keluarga_merupakan_hal_yang_sangat_penting_bagi_saya = request.POST[
                'Keluarga_merupakan_hal_yang_sangat_penting_bagi_saya']
            Saya_peduli_terhadap_keluarga_saya = request.POST['Saya_peduli_terhadap_keluarga_saya']
            Saya_selalu_ingin_memenuhi_kebutuhan_keluarga_saya = request.POST[
                'Saya_selalu_ingin_memenuhi_kebutuhan_keluarga_saya']
            Saat_waktu_senggang_saya_melakukan_hobi_saya = request.POST['Saat_waktu_senggang_saya_melakukan_hobi_saya']
            Saya_mencari_hiburan_yang_saya_sukai_saat_waktu_senggang = request.POST[
                'Saya_mencari_hiburan_yang_saya_sukai_saat_waktu_senggang']
            Saya_mempunyai_aktivitas_rutin_di_luar_pekerjaan_utama_saya = request.POST[
                'Saya_mempunyai_aktivitas_rutin_di_luar_pekerjaan_utama_saya']
            Banyak_orang_yang_mengenal_saya = request.POST['Banyak_orang_yang_mengenal_saya']
            Saya_termasuk_orang_yang_cepat_dalam_mencoba_tren = request.POST[
                'Saya_termasuk_orang_yang_cepat_dalam_mencoba_tren']
            Saya_menghabiskan_banyak_waktu = request.POST['Saya_menghabiskan_banyak_waktu']
            Saya_mencoba_untuk_memilih_model_fesyen_terbaru = request.POST[
                'Saya_mencoba_untuk_memilih_model_fesyen_terbaru']
            Saya_senang_berbelanja_produk_fesyen = request.POST['Saya_senang_berbelanja_produk_fesyen']
            Saya_lebih_percaya_terhadap_produk_fesyen_dengan_merek_terkenal = request.POST[
                'Saya_lebih_percaya_terhadap_produk_fesyen_dengan_merek_terkenal']
            Menurut_saya_merek_terkenal_selalu_mempunyai_kualitas_yang_baik = request.POST[
                'Menurut_saya_merek_terkenal_selalu_mempunyai_kualitas_yang_baik']
            Saya_tetap_membeli_produk_fesyen_dengan_merek_terkenal = request.POST[
                'Saya_tetap_membeli_produk_fesyen_dengan_merek_terkenal']
            Saya_membeli_produk_fesyen_yang_saya_suka = request.POST['Saya_membeli_produk_fesyen_yang_saya_suka']
            Saya_membeli_produk_fesyen_hanya_saat_diskon = request.POST['Saya_membeli_produk_fesyen_hanya_saat_diskon']
            Saat_saya_berbelanja_produk_fesyen_saya_membandingkan = request.POST[
                'Saat_saya_berbelanja_produk_fesyen_saya_membandingkan']

            Survey_Fashion = buat_survey_fashion(username=username, responden_name=responden_name, gender=gender,
                                                 umur=umur,
                                                 pekerjaan=pekerjaan,
                                                 status=status,
                                                 pendapatan=pendapatan,
                                                 sumber_informasi_mengenai_produk=sumber_informasi_mengenai_produk,
                                                 frekuensi_pembelian_produk_per_tahun=frekuensi_pembelian_produk_per_tahun,
                                                 jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian=jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian,
                                                 strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk=strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk,
                                                 tempat_penayangan_iklan_atau_placement_yang_paling_menarik=tempat_penayangan_iklan_atau_placement_yang_paling_menarik,
                                                 bentuk_iklan_yang_paling_menarik=bentuk_iklan_yang_paling_menarik,
                                                 konten_iklan_yang_paling_menarik=konten_iklan_yang_paling_menarik,
                                                 saya_senang_mengikuti_komunitas_terdiri_dari_banyak_orang=saya_senang_mengikuti_komunitas_terdiri_dari_banyak_orang,
                                                 saya_senang_menghabiskan_waktu_bersama_teman_teman=saya_senang_menghabiskan_waktu_bersama_teman_teman,
                                                 Saya_senang_terlibat_dalam_sebuah_proyek=Saya_senang_terlibat_dalam_sebuah_proyek,
                                                 Saya_senang_merawat_kuku_rambut_dan_berbagai_bagian_tubuh_saya=Saya_senang_merawat_kuku_rambut_dan_berbagai_bagian_tubuh_saya,
                                                 Saya_sering_membeli_peralatan_kosmetik=Saya_sering_membeli_peralatan_kosmetik,
                                                 Saya_senang_pergi_ke_salon_untuk_melakukan_perawatan_diri=Saya_senang_pergi_ke_salon_untuk_melakukan_perawatan_diri,
                                                 Saya_senang_menjelajahi_tempat_baru_saat_berlibur=Saya_senang_menjelajahi_tempat_baru_saat_berlibur,
                                                 Saya_mempunyai_keinginan_untuk_dapat_pergi_ke_seluruh_dunia=Saya_mempunyai_keinginan_untuk_dapat_pergi_ke_seluruh_dunia,
                                                 Menghabiskan_waktu_berlibur_dengan_travelling=Menghabiskan_waktu_berlibur_dengan_travelling,
                                                 Keluarga_merupakan_hal_yang_sangat_penting_bagi_saya=Keluarga_merupakan_hal_yang_sangat_penting_bagi_saya,
                                                 Saya_peduli_terhadap_keluarga_saya=Saya_peduli_terhadap_keluarga_saya,
                                                 Saya_selalu_ingin_memenuhi_kebutuhan_keluarga_saya=Saya_selalu_ingin_memenuhi_kebutuhan_keluarga_saya,
                                                 Saat_waktu_senggang_saya_melakukan_hobi_saya=Saat_waktu_senggang_saya_melakukan_hobi_saya,
                                                 Saya_mencari_hiburan_yang_saya_sukai_saat_waktu_senggang=Saya_mencari_hiburan_yang_saya_sukai_saat_waktu_senggang,
                                                 Saya_mempunyai_aktivitas_rutin_di_luar_pekerjaan_utama_saya=Saya_mempunyai_aktivitas_rutin_di_luar_pekerjaan_utama_saya,
                                                 Banyak_orang_yang_mengenal_saya=Banyak_orang_yang_mengenal_saya,
                                                 Saya_termasuk_orang_yang_cepat_dalam_mencoba_tren=Saya_termasuk_orang_yang_cepat_dalam_mencoba_tren,
                                                 Saya_menghabiskan_banyak_waktu=Saya_menghabiskan_banyak_waktu,
                                                 Saya_mencoba_untuk_memilih_model_fesyen_terbaru=Saya_mencoba_untuk_memilih_model_fesyen_terbaru,
                                                 Saya_senang_berbelanja_produk_fesyen=Saya_senang_berbelanja_produk_fesyen,
                                                 Saya_lebih_percaya_terhadap_produk_fesyen_dengan_merek_terkenal=Saya_lebih_percaya_terhadap_produk_fesyen_dengan_merek_terkenal,
                                                 Menurut_saya_merek_terkenal_selalu_mempunyai_kualitas_yang_baik=Menurut_saya_merek_terkenal_selalu_mempunyai_kualitas_yang_baik,
                                                 Saya_tetap_membeli_produk_fesyen_dengan_merek_terkenal=Saya_tetap_membeli_produk_fesyen_dengan_merek_terkenal,
                                                 Saya_membeli_produk_fesyen_yang_saya_suka=Saya_membeli_produk_fesyen_yang_saya_suka,
                                                 Saya_membeli_produk_fesyen_hanya_saat_diskon=Saya_membeli_produk_fesyen_hanya_saat_diskon,
                                                 Saat_saya_berbelanja_produk_fesyen_saya_membandingkan=Saat_saya_berbelanja_produk_fesyen_saya_membandingkan)
            Survey_Fashion.save()
        elif request.POST['tipe_bisnis'] == 'Makanan - restoran & pesan antar':
            username=int(request.POST['id_bisnis'])
            responden_name = request.POST['responden_name']
            umur = request.POST['umur']
            gender = request.POST['gender']
            pekerjaan = request.POST['pekerjaan']
            status = request.POST['status']
            pendapatan = request.POST['pendapatan']
            Seberapa_penting_konsistensi_makanan_yang_disajikan = request.POST[
                'Seberapa_penting_konsistensi_makanan_yang_disajikan']
            Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun = request.POST[
                'Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun']
            Seberapa_penting_kualitas_makanan_yang_tinggi = request.POST[
                'Seberapa_penting_kualitas_makanan_yang_tinggi']
            Seberapa_penting_bahan_makanan_yang_digunakan_segar = request.POST[
                'Seberapa_penting_bahan_makanan_yang_digunakan_segar']
            Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa = request.POST[
                'Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa']
            Seberapa_penting_ketersediaan_menu_makanan_lokal = request.POST[
                'Seberapa_penting_ketersediaan_menu_makanan_lokal']
            Seberapa_penting_ketersediaan_menu_makanan_yang_menarik = request.POST[
                'Seberapa_penting_ketersediaan_menu_makanan_yang_menarik']
            Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi = request.POST[
                'Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi']
            Harga_makanan_yang_wajar = request.POST['Harga_makanan_yang_wajar']
            Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan = request.POST[
                'Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan']
            Terdapat_pilihan_menu_makanan_sehat_di_restoran = request.POST[
                'Terdapat_pilihan_menu_makanan_sehat_di_restoran']
            Makanan_mengandung_gizi_yang_baik = request.POST['Makanan_mengandung_gizi_yang_baik']
            Seberapa_penting_makanan_dimasak_secara_higienis = request.POST[
                'Seberapa_penting_makanan_dimasak_secara_higienis']
            Seberapa_penting_kebersihan_dijaga_dengan_baik_oleh_pelayan = request.POST[
                'Seberapa_penting_kebersihan_dijaga_dengan_baik_oleh_pelayan']
            Seberapa_penting_terdapat_standar_terhadap_pelayanan = request.POST[
                'Seberapa_penting_terdapat_standar_terhadap_pelayanan']
            Seberapa_penting_pelayan_melakukan_pelayanan_secara_cepat = request.POST[
                'Seberapa_penting_pelayan_melakukan_pelayanan_secara_cepat']
            Seberapa_penting_pelayan_perhatian_kepada_kebutuhan_pelanggan = request.POST[
                'Seberapa_penting_pelayan_perhatian_kepada_kebutuhan_pelanggan']
            Seberapa_penting_pelayan_memberikan_bantuan_yang_baik = request.POST[
                'Seberapa_penting_pelayan_memberikan_bantuan_yang_baik']
            Seberapa_penting_pelayan_berpenampilan_bersih_dan_rapi = request.POST[
                'Seberapa_penting_pelayan_berpenampilan_bersih_dan_rapi']
            Seberapa_penting_menu_dapat_dimengerti_dengan_mudah = request.POST[
                'Seberapa_penting_menu_dapat_dimengerti_dengan_mudah']
            Seberapa_penting_suasana_restoran_memberikan_pengalaman = request.POST[
                'Seberapa_penting_suasana_restoran_memberikan_pengalaman']
            Seberapa_penting_terdapat_aktivitas_dan_hiburan = request.POST[
                'Seberapa_penting_terdapat_aktivitas_dan_hiburan']
            Seberapa_penting_restoran_terlihat_menarik = request.POST['Seberapa_penting_restoran_terlihat_menarik']
            Seberapa_penting_lokasi_restoran_bagus_dan_mudah_diakses = request.POST[
                'Seberapa_penting_lokasi_restoran_bagus_dan_mudah_diakses']
            Seberapa_penting_pesanan_diantar_sesuai_dengan_yang_dijanjikan = request.POST[
                'Seberapa_penting_pesanan_diantar_sesuai_dengan_yang_dijanjikan']
            Seberapa_penting_pesanan_diantar_dengan_segera = request.POST[
                'Seberapa_penting_pesanan_diantar_dengan_segera']

            Survey_Makanan_Resto = buat_survey_makanan_resto(username=username, responden_name=responden_name,
                                                             gender=gender, umur=umur,
                                                             pekerjaan=pekerjaan,
                                                             status=status,
                                                             pendapatan=pendapatan,
                                                             Seberapa_penting_konsistensi_makanan_yang_disajikan=Seberapa_penting_konsistensi_makanan_yang_disajikan,
                                                             Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun=Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun,
                                                             Seberapa_penting_kualitas_makanan_yang_tinggi=Seberapa_penting_kualitas_makanan_yang_tinggi,
                                                             Seberapa_penting_bahan_makanan_yang_digunakan_segar=Seberapa_penting_bahan_makanan_yang_digunakan_segar,
                                                             Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa=Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa,
                                                             Seberapa_penting_ketersediaan_menu_makanan_lokal=Seberapa_penting_ketersediaan_menu_makanan_lokal,
                                                             Seberapa_penting_ketersediaan_menu_makanan_yang_menarik=Seberapa_penting_ketersediaan_menu_makanan_yang_menarik,
                                                             Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi=Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi,
                                                             Harga_makanan_yang_wajar=Harga_makanan_yang_wajar,
                                                             Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan=Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan,
                                                             Terdapat_pilihan_menu_makanan_sehat_di_restoran=Terdapat_pilihan_menu_makanan_sehat_di_restoran,
                                                             Makanan_mengandung_gizi_yang_baik=Makanan_mengandung_gizi_yang_baik,
                                                             Seberapa_penting_makanan_dimasak_secara_higienis=Seberapa_penting_makanan_dimasak_secara_higienis,
                                                             Seberapa_penting_kebersihan_dijaga_dengan_baik_oleh_pelayan=Seberapa_penting_kebersihan_dijaga_dengan_baik_oleh_pelayan,
                                                             Seberapa_penting_terdapat_standar_terhadap_pelayanan=Seberapa_penting_terdapat_standar_terhadap_pelayanan,
                                                             Seberapa_penting_pelayan_melakukan_pelayanan_secara_cepat=Seberapa_penting_pelayan_melakukan_pelayanan_secara_cepat,
                                                             Seberapa_penting_pelayan_perhatian_kepada_kebutuhan_pelanggan=Seberapa_penting_pelayan_perhatian_kepada_kebutuhan_pelanggan,
                                                             Seberapa_penting_pelayan_memberikan_bantuan_yang_baik=Seberapa_penting_pelayan_memberikan_bantuan_yang_baik,
                                                             Seberapa_penting_pelayan_berpenampilan_bersih_dan_rapi=Seberapa_penting_pelayan_berpenampilan_bersih_dan_rapi,
                                                             Seberapa_penting_menu_dapat_dimengerti_dengan_mudah=Seberapa_penting_menu_dapat_dimengerti_dengan_mudah,
                                                             Seberapa_penting_suasana_restoran_memberikan_pengalaman=Seberapa_penting_suasana_restoran_memberikan_pengalaman,
                                                             Seberapa_penting_terdapat_aktivitas_dan_hiburan=Seberapa_penting_terdapat_aktivitas_dan_hiburan,
                                                             Seberapa_penting_restoran_terlihat_menarik=Seberapa_penting_restoran_terlihat_menarik,
                                                             Seberapa_penting_lokasi_restoran_bagus_dan_mudah_diakses=Seberapa_penting_lokasi_restoran_bagus_dan_mudah_diakses,
                                                             Seberapa_penting_pesanan_diantar_sesuai_dengan_yang_dijanjikan=Seberapa_penting_pesanan_diantar_sesuai_dengan_yang_dijanjikan,
                                                             Seberapa_penting_pesanan_diantar_dengan_segera=Seberapa_penting_pesanan_diantar_dengan_segera)
            Survey_Makanan_Resto.save()
        elif request.POST['tipe_bisnis'] == 'Makanan - saji di tempat saja':
            username=int(request.POST['id_bisnis'])
            responden_name = request.POST['responden_name']
            umur = request.POST['umur']
            gender = request.POST['gender']
            pekerjaan = request.POST['pekerjaan']
            status = request.POST['status']
            pendapatan = request.POST['pendapatan']
            Seberapa_penting_konsistensi_makanan_yang_disajikan = request.POST[
                'Seberapa_penting_konsistensi_makanan_yang_disajikan']
            Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun = request.POST[
                'Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun']
            Seberapa_penting_kualitas_makanan_yang_tinggi = request.POST[
                'Seberapa_penting_kualitas_makanan_yang_tinggi']
            Seberapa_penting_bahan_makanan_yang_digunakan_segar = request.POST[
                'Seberapa_penting_bahan_makanan_yang_digunakan_segar']
            Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa = request.POST[
                'Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa']
            Seberapa_penting_ketersediaan_menu_makanan_lokal = request.POST[
                'Seberapa_penting_ketersediaan_menu_makanan_lokal']
            Seberapa_penting_ketersediaan_menu_makanan_yang_menarik = request.POST[
                'Seberapa_penting_ketersediaan_menu_makanan_yang_menarik']
            Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi = request.POST[
                'Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi']
            Harga_makanan_yang_wajar = request.POST['Harga_makanan_yang_wajar']
            Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan = request.POST[
                'Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan']
            Terdapat_pilihan_menu_makanan_sehat_di_restoran = request.POST[
                'Terdapat_pilihan_menu_makanan_sehat_di_restoran']
            Makanan_mengandung_gizi_yang_baik = request.POST['Makanan_mengandung_gizi_yang_baik']
            Seberapa_penting_makanan_dimasak_secara_higienis = request.POST[
                'Seberapa_penting_makanan_dimasak_secara_higienis']
            Seberapa_penting_kebersihan_dijaga_dengan_baik_oleh_pelayan = request.POST[
                'Seberapa_penting_kebersihan_dijaga_dengan_baik_oleh_pelayan']
            Seberapa_penting_terdapat_standar_terhadap_pelayanan = request.POST[
                'Seberapa_penting_terdapat_standar_terhadap_pelayanan']
            Seberapa_penting_pelayan_melakukan_pelayanan_secara_cepat = request.POST[
                'Seberapa_penting_pelayan_melakukan_pelayanan_secara_cepat']
            Seberapa_penting_pelayan_perhatian_kepada_kebutuhan_pelanggan = request.POST[
                'Seberapa_penting_pelayan_perhatian_kepada_kebutuhan_pelanggan']
            Seberapa_penting_pelayan_memberikan_bantuan_yang_baik = request.POST[
                'Seberapa_penting_pelayan_memberikan_bantuan_yang_baik']
            Seberapa_penting_pelayan_berpenampilan_bersih_dan_rapi = request.POST[
                'Seberapa_penting_pelayan_berpenampilan_bersih_dan_rapi']
            Seberapa_penting_menu_dapat_dimengerti_dengan_mudah = request.POST[
                'Seberapa_penting_menu_dapat_dimengerti_dengan_mudah']
            Seberapa_penting_suasana_restoran_memberikan_pengalaman = request.POST[
                'Seberapa_penting_suasana_restoran_memberikan_pengalaman']
            Seberapa_penting_terdapat_aktivitas_dan_hiburan = request.POST[
                'Seberapa_penting_terdapat_aktivitas_dan_hiburan']
            Seberapa_penting_restoran_terlihat_menarik = request.POST['Seberapa_penting_restoran_terlihat_menarik']
            Seberapa_penting_lokasi_restoran_bagus_dan_mudah_diakses = request.POST[
                'Seberapa_penting_lokasi_restoran_bagus_dan_mudah_diakses']

            Survey_Makanan_Saji = buat_survey_makanan_saji(username=username, responden_name=responden_name,
                                                           gender=gender, umur=umur,
                                                           pekerjaan=pekerjaan,
                                                           status=status,
                                                           pendapatan=pendapatan,
                                                           Seberapa_penting_konsistensi_makanan_yang_disajikan=Seberapa_penting_konsistensi_makanan_yang_disajikan,
                                                           Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun=Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun,
                                                           Seberapa_penting_kualitas_makanan_yang_tinggi=Seberapa_penting_kualitas_makanan_yang_tinggi,
                                                           Seberapa_penting_bahan_makanan_yang_digunakan_segar=Seberapa_penting_bahan_makanan_yang_digunakan_segar,
                                                           Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa=Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa,
                                                           Seberapa_penting_ketersediaan_menu_makanan_lokal=Seberapa_penting_ketersediaan_menu_makanan_lokal,
                                                           Seberapa_penting_ketersediaan_menu_makanan_yang_menarik=Seberapa_penting_ketersediaan_menu_makanan_yang_menarik,
                                                           Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi=Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi,
                                                           Harga_makanan_yang_wajar=Harga_makanan_yang_wajar,
                                                           Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan=Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan,
                                                           Terdapat_pilihan_menu_makanan_sehat_di_restoran=Terdapat_pilihan_menu_makanan_sehat_di_restoran,
                                                           Makanan_mengandung_gizi_yang_baik=Makanan_mengandung_gizi_yang_baik,
                                                           Seberapa_penting_makanan_dimasak_secara_higienis=Seberapa_penting_makanan_dimasak_secara_higienis,
                                                           Seberapa_penting_kebersihan_dijaga_dengan_baik_oleh_pelayan=Seberapa_penting_kebersihan_dijaga_dengan_baik_oleh_pelayan,
                                                           Seberapa_penting_terdapat_standar_terhadap_pelayanan=Seberapa_penting_terdapat_standar_terhadap_pelayanan,
                                                           Seberapa_penting_pelayan_melakukan_pelayanan_secara_cepat=Seberapa_penting_pelayan_melakukan_pelayanan_secara_cepat,
                                                           Seberapa_penting_pelayan_perhatian_kepada_kebutuhan_pelanggan=Seberapa_penting_pelayan_perhatian_kepada_kebutuhan_pelanggan,
                                                           Seberapa_penting_pelayan_memberikan_bantuan_yang_baik=Seberapa_penting_pelayan_memberikan_bantuan_yang_baik,
                                                           Seberapa_penting_pelayan_berpenampilan_bersih_dan_rapi=Seberapa_penting_pelayan_berpenampilan_bersih_dan_rapi,
                                                           Seberapa_penting_menu_dapat_dimengerti_dengan_mudah=Seberapa_penting_menu_dapat_dimengerti_dengan_mudah,
                                                           Seberapa_penting_suasana_restoran_memberikan_pengalaman=Seberapa_penting_suasana_restoran_memberikan_pengalaman,
                                                           Seberapa_penting_terdapat_aktivitas_dan_hiburan=Seberapa_penting_terdapat_aktivitas_dan_hiburan,
                                                           Seberapa_penting_restoran_terlihat_menarik=Seberapa_penting_restoran_terlihat_menarik,
                                                           Seberapa_penting_lokasi_restoran_bagus_dan_mudah_diakses=Seberapa_penting_lokasi_restoran_bagus_dan_mudah_diakses)
            Survey_Makanan_Saji.save()
        elif request.POST['tipe_bisnis'] == 'Makanan - layan antar saja':
            username=int(request.POST['id_bisnis'])
            responden_name = request.POST['responden_name']
            umur = request.POST['umur']
            gender = request.POST['gender']
            pekerjaan = request.POST['pekerjaan']
            status = request.POST['status']
            pendapatan = request.POST['pendapatan']
            Seberapa_penting_konsistensi_makanan_yang_disajikan = request.POST[
                'Seberapa_penting_konsistensi_makanan_yang_disajikan']
            Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun = request.POST[
                'Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun']
            Seberapa_penting_kualitas_makanan_yang_tinggi = request.POST[
                'Seberapa_penting_kualitas_makanan_yang_tinggi']
            Seberapa_penting_bahan_makanan_yang_digunakan_segar = request.POST[
                'Seberapa_penting_bahan_makanan_yang_digunakan_segar']
            Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa = request.POST[
                'Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa']
            Seberapa_penting_ketersediaan_menu_makanan_lokal = request.POST[
                'Seberapa_penting_ketersediaan_menu_makanan_lokal']
            Seberapa_penting_ketersediaan_menu_makanan_yang_menarik = request.POST[
                'Seberapa_penting_ketersediaan_menu_makanan_yang_menarik']
            Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi = request.POST[
                'Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi']
            Harga_makanan_yang_wajar = request.POST['Harga_makanan_yang_wajar']
            Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan = request.POST[
                'Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan']
            Terdapat_pilihan_menu_makanan_sehat_di_restoran = request.POST[
                'Terdapat_pilihan_menu_makanan_sehat_di_restoran']
            Makanan_mengandung_gizi_yang_baik = request.POST['Makanan_mengandung_gizi_yang_baik']
            Seberapa_penting_pesanan_diantar_sesuai_dengan_yang_dijanjikan = request.POST[
                'Seberapa_penting_pesanan_diantar_sesuai_dengan_yang_dijanjikan']
            Seberapa_penting_pesanan_diantar_dengan_segera = request.POST[
                'Seberapa_penting_pesanan_diantar_dengan_segera']

            Survey_Makanan_Layan_Antar = buat_survey_makanan_layan_antar(username=username,
                                                                         responden_name=responden_name, gender=gender,
                                                                         umur=umur,
                                                                         pekerjaan=pekerjaan,
                                                                         status=status,
                                                                         pendapatan=pendapatan,
                                                                         Seberapa_penting_konsistensi_makanan_yang_disajikan=Seberapa_penting_konsistensi_makanan_yang_disajikan,
                                                                         Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun=Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun,
                                                                         Seberapa_penting_kualitas_makanan_yang_tinggi=Seberapa_penting_kualitas_makanan_yang_tinggi,
                                                                         Seberapa_penting_bahan_makanan_yang_digunakan_segar=Seberapa_penting_bahan_makanan_yang_digunakan_segar,
                                                                         Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa=Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa,
                                                                         Seberapa_penting_ketersediaan_menu_makanan_lokal=Seberapa_penting_ketersediaan_menu_makanan_lokal,
                                                                         Seberapa_penting_ketersediaan_menu_makanan_yang_menarik=Seberapa_penting_ketersediaan_menu_makanan_yang_menarik,
                                                                         Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi=Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi,
                                                                         Harga_makanan_yang_wajar=Harga_makanan_yang_wajar,
                                                                         Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan=Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan,
                                                                         Terdapat_pilihan_menu_makanan_sehat_di_restoran=Terdapat_pilihan_menu_makanan_sehat_di_restoran,
                                                                         Makanan_mengandung_gizi_yang_baik=Makanan_mengandung_gizi_yang_baik,
                                                                         Seberapa_penting_pesanan_diantar_sesuai_dengan_yang_dijanjikan=Seberapa_penting_pesanan_diantar_sesuai_dengan_yang_dijanjikan,
                                                                         Seberapa_penting_pesanan_diantar_dengan_segera=Seberapa_penting_pesanan_diantar_dengan_segera)
            Survey_Makanan_Layan_Antar.save()
        elif request.POST['tipe_bisnis'] == 'Makanan - penyedia saja (layan antar oleh Gojek/Grab)':
            username=int(request.POST['id_bisnis'])
            responden_name = request.POST['responden_name']
            umur = request.POST['umur']
            gender = request.POST['gender']
            pekerjaan = request.POST['pekerjaan']
            status = request.POST['status']
            pendapatan = request.POST['pendapatan']
            Seberapa_penting_konsistensi_makanan_yang_disajikan = request.POST[
                'Seberapa_penting_konsistensi_makanan_yang_disajikan']
            Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun = request.POST[
                'Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun']
            Seberapa_penting_kualitas_makanan_yang_tinggi = request.POST[
                'Seberapa_penting_kualitas_makanan_yang_tinggi']
            Seberapa_penting_bahan_makanan_yang_digunakan_segar = request.POST[
                'Seberapa_penting_bahan_makanan_yang_digunakan_segar']
            Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa = request.POST[
                'Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa']
            Seberapa_penting_ketersediaan_menu_makanan_lokal = request.POST[
                'Seberapa_penting_ketersediaan_menu_makanan_lokal']
            Seberapa_penting_ketersediaan_menu_makanan_yang_menarik = request.POST[
                'Seberapa_penting_ketersediaan_menu_makanan_yang_menarik']
            Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi = request.POST[
                'Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi']
            Harga_makanan_yang_wajar = request.POST['Harga_makanan_yang_wajar']
            Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan = request.POST[
                'Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan']
            Terdapat_pilihan_menu_makanan_sehat_di_restoran = request.POST[
                'Terdapat_pilihan_menu_makanan_sehat_di_restoran']
            Makanan_mengandung_gizi_yang_baik = request.POST['Makanan_mengandung_gizi_yang_baik']

            Survey_Makanan_Penyedia_Saja = buat_survey_makanan_penyedia_jasa(username=username,
                                                                             responden_name=responden_name,
                                                                             gender=gender, umur=umur,
                                                                             pekerjaan=pekerjaan,
                                                                             status=status,
                                                                             pendapatan=pendapatan,
                                                                             Seberapa_penting_konsistensi_makanan_yang_disajikan=Seberapa_penting_konsistensi_makanan_yang_disajikan,
                                                                             Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun=Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun,
                                                                             Seberapa_penting_kualitas_makanan_yang_tinggi=Seberapa_penting_kualitas_makanan_yang_tinggi,
                                                                             Seberapa_penting_bahan_makanan_yang_digunakan_segar=Seberapa_penting_bahan_makanan_yang_digunakan_segar,
                                                                             Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa=Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa,
                                                                             Seberapa_penting_ketersediaan_menu_makanan_lokal=Seberapa_penting_ketersediaan_menu_makanan_lokal,
                                                                             Seberapa_penting_ketersediaan_menu_makanan_yang_menarik=Seberapa_penting_ketersediaan_menu_makanan_yang_menarik,
                                                                             Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi=Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi,
                                                                             Harga_makanan_yang_wajar=Harga_makanan_yang_wajar,
                                                                             Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan=Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan,
                                                                             Terdapat_pilihan_menu_makanan_sehat_di_restoran=Terdapat_pilihan_menu_makanan_sehat_di_restoran,
                                                                             Makanan_mengandung_gizi_yang_baik=Makanan_mengandung_gizi_yang_baik)
            Survey_Makanan_Penyedia_Saja.save()

        return render(request, 'donesurvey.html')

def umum(request):
    if request.method == 'POST':
        username=request.user
        try:
            responden_name = request.POST['responden_name']
            umur = request.POST['umur']
            gender = request.POST['gender']
            pekerjaan = request.POST['pekerjaan']
            status = request.POST['status']
            pendapatan = request.POST['pendapatan']
            sumber_informasi_mengenai_produk = request.POST['sumber_informasi_mengenai_produk']
            frekuensi_pembelian_produk_per_tahun = request.POST['frekuensi_pembelian_produk_per_tahun']
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian = request.POST[
                'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian']
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk = request.POST[
                'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk']
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik = request.POST[
                'tempat_penayangan_iklan_atau_placement_yang_paling_menarik']
            bentuk_iklan_yang_paling_menarik = request.POST['bentuk_iklan_yang_paling_menarik']
            konten_iklan_yang_paling_menarik = request.POST['konten_iklan_yang_paling_menarik']
            saya_senang_mengikuti_komunitas_terdiri_dari_banyak_orang = request.POST[
                'saya_senang_mengikuti_komunitas_terdiri_dari_banyak_orang']
            saya_senang_menghabiskan_waktu_bersama_teman_teman = request.POST[
                'saya_senang_menghabiskan_waktu_bersama_teman_teman']
            Saya_senang_terlibat_dalam_sebuah_proyek = request.POST['Saya_senang_terlibat_dalam_sebuah_proyek']
            Saya_senang_merawat_kuku_rambut_dan_berbagai_bagian_tubuh_saya = request.POST[
                'Saya_senang_merawat_kuku_rambut_dan_berbagai_bagian_tubuh_saya']
            Saya_sering_membeli_peralatan_kosmetik = request.POST['Saya_sering_membeli_peralatan_kosmetik']
            Saya_senang_pergi_ke_salon_untuk_melakukan_perawatan_diri = request.POST[
                'Saya_senang_pergi_ke_salon_untuk_melakukan_perawatan_diri']
            Saya_senang_menjelajahi_tempat_baru_saat_berlibur = request.POST[
                'Saya_senang_menjelajahi_tempat_baru_saat_berlibur']
            Saya_mempunyai_keinginan_untuk_dapat_pergi_ke_seluruh_dunia = request.POST[
                'Saya_mempunyai_keinginan_untuk_dapat_pergi_ke_seluruh_dunia']
            Menghabiskan_waktu_berlibur_dengan_travelling = request.POST[
                'Menghabiskan_waktu_berlibur_dengan_travelling']
            Keluarga_merupakan_hal_yang_sangat_penting_bagi_saya = request.POST[
                'Keluarga_merupakan_hal_yang_sangat_penting_bagi_saya']
            Saya_peduli_terhadap_keluarga_saya = request.POST['Saya_peduli_terhadap_keluarga_saya']
            Saya_selalu_ingin_memenuhi_kebutuhan_keluarga_saya = request.POST[
                'Saya_selalu_ingin_memenuhi_kebutuhan_keluarga_saya']
            Saat_waktu_senggang_saya_melakukan_hobi_saya = request.POST['Saat_waktu_senggang_saya_melakukan_hobi_saya']
            Saya_mencari_hiburan_yang_saya_sukai_saat_waktu_senggang = request.POST[
                'Saya_mencari_hiburan_yang_saya_sukai_saat_waktu_senggang']
            Saya_mempunyai_aktivitas_rutin_di_luar_pekerjaan_utama_saya = request.POST[
                'Saya_mempunyai_aktivitas_rutin_di_luar_pekerjaan_utama_saya']

            Survey_Umum = buat_survey_umum(username=username, responden_name=responden_name, gender=gender, umur=umur,
                                           pekerjaan=pekerjaan,
                                           status=status,
                                           pendapatan=pendapatan,
                                           sumber_informasi_mengenai_produk=sumber_informasi_mengenai_produk,
                                           frekuensi_pembelian_produk_per_tahun=frekuensi_pembelian_produk_per_tahun,
                                           jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian=jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian,
                                           strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk=strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk,
                                           tempat_penayangan_iklan_atau_placement_yang_paling_menarik=tempat_penayangan_iklan_atau_placement_yang_paling_menarik,
                                           bentuk_iklan_yang_paling_menarik=bentuk_iklan_yang_paling_menarik,
                                           konten_iklan_yang_paling_menarik=konten_iklan_yang_paling_menarik,
                                           saya_senang_mengikuti_komunitas_terdiri_dari_banyak_orang=saya_senang_mengikuti_komunitas_terdiri_dari_banyak_orang,
                                           saya_senang_menghabiskan_waktu_bersama_teman_teman=saya_senang_menghabiskan_waktu_bersama_teman_teman,
                                           Saya_senang_terlibat_dalam_sebuah_proyek=Saya_senang_terlibat_dalam_sebuah_proyek,
                                           Saya_senang_merawat_kuku_rambut_dan_berbagai_bagian_tubuh_saya=Saya_senang_merawat_kuku_rambut_dan_berbagai_bagian_tubuh_saya,
                                           Saya_sering_membeli_peralatan_kosmetik=Saya_sering_membeli_peralatan_kosmetik,
                                           Saya_senang_pergi_ke_salon_untuk_melakukan_perawatan_diri=Saya_senang_pergi_ke_salon_untuk_melakukan_perawatan_diri,
                                           Saya_senang_menjelajahi_tempat_baru_saat_berlibur=Saya_senang_menjelajahi_tempat_baru_saat_berlibur,
                                           Saya_mempunyai_keinginan_untuk_dapat_pergi_ke_seluruh_dunia=Saya_mempunyai_keinginan_untuk_dapat_pergi_ke_seluruh_dunia,
                                           Menghabiskan_waktu_berlibur_dengan_travelling=Menghabiskan_waktu_berlibur_dengan_travelling,
                                           Keluarga_merupakan_hal_yang_sangat_penting_bagi_saya=Keluarga_merupakan_hal_yang_sangat_penting_bagi_saya,
                                           Saya_peduli_terhadap_keluarga_saya=Saya_peduli_terhadap_keluarga_saya,
                                           Saya_selalu_ingin_memenuhi_kebutuhan_keluarga_saya=Saya_selalu_ingin_memenuhi_kebutuhan_keluarga_saya,
                                           Saat_waktu_senggang_saya_melakukan_hobi_saya=Saat_waktu_senggang_saya_melakukan_hobi_saya,
                                           Saya_mencari_hiburan_yang_saya_sukai_saat_waktu_senggang=Saya_mencari_hiburan_yang_saya_sukai_saat_waktu_senggang,
                                           Saya_mempunyai_aktivitas_rutin_di_luar_pekerjaan_utama_saya=Saya_mempunyai_aktivitas_rutin_di_luar_pekerjaan_utama_saya)
            Survey_Umum.save()
            return redirect('umum')
        except:
            messages.error(request, 'Form Tidak Boleh Kosong')
            return redirect('umum')

    else:
        return render(request, "umum.html")

def fashion(request):
    if request.method == 'POST':
        username = request.user
        try:
            responden_name = request.POST['responden_name']
            umur = request.POST['umur']
            gender = request.POST['gender']
            pekerjaan = request.POST['pekerjaan']
            status = request.POST['status']
            pendapatan = request.POST['pendapatan']
            sumber_informasi_mengenai_produk = request.POST['sumber_informasi_mengenai_produk']
            frekuensi_pembelian_produk_per_tahun = request.POST['frekuensi_pembelian_produk_per_tahun']
            jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian = request.POST[
                'jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian']
            strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk = request.POST[
                'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk']
            tempat_penayangan_iklan_atau_placement_yang_paling_menarik = request.POST[
                'tempat_penayangan_iklan_atau_placement_yang_paling_menarik']
            bentuk_iklan_yang_paling_menarik = request.POST['bentuk_iklan_yang_paling_menarik']
            konten_iklan_yang_paling_menarik = request.POST['konten_iklan_yang_paling_menarik']
            saya_senang_mengikuti_komunitas_terdiri_dari_banyak_orang = request.POST[
                'saya_senang_mengikuti_komunitas_terdiri_dari_banyak_orang']
            saya_senang_menghabiskan_waktu_bersama_teman_teman = request.POST[
                'saya_senang_menghabiskan_waktu_bersama_teman_teman']
            Saya_senang_terlibat_dalam_sebuah_proyek = request.POST['Saya_senang_terlibat_dalam_sebuah_proyek']
            Saya_senang_merawat_kuku_rambut_dan_berbagai_bagian_tubuh_saya = request.POST[
                'Saya_senang_merawat_kuku_rambut_dan_berbagai_bagian_tubuh_saya']
            Saya_sering_membeli_peralatan_kosmetik = request.POST['Saya_sering_membeli_peralatan_kosmetik']
            Saya_senang_pergi_ke_salon_untuk_melakukan_perawatan_diri = request.POST[
                'Saya_senang_pergi_ke_salon_untuk_melakukan_perawatan_diri']
            Saya_senang_menjelajahi_tempat_baru_saat_berlibur = request.POST[
                'Saya_senang_menjelajahi_tempat_baru_saat_berlibur']
            Saya_mempunyai_keinginan_untuk_dapat_pergi_ke_seluruh_dunia = request.POST[
                'Saya_mempunyai_keinginan_untuk_dapat_pergi_ke_seluruh_dunia']
            Menghabiskan_waktu_berlibur_dengan_travelling = request.POST['Menghabiskan_waktu_berlibur_dengan_travelling']
            Keluarga_merupakan_hal_yang_sangat_penting_bagi_saya = request.POST[
                'Keluarga_merupakan_hal_yang_sangat_penting_bagi_saya']
            Saya_peduli_terhadap_keluarga_saya = request.POST['Saya_peduli_terhadap_keluarga_saya']
            Saya_selalu_ingin_memenuhi_kebutuhan_keluarga_saya = request.POST[
                'Saya_selalu_ingin_memenuhi_kebutuhan_keluarga_saya']
            Saat_waktu_senggang_saya_melakukan_hobi_saya = request.POST['Saat_waktu_senggang_saya_melakukan_hobi_saya']
            Saya_mencari_hiburan_yang_saya_sukai_saat_waktu_senggang = request.POST[
                'Saya_mencari_hiburan_yang_saya_sukai_saat_waktu_senggang']
            Saya_mempunyai_aktivitas_rutin_di_luar_pekerjaan_utama_saya = request.POST[
                'Saya_mempunyai_aktivitas_rutin_di_luar_pekerjaan_utama_saya']
            Banyak_orang_yang_mengenal_saya = request.POST['Banyak_orang_yang_mengenal_saya']
            Saya_termasuk_orang_yang_cepat_dalam_mencoba_tren = request.POST['Saya_termasuk_orang_yang_cepat_dalam_mencoba_tren']
            Saya_menghabiskan_banyak_waktu = request.POST['Saya_menghabiskan_banyak_waktu']
            Saya_mencoba_untuk_memilih_model_fesyen_terbaru = request.POST['Saya_mencoba_untuk_memilih_model_fesyen_terbaru']
            Saya_senang_berbelanja_produk_fesyen = request.POST['Saya_senang_berbelanja_produk_fesyen']
            Saya_lebih_percaya_terhadap_produk_fesyen_dengan_merek_terkenal = request.POST['Saya_lebih_percaya_terhadap_produk_fesyen_dengan_merek_terkenal']
            Menurut_saya_merek_terkenal_selalu_mempunyai_kualitas_yang_baik = request.POST['Menurut_saya_merek_terkenal_selalu_mempunyai_kualitas_yang_baik']
            Saya_tetap_membeli_produk_fesyen_dengan_merek_terkenal = request.POST['Saya_tetap_membeli_produk_fesyen_dengan_merek_terkenal']
            Saya_membeli_produk_fesyen_yang_saya_suka = request.POST['Saya_membeli_produk_fesyen_yang_saya_suka']
            Saya_membeli_produk_fesyen_hanya_saat_diskon = request.POST['Saya_membeli_produk_fesyen_hanya_saat_diskon']
            Saat_saya_berbelanja_produk_fesyen_saya_membandingkan = request.POST['Saat_saya_berbelanja_produk_fesyen_saya_membandingkan']

            Survey_Fashion = buat_survey_fashion(username=username, responden_name=responden_name, gender=gender, umur=umur,
                                           pekerjaan=pekerjaan,
                                           status=status,
                                           pendapatan=pendapatan,
                                           sumber_informasi_mengenai_produk=sumber_informasi_mengenai_produk,
                                           frekuensi_pembelian_produk_per_tahun=frekuensi_pembelian_produk_per_tahun,
                                           jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian=jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian,
                                           strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk=strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk,
                                           tempat_penayangan_iklan_atau_placement_yang_paling_menarik=tempat_penayangan_iklan_atau_placement_yang_paling_menarik,
                                           bentuk_iklan_yang_paling_menarik=bentuk_iklan_yang_paling_menarik,
                                           konten_iklan_yang_paling_menarik=konten_iklan_yang_paling_menarik,
                                           saya_senang_mengikuti_komunitas_terdiri_dari_banyak_orang=saya_senang_mengikuti_komunitas_terdiri_dari_banyak_orang,
                                           saya_senang_menghabiskan_waktu_bersama_teman_teman=saya_senang_menghabiskan_waktu_bersama_teman_teman,
                                           Saya_senang_terlibat_dalam_sebuah_proyek=Saya_senang_terlibat_dalam_sebuah_proyek,
                                           Saya_senang_merawat_kuku_rambut_dan_berbagai_bagian_tubuh_saya=Saya_senang_merawat_kuku_rambut_dan_berbagai_bagian_tubuh_saya,
                                           Saya_sering_membeli_peralatan_kosmetik=Saya_sering_membeli_peralatan_kosmetik,
                                           Saya_senang_pergi_ke_salon_untuk_melakukan_perawatan_diri=Saya_senang_pergi_ke_salon_untuk_melakukan_perawatan_diri,
                                           Saya_senang_menjelajahi_tempat_baru_saat_berlibur=Saya_senang_menjelajahi_tempat_baru_saat_berlibur,
                                           Saya_mempunyai_keinginan_untuk_dapat_pergi_ke_seluruh_dunia=Saya_mempunyai_keinginan_untuk_dapat_pergi_ke_seluruh_dunia,
                                           Menghabiskan_waktu_berlibur_dengan_travelling=Menghabiskan_waktu_berlibur_dengan_travelling,
                                           Keluarga_merupakan_hal_yang_sangat_penting_bagi_saya=Keluarga_merupakan_hal_yang_sangat_penting_bagi_saya,
                                           Saya_peduli_terhadap_keluarga_saya=Saya_peduli_terhadap_keluarga_saya,
                                           Saya_selalu_ingin_memenuhi_kebutuhan_keluarga_saya=Saya_selalu_ingin_memenuhi_kebutuhan_keluarga_saya,
                                           Saat_waktu_senggang_saya_melakukan_hobi_saya=Saat_waktu_senggang_saya_melakukan_hobi_saya,
                                           Saya_mencari_hiburan_yang_saya_sukai_saat_waktu_senggang=Saya_mencari_hiburan_yang_saya_sukai_saat_waktu_senggang,
                                           Saya_mempunyai_aktivitas_rutin_di_luar_pekerjaan_utama_saya=Saya_mempunyai_aktivitas_rutin_di_luar_pekerjaan_utama_saya,
                                            Banyak_orang_yang_mengenal_saya=Banyak_orang_yang_mengenal_saya,Saya_termasuk_orang_yang_cepat_dalam_mencoba_tren=Saya_termasuk_orang_yang_cepat_dalam_mencoba_tren,
                                                 Saya_menghabiskan_banyak_waktu=Saya_menghabiskan_banyak_waktu,Saya_mencoba_untuk_memilih_model_fesyen_terbaru=Saya_mencoba_untuk_memilih_model_fesyen_terbaru,
                                                 Saya_senang_berbelanja_produk_fesyen=Saya_senang_berbelanja_produk_fesyen,Saya_lebih_percaya_terhadap_produk_fesyen_dengan_merek_terkenal=Saya_lebih_percaya_terhadap_produk_fesyen_dengan_merek_terkenal,
                                                 Menurut_saya_merek_terkenal_selalu_mempunyai_kualitas_yang_baik=Menurut_saya_merek_terkenal_selalu_mempunyai_kualitas_yang_baik,Saya_tetap_membeli_produk_fesyen_dengan_merek_terkenal=Saya_tetap_membeli_produk_fesyen_dengan_merek_terkenal,
                                                 Saya_membeli_produk_fesyen_yang_saya_suka=Saya_membeli_produk_fesyen_yang_saya_suka,Saya_membeli_produk_fesyen_hanya_saat_diskon=Saya_membeli_produk_fesyen_hanya_saat_diskon,
                                                 Saat_saya_berbelanja_produk_fesyen_saya_membandingkan=Saat_saya_berbelanja_produk_fesyen_saya_membandingkan)
            Survey_Fashion.save()
            return redirect('fashion')
        except:
            messages.error(request, 'Form Tidak Boleh Kosong')
            return redirect('fashion')
    else:
        return render(request, "fesyen.html")

def makananresto(request):
    if request.method == 'POST':
        username = request.user
        try:
            responden_name = request.POST['responden_name']
            umur = request.POST['umur']
            gender = request.POST['gender']
            pekerjaan = request.POST['pekerjaan']
            status = request.POST['status']
            pendapatan = request.POST['pendapatan']
            Seberapa_penting_konsistensi_makanan_yang_disajikan = request.POST['Seberapa_penting_konsistensi_makanan_yang_disajikan']
            Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun = request.POST['Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun']
            Seberapa_penting_kualitas_makanan_yang_tinggi = request.POST['Seberapa_penting_kualitas_makanan_yang_tinggi']
            Seberapa_penting_bahan_makanan_yang_digunakan_segar = request.POST['Seberapa_penting_bahan_makanan_yang_digunakan_segar']
            Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa = request.POST['Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa']
            Seberapa_penting_ketersediaan_menu_makanan_lokal = request.POST['Seberapa_penting_ketersediaan_menu_makanan_lokal']
            Seberapa_penting_ketersediaan_menu_makanan_yang_menarik = request.POST['Seberapa_penting_ketersediaan_menu_makanan_yang_menarik']
            Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi = request.POST['Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi']
            Harga_makanan_yang_wajar = request.POST['Harga_makanan_yang_wajar']
            Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan = request.POST['Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan']
            Terdapat_pilihan_menu_makanan_sehat_di_restoran = request.POST['Terdapat_pilihan_menu_makanan_sehat_di_restoran']
            Makanan_mengandung_gizi_yang_baik = request.POST['Makanan_mengandung_gizi_yang_baik']
            Seberapa_penting_makanan_dimasak_secara_higienis = request.POST['Seberapa_penting_makanan_dimasak_secara_higienis']
            Seberapa_penting_kebersihan_dijaga_dengan_baik_oleh_pelayan = request.POST['Seberapa_penting_kebersihan_dijaga_dengan_baik_oleh_pelayan']
            Seberapa_penting_terdapat_standar_terhadap_pelayanan = request.POST['Seberapa_penting_terdapat_standar_terhadap_pelayanan']
            Seberapa_penting_pelayan_melakukan_pelayanan_secara_cepat = request.POST['Seberapa_penting_pelayan_melakukan_pelayanan_secara_cepat']
            Seberapa_penting_pelayan_perhatian_kepada_kebutuhan_pelanggan = request.POST['Seberapa_penting_pelayan_perhatian_kepada_kebutuhan_pelanggan']
            Seberapa_penting_pelayan_memberikan_bantuan_yang_baik = request.POST['Seberapa_penting_pelayan_memberikan_bantuan_yang_baik']
            Seberapa_penting_pelayan_berpenampilan_bersih_dan_rapi = request.POST['Seberapa_penting_pelayan_berpenampilan_bersih_dan_rapi']
            Seberapa_penting_menu_dapat_dimengerti_dengan_mudah = request.POST['Seberapa_penting_menu_dapat_dimengerti_dengan_mudah']
            Seberapa_penting_suasana_restoran_memberikan_pengalaman = request.POST['Seberapa_penting_suasana_restoran_memberikan_pengalaman']
            Seberapa_penting_terdapat_aktivitas_dan_hiburan = request.POST['Seberapa_penting_terdapat_aktivitas_dan_hiburan']
            Seberapa_penting_restoran_terlihat_menarik = request.POST['Seberapa_penting_restoran_terlihat_menarik']
            Seberapa_penting_lokasi_restoran_bagus_dan_mudah_diakses = request.POST['Seberapa_penting_lokasi_restoran_bagus_dan_mudah_diakses']
            Seberapa_penting_pesanan_diantar_sesuai_dengan_yang_dijanjikan = request.POST['Seberapa_penting_pesanan_diantar_sesuai_dengan_yang_dijanjikan']
            Seberapa_penting_pesanan_diantar_dengan_segera = request.POST['Seberapa_penting_pesanan_diantar_dengan_segera']

            Survey_Makanan_Resto = buat_survey_makanan_resto(username=username, responden_name=responden_name, gender=gender, umur=umur,
                                                 pekerjaan=pekerjaan,
                                                 status=status,
                                                 pendapatan=pendapatan,Seberapa_penting_konsistensi_makanan_yang_disajikan=Seberapa_penting_konsistensi_makanan_yang_disajikan,
                                                             Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun=Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun,
                                                             Seberapa_penting_kualitas_makanan_yang_tinggi=Seberapa_penting_kualitas_makanan_yang_tinggi,
                                                             Seberapa_penting_bahan_makanan_yang_digunakan_segar=Seberapa_penting_bahan_makanan_yang_digunakan_segar,
                                                             Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa=Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa,
                                                             Seberapa_penting_ketersediaan_menu_makanan_lokal=Seberapa_penting_ketersediaan_menu_makanan_lokal,
                                                             Seberapa_penting_ketersediaan_menu_makanan_yang_menarik=Seberapa_penting_ketersediaan_menu_makanan_yang_menarik,
                                                             Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi=Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi,
                                                             Harga_makanan_yang_wajar=Harga_makanan_yang_wajar,Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan=Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan,
                                                             Terdapat_pilihan_menu_makanan_sehat_di_restoran=Terdapat_pilihan_menu_makanan_sehat_di_restoran,Makanan_mengandung_gizi_yang_baik=Makanan_mengandung_gizi_yang_baik,
                                                             Seberapa_penting_makanan_dimasak_secara_higienis=Seberapa_penting_makanan_dimasak_secara_higienis,Seberapa_penting_kebersihan_dijaga_dengan_baik_oleh_pelayan=Seberapa_penting_kebersihan_dijaga_dengan_baik_oleh_pelayan,
                                                             Seberapa_penting_terdapat_standar_terhadap_pelayanan=Seberapa_penting_terdapat_standar_terhadap_pelayanan,Seberapa_penting_pelayan_melakukan_pelayanan_secara_cepat=Seberapa_penting_pelayan_melakukan_pelayanan_secara_cepat,
                                                             Seberapa_penting_pelayan_perhatian_kepada_kebutuhan_pelanggan=Seberapa_penting_pelayan_perhatian_kepada_kebutuhan_pelanggan,Seberapa_penting_pelayan_memberikan_bantuan_yang_baik=Seberapa_penting_pelayan_memberikan_bantuan_yang_baik,
                                                             Seberapa_penting_pelayan_berpenampilan_bersih_dan_rapi=Seberapa_penting_pelayan_berpenampilan_bersih_dan_rapi,Seberapa_penting_menu_dapat_dimengerti_dengan_mudah=Seberapa_penting_menu_dapat_dimengerti_dengan_mudah,
                                                             Seberapa_penting_suasana_restoran_memberikan_pengalaman=Seberapa_penting_suasana_restoran_memberikan_pengalaman,Seberapa_penting_terdapat_aktivitas_dan_hiburan=Seberapa_penting_terdapat_aktivitas_dan_hiburan,
                                                             Seberapa_penting_restoran_terlihat_menarik=Seberapa_penting_restoran_terlihat_menarik,Seberapa_penting_lokasi_restoran_bagus_dan_mudah_diakses=Seberapa_penting_lokasi_restoran_bagus_dan_mudah_diakses,
                                                             Seberapa_penting_pesanan_diantar_sesuai_dengan_yang_dijanjikan=Seberapa_penting_pesanan_diantar_sesuai_dengan_yang_dijanjikan,Seberapa_penting_pesanan_diantar_dengan_segera=Seberapa_penting_pesanan_diantar_dengan_segera)
            Survey_Makanan_Resto.save()
            return redirect('makananresto')
        except:
            messages.error(request, 'Form Tidak Boleh Kosong')
            return redirect('makananresto')
    else:
        return render(request, "makananresto.html")

def makanansaji(request):
    if request.method == 'POST':
        username = request.user
        try:
            responden_name = request.POST['responden_name']
            umur = request.POST['umur']
            gender = request.POST['gender']
            pekerjaan = request.POST['pekerjaan']
            status = request.POST['status']
            pendapatan = request.POST['pendapatan']
            Seberapa_penting_konsistensi_makanan_yang_disajikan = request.POST['Seberapa_penting_konsistensi_makanan_yang_disajikan']
            Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun = request.POST['Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun']
            Seberapa_penting_kualitas_makanan_yang_tinggi = request.POST['Seberapa_penting_kualitas_makanan_yang_tinggi']
            Seberapa_penting_bahan_makanan_yang_digunakan_segar = request.POST['Seberapa_penting_bahan_makanan_yang_digunakan_segar']
            Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa = request.POST['Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa']
            Seberapa_penting_ketersediaan_menu_makanan_lokal = request.POST['Seberapa_penting_ketersediaan_menu_makanan_lokal']
            Seberapa_penting_ketersediaan_menu_makanan_yang_menarik = request.POST['Seberapa_penting_ketersediaan_menu_makanan_yang_menarik']
            Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi = request.POST['Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi']
            Harga_makanan_yang_wajar = request.POST['Harga_makanan_yang_wajar']
            Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan = request.POST['Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan']
            Terdapat_pilihan_menu_makanan_sehat_di_restoran = request.POST['Terdapat_pilihan_menu_makanan_sehat_di_restoran']
            Makanan_mengandung_gizi_yang_baik = request.POST['Makanan_mengandung_gizi_yang_baik']
            Seberapa_penting_makanan_dimasak_secara_higienis = request.POST['Seberapa_penting_makanan_dimasak_secara_higienis']
            Seberapa_penting_kebersihan_dijaga_dengan_baik_oleh_pelayan = request.POST['Seberapa_penting_kebersihan_dijaga_dengan_baik_oleh_pelayan']
            Seberapa_penting_terdapat_standar_terhadap_pelayanan = request.POST['Seberapa_penting_terdapat_standar_terhadap_pelayanan']
            Seberapa_penting_pelayan_melakukan_pelayanan_secara_cepat = request.POST['Seberapa_penting_pelayan_melakukan_pelayanan_secara_cepat']
            Seberapa_penting_pelayan_perhatian_kepada_kebutuhan_pelanggan = request.POST['Seberapa_penting_pelayan_perhatian_kepada_kebutuhan_pelanggan']
            Seberapa_penting_pelayan_memberikan_bantuan_yang_baik = request.POST['Seberapa_penting_pelayan_memberikan_bantuan_yang_baik']
            Seberapa_penting_pelayan_berpenampilan_bersih_dan_rapi = request.POST['Seberapa_penting_pelayan_berpenampilan_bersih_dan_rapi']
            Seberapa_penting_menu_dapat_dimengerti_dengan_mudah = request.POST['Seberapa_penting_menu_dapat_dimengerti_dengan_mudah']
            Seberapa_penting_suasana_restoran_memberikan_pengalaman = request.POST['Seberapa_penting_suasana_restoran_memberikan_pengalaman']
            Seberapa_penting_terdapat_aktivitas_dan_hiburan = request.POST['Seberapa_penting_terdapat_aktivitas_dan_hiburan']
            Seberapa_penting_restoran_terlihat_menarik = request.POST['Seberapa_penting_restoran_terlihat_menarik']
            Seberapa_penting_lokasi_restoran_bagus_dan_mudah_diakses = request.POST['Seberapa_penting_lokasi_restoran_bagus_dan_mudah_diakses']

            Survey_Makanan_Saji = buat_survey_makanan_saji(username=username, responden_name=responden_name, gender=gender, umur=umur,
                                                 pekerjaan=pekerjaan,
                                                 status=status,
                                                 pendapatan=pendapatan,Seberapa_penting_konsistensi_makanan_yang_disajikan=Seberapa_penting_konsistensi_makanan_yang_disajikan,
                                                             Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun=Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun,
                                                             Seberapa_penting_kualitas_makanan_yang_tinggi=Seberapa_penting_kualitas_makanan_yang_tinggi,
                                                             Seberapa_penting_bahan_makanan_yang_digunakan_segar=Seberapa_penting_bahan_makanan_yang_digunakan_segar,
                                                             Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa=Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa,
                                                             Seberapa_penting_ketersediaan_menu_makanan_lokal=Seberapa_penting_ketersediaan_menu_makanan_lokal,
                                                             Seberapa_penting_ketersediaan_menu_makanan_yang_menarik=Seberapa_penting_ketersediaan_menu_makanan_yang_menarik,
                                                             Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi=Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi,
                                                             Harga_makanan_yang_wajar=Harga_makanan_yang_wajar,Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan=Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan,
                                                             Terdapat_pilihan_menu_makanan_sehat_di_restoran=Terdapat_pilihan_menu_makanan_sehat_di_restoran,Makanan_mengandung_gizi_yang_baik=Makanan_mengandung_gizi_yang_baik,
                                                             Seberapa_penting_makanan_dimasak_secara_higienis=Seberapa_penting_makanan_dimasak_secara_higienis,Seberapa_penting_kebersihan_dijaga_dengan_baik_oleh_pelayan=Seberapa_penting_kebersihan_dijaga_dengan_baik_oleh_pelayan,
                                                             Seberapa_penting_terdapat_standar_terhadap_pelayanan=Seberapa_penting_terdapat_standar_terhadap_pelayanan,Seberapa_penting_pelayan_melakukan_pelayanan_secara_cepat=Seberapa_penting_pelayan_melakukan_pelayanan_secara_cepat,
                                                             Seberapa_penting_pelayan_perhatian_kepada_kebutuhan_pelanggan=Seberapa_penting_pelayan_perhatian_kepada_kebutuhan_pelanggan,Seberapa_penting_pelayan_memberikan_bantuan_yang_baik=Seberapa_penting_pelayan_memberikan_bantuan_yang_baik,
                                                             Seberapa_penting_pelayan_berpenampilan_bersih_dan_rapi=Seberapa_penting_pelayan_berpenampilan_bersih_dan_rapi,Seberapa_penting_menu_dapat_dimengerti_dengan_mudah=Seberapa_penting_menu_dapat_dimengerti_dengan_mudah,
                                                             Seberapa_penting_suasana_restoran_memberikan_pengalaman=Seberapa_penting_suasana_restoran_memberikan_pengalaman,Seberapa_penting_terdapat_aktivitas_dan_hiburan=Seberapa_penting_terdapat_aktivitas_dan_hiburan,
                                                             Seberapa_penting_restoran_terlihat_menarik=Seberapa_penting_restoran_terlihat_menarik,Seberapa_penting_lokasi_restoran_bagus_dan_mudah_diakses=Seberapa_penting_lokasi_restoran_bagus_dan_mudah_diakses)
            Survey_Makanan_Saji.save()
            return redirect('makanansaji')
        except:
            messages.error(request, 'Form Tidak Boleh Kosong')
            return redirect('makanansaji')
    else:
        return render(request, "makanansaji.html")

def makananlayanantar(request):
    if request.method == 'POST':
        username = request.user
        try:
            responden_name = request.POST['responden_name']
            umur = request.POST['umur']
            gender = request.POST['gender']
            pekerjaan = request.POST['pekerjaan']
            status = request.POST['status']
            pendapatan = request.POST['pendapatan']
            Seberapa_penting_konsistensi_makanan_yang_disajikan = request.POST['Seberapa_penting_konsistensi_makanan_yang_disajikan']
            Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun = request.POST['Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun']
            Seberapa_penting_kualitas_makanan_yang_tinggi = request.POST['Seberapa_penting_kualitas_makanan_yang_tinggi']
            Seberapa_penting_bahan_makanan_yang_digunakan_segar = request.POST['Seberapa_penting_bahan_makanan_yang_digunakan_segar']
            Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa = request.POST['Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa']
            Seberapa_penting_ketersediaan_menu_makanan_lokal = request.POST['Seberapa_penting_ketersediaan_menu_makanan_lokal']
            Seberapa_penting_ketersediaan_menu_makanan_yang_menarik = request.POST['Seberapa_penting_ketersediaan_menu_makanan_yang_menarik']
            Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi = request.POST['Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi']
            Harga_makanan_yang_wajar = request.POST['Harga_makanan_yang_wajar']
            Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan = request.POST['Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan']
            Terdapat_pilihan_menu_makanan_sehat_di_restoran = request.POST['Terdapat_pilihan_menu_makanan_sehat_di_restoran']
            Makanan_mengandung_gizi_yang_baik = request.POST['Makanan_mengandung_gizi_yang_baik']
            Seberapa_penting_pesanan_diantar_sesuai_dengan_yang_dijanjikan = request.POST['Seberapa_penting_pesanan_diantar_sesuai_dengan_yang_dijanjikan']
            Seberapa_penting_pesanan_diantar_dengan_segera = request.POST['Seberapa_penting_pesanan_diantar_dengan_segera']

            Survey_Makanan_Layan_Antar = buat_survey_makanan_layan_antar(username=username, responden_name=responden_name, gender=gender, umur=umur,
                                                 pekerjaan=pekerjaan,
                                                 status=status,
                                                 pendapatan=pendapatan,Seberapa_penting_konsistensi_makanan_yang_disajikan=Seberapa_penting_konsistensi_makanan_yang_disajikan,
                                                             Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun=Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun,
                                                             Seberapa_penting_kualitas_makanan_yang_tinggi=Seberapa_penting_kualitas_makanan_yang_tinggi,
                                                             Seberapa_penting_bahan_makanan_yang_digunakan_segar=Seberapa_penting_bahan_makanan_yang_digunakan_segar,
                                                             Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa=Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa,
                                                             Seberapa_penting_ketersediaan_menu_makanan_lokal=Seberapa_penting_ketersediaan_menu_makanan_lokal,
                                                             Seberapa_penting_ketersediaan_menu_makanan_yang_menarik=Seberapa_penting_ketersediaan_menu_makanan_yang_menarik,
                                                             Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi=Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi,
                                                             Harga_makanan_yang_wajar=Harga_makanan_yang_wajar,Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan=Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan,
                                                             Terdapat_pilihan_menu_makanan_sehat_di_restoran=Terdapat_pilihan_menu_makanan_sehat_di_restoran,Makanan_mengandung_gizi_yang_baik=Makanan_mengandung_gizi_yang_baik,
                                                             Seberapa_penting_pesanan_diantar_sesuai_dengan_yang_dijanjikan=Seberapa_penting_pesanan_diantar_sesuai_dengan_yang_dijanjikan,Seberapa_penting_pesanan_diantar_dengan_segera=Seberapa_penting_pesanan_diantar_dengan_segera)
            Survey_Makanan_Layan_Antar.save()
            return redirect('makananlayanantar')
        except:
            messages.error(request, 'Form Tidak Boleh Kosong')
            return redirect('makananlayanantar')
    else:
        return render(request, "makananlayanantar.html")

def makananpenyediasaja(request):
    if request.method == 'POST':
        username = request.user
        try:
            responden_name = request.POST['responden_name']
            umur = request.POST['umur']
            gender = request.POST['gender']
            pekerjaan = request.POST['pekerjaan']
            status = request.POST['status']
            pendapatan = request.POST['pendapatan']
            Seberapa_penting_konsistensi_makanan_yang_disajikan = request.POST['Seberapa_penting_konsistensi_makanan_yang_disajikan']
            Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun = request.POST['Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun']
            Seberapa_penting_kualitas_makanan_yang_tinggi = request.POST['Seberapa_penting_kualitas_makanan_yang_tinggi']
            Seberapa_penting_bahan_makanan_yang_digunakan_segar = request.POST['Seberapa_penting_bahan_makanan_yang_digunakan_segar']
            Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa = request.POST['Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa']
            Seberapa_penting_ketersediaan_menu_makanan_lokal = request.POST['Seberapa_penting_ketersediaan_menu_makanan_lokal']
            Seberapa_penting_ketersediaan_menu_makanan_yang_menarik = request.POST['Seberapa_penting_ketersediaan_menu_makanan_yang_menarik']
            Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi = request.POST['Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi']
            Harga_makanan_yang_wajar = request.POST['Harga_makanan_yang_wajar']
            Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan = request.POST['Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan']
            Terdapat_pilihan_menu_makanan_sehat_di_restoran = request.POST['Terdapat_pilihan_menu_makanan_sehat_di_restoran']
            Makanan_mengandung_gizi_yang_baik = request.POST['Makanan_mengandung_gizi_yang_baik']


            Survey_Makanan_Penyedia_Saja = buat_survey_makanan_penyedia_jasa(username=username, responden_name=responden_name, gender=gender, umur=umur,
                                                 pekerjaan=pekerjaan,
                                                 status=status,
                                                 pendapatan=pendapatan,Seberapa_penting_konsistensi_makanan_yang_disajikan=Seberapa_penting_konsistensi_makanan_yang_disajikan,
                                                             Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun=Seberapa_banyak_frekuensi_pembelian_produk_fesyen_per_tahun,
                                                             Seberapa_penting_kualitas_makanan_yang_tinggi=Seberapa_penting_kualitas_makanan_yang_tinggi,
                                                             Seberapa_penting_bahan_makanan_yang_digunakan_segar=Seberapa_penting_bahan_makanan_yang_digunakan_segar,
                                                             Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa=Seberapa_penting_terdapat_menu_menu_yang_tidak_biasa,
                                                             Seberapa_penting_ketersediaan_menu_makanan_lokal=Seberapa_penting_ketersediaan_menu_makanan_lokal,
                                                             Seberapa_penting_ketersediaan_menu_makanan_yang_menarik=Seberapa_penting_ketersediaan_menu_makanan_yang_menarik,
                                                             Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi=Seberapa_penting_merupakan_tempat_yang_sering_dikunjungi,
                                                             Harga_makanan_yang_wajar=Harga_makanan_yang_wajar,Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan=Harga_yang_ditawarkan_setara_dengan_tingkat_pelayanan,
                                                             Terdapat_pilihan_menu_makanan_sehat_di_restoran=Terdapat_pilihan_menu_makanan_sehat_di_restoran,Makanan_mengandung_gizi_yang_baik=Makanan_mengandung_gizi_yang_baik)
            Survey_Makanan_Penyedia_Saja.save()
            return redirect('makananpenyediasaja')
        except:
            messages.error(request, 'Form Tidak Boleh Kosong')
            return redirect('makananpenyediasaja')
    else:
        return render(request, "makanananpenyediajasa.html")
plt.rcParams.update({'font.size':16})
def hasil_segmentasi_umum(request):
    username = request.user.id
    if request.user.last_name == 'Umum':
        obj = buat_survey_umum.objects.all().values()
        data = pd.DataFrame(obj)
        temp=data[data['username'] == username]
        if temp.shape[0] <= 4:
            messages.error(request, 'Data Tidak Mencukupi, minimal data adalah 12')
            return redirect('/owner')


        # umur dan Strategi
        xbaru = np.array([1, 2, 3, 4, 5, 6])
        ybaru = np.array([1, 2, 3, 4, 5])
        wehx = np.array([1, 2, 3, 4, 5, 6])
        wehy = np.array([1, 2, 3, 4, 5])
        print(temp)
        temp = temp.reset_index(drop=True)
        kabehx = temp['sumber_informasi_mengenai_produk']
        kabehy = temp['strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk']
        memex = []
        memey = []
        for i in range(0,len(kabehx),1):
            if kabehx[i] == 'Sosial Media (cth : Instagram, Facebook)':
                memex.append(1)
            elif kabehx[i] == 'Mengunjungi toko langsung secara offline':
                memex.append(2)
            elif kabehx[i] == 'Mesin pencari online (cth : Google)':
                memex.append(3)
            elif kabehx[i] == 'Artis/ influencer':
                memex.append(4)
            elif kabehx[i] == 'Teman-teman atau kerabat':
                memex.append(5)
            elif kabehx[i] == 'Majalah atau media cetak':
                memex.append(6)
        temp['sumber_memex'] = pd.DataFrame(memex)
        print(temp)
        for i in range(0,len(kabehy),1):
            if kabehy[i] == 'Terdapat testimoni toko/produk yang baik':
                memey.append(1)
            elif kabehy[i] == 'Terdapat diskon / potongan harga':
                memey.append(2)
            elif kabehy[i] == 'Terdapat kemudahan pemesanan termasuk pemilihan channel pembelian (website, sosial media, dll) dan channel pembayaran (transfer bank, m-banking, dll)':
                memey.append(3)
            elif kabehy[i] == 'Terdapat layanan yang baik termasuk pengajuan komplain, retur barang, dan lain-lain':
                memey.append(4)
            elif kabehy[i] == 'Toko online tersebut mempunyai konten interaksi yang menarik (giveaway, kuis, informasi berguna, dan lain-lain)':
                memey.append(5)
        print(memey)
        temp['strategi_memey'] = pd.DataFrame(memey)
        urutan = np.sort(temp['Segmen'].unique())
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['sumber_memex'],
                        temp[temp['Segmen'] == urutan[i]][
                            'strategi_memey'],
                        label=urutan[i])
        plt.xticks(xbaru, wehx)
        plt.yticks(ybaru, wehy)
        plt.title('Data Hasil Cluster')
        plt.xlabel('Sumber Informasi')
        plt.ylabel('Strategi Pemasaran yang Paling Menarik')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\sumber_informasi_mengenai_produkXstrategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk.png')


        return render(request, "hasil_segmentasi_umum.html")
    elif request.user.last_name == 'Fashion':
        obj = buat_survey_fashion.objects.all().values()
        data = pd.DataFrame(obj)
        temp = data[data['username'] == username]
        if temp.shape[0] <= 4:
            messages.error(request, 'Data Tidak Mencukupi, minimal data adalah 12')
            return redirect('/owner')
        xbaru = np.array([1, 2, 3, 4, 5, 6])
        ybaru = np.array([1, 2, 3, 4, 5])
        wehx = np.array([1, 2, 3, 4, 5, 6])
        wehy = np.array([1, 2, 3, 4, 5])
        print(temp)
        temp = temp.reset_index(drop=True)
        kabehx = temp['sumber_informasi_mengenai_produk']
        kabehy = temp['strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk']
        memex = []
        memey = []
        for i in range(0, len(kabehx), 1):
            if kabehx[i] == 'Sosial Media (cth : Instagram, Facebook)':
                memex.append(1)
            elif kabehx[i] == 'Mengunjungi toko langsung secara offline':
                memex.append(2)
            elif kabehx[i] == 'Mesin pencari online (cth : Google)':
                memex.append(3)
            elif kabehx[i] == 'Artis/ influencer':
                memex.append(4)
            elif kabehx[i] == 'Teman-teman atau kerabat':
                memex.append(5)
            elif kabehx[i] == 'Majalah atau media cetak':
                memex.append(6)
        temp['sumber_memex'] = pd.DataFrame(memex)
        print(temp)
        for i in range(0, len(kabehy), 1):
            if kabehy[i] == 'Terdapat testimoni toko/produk yang baik':
                memey.append(1)
            elif kabehy[i] == 'Terdapat diskon / potongan harga':
                memey.append(2)
            elif kabehy[
                i] == 'Terdapat kemudahan pemesanan termasuk pemilihan channel pembelian (website, sosial media, dll) dan channel pembayaran (transfer bank, m-banking, dll)':
                memey.append(3)
            elif kabehy[i] == 'Terdapat layanan yang baik termasuk pengajuan komplain, retur barang, dan lain-lain':
                memey.append(4)
            elif kabehy[
                i] == 'Toko online tersebut mempunyai konten interaksi yang menarik (giveaway, kuis, informasi berguna, dan lain-lain)':
                memey.append(5)
        print(memey)
        temp['strategi_memey'] = pd.DataFrame(memey)
        urutan = np.sort(temp['Segmen'].unique())
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['sumber_memex'],
                        temp[temp['Segmen'] == urutan[i]][
                            'strategi_memey'],
                        label=urutan[i])
        plt.xticks(xbaru, wehx)
        plt.yticks(ybaru, wehy)
        plt.title('Data Hasil Cluster')
        plt.xlabel('Sumber Informasi')
        plt.ylabel('Strategi Pemasaran yang Paling Menarik')
        plt.legend()
        plt.savefig(
            'D:\\Projek WebApp\\web1\\web1\\static\\images\\sumber_informasi_mengenai_produkXstrategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk.png')

        return render(request, "hasil_segmentasi_fashion.html")
    elif request.user.last_name == 'Makanan - restoran & pesan antar':
        obj = buat_survey_makanan_resto.objects.all().values()
        data = pd.DataFrame(obj)
        temp = data[data['username'] == username]
        if temp.shape[0] <= 4:
            messages.error(request, 'Data Tidak Mencukupi, minimal data adalah 12')
            return redirect('/owner')
        temp=temp.drop(['id','username'],axis=1)
        asshole=temp.groupby('Segmen').mean()
        asshole = asshole.std(axis=0)
        asshole_x = asshole.idxmax()
        asshole_y = asshole.drop(asshole_x).idxmax()
        print(asshole)
        print(asshole_x)
        print(asshole_y)
        total_x = 0
        total_y = 0
        for i in asshole_x:
            total_x=total_x+1
        for i in asshole_y:
            total_y=total_y+1
        print(total_x)
        print(total_y)
        if total_x >= total_y:
            boobs_x = asshole_x
            boobs_y = asshole_y
        elif total_x < total_y:
            boobs_x = asshole_y
            boobs_y = asshole_x
        print(boobs_x)
        print(boobs_y)
        urutan = np.sort(temp['Segmen'].unique())

        xbaru = np.array([1, 2, 3, 4, 5])
        ybaru = np.array([1, 2, 3, 4, 5])
        wehx = np.array([1, 2, 3, 4, 5])
        wehy = np.array([1, 2, 3, 4, 5])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]][boobs_x],
                        temp[temp['Segmen'] == urutan[i]][
                            boobs_y],
                        label=urutan[i])
        plt.xticks(xbaru, wehx)
        plt.yticks(ybaru, wehy)
        plt.title('Data Hasil Cluster')
        plt.xlabel(boobs_x.replace("_"," "))
        plt.ylabel(boobs_y.replace("_"," "))
        plt.legend()
        plt.savefig(
            'D:\\Projek WebApp\\web1\\web1\\static\\images\\sumber_informasi_mengenai_produkXstrategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk.png')

        return render(request, "hasil_segmentasi_makananresto.html")
    elif request.user.last_name == 'Makanan - saji di tempat saja':
        obj = buat_survey_makanan_saji.objects.all().values()
        data = pd.DataFrame(obj)
        temp = data[data['username'] == username]
        if temp.shape[0] <= 4:
            messages.error(request, 'Data Tidak Mencukupi, minimal data adalah 12')
            return redirect('/owner')
        temp = temp.drop(['id', 'username'], axis=1)
        asshole = temp.groupby('Segmen').mean()
        asshole = asshole.std(axis=0)
        asshole_x = asshole.idxmax()
        asshole_y = asshole.drop(asshole_x).idxmax()
        print(asshole)
        print(asshole_x)
        print(asshole_y)
        total_x = 0
        total_y = 0
        for i in asshole_x:
            total_x = total_x + 1
        for i in asshole_y:
            total_y = total_y + 1
        print(total_x)
        print(total_y)
        if total_x >= total_y:
            boobs_x = asshole_x
            boobs_y = asshole_y
        elif total_x < total_y:
            boobs_x = asshole_y
            boobs_y = asshole_x
        print(boobs_x)
        print(boobs_y)
        urutan = np.sort(temp['Segmen'].unique())

        xbaru = np.array([1, 2, 3, 4, 5])
        ybaru = np.array([1, 2, 3, 4, 5])
        wehx = np.array([1, 2, 3, 4, 5])
        wehy = np.array([1, 2, 3, 4, 5])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]][boobs_x],
                        temp[temp['Segmen'] == urutan[i]][
                            boobs_y],
                        label=urutan[i])
        plt.xticks(xbaru, wehx)
        plt.yticks(ybaru, wehy)
        plt.title('Data Hasil Cluster')
        plt.xlabel(boobs_x.replace("_", " "))
        plt.ylabel(boobs_y.replace("_", " "))
        plt.legend()
        plt.savefig(
            'D:\\Projek WebApp\\web1\\web1\\static\\images\\sumber_informasi_mengenai_produkXstrategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk.png')

        return render(request, "hasil_segmentasi_makanansaji.html")
    elif request.user.last_name == 'Makanan - layan antar saja':
        obj = buat_survey_makanan_layan_antar.objects.all().values()
        data = pd.DataFrame(obj)
        temp = data[data['username'] == username]
        if temp.shape[0] <= 4:
            messages.error(request, 'Data Tidak Mencukupi, minimal data adalah 12')
            return redirect('/owner')
        temp = temp.drop(['id', 'username'], axis=1)
        asshole = temp.groupby('Segmen').mean()
        asshole = asshole.std(axis=0)
        asshole_x = asshole.idxmax()
        asshole_y = asshole.drop(asshole_x).idxmax()
        print(asshole)
        print(asshole_x)
        print(asshole_y)
        total_x = 0
        total_y = 0
        for i in asshole_x:
            total_x = total_x + 1
        for i in asshole_y:
            total_y = total_y + 1
        print(total_x)
        print(total_y)
        if total_x >= total_y:
            boobs_x = asshole_x
            boobs_y = asshole_y
        elif total_x < total_y:
            boobs_x = asshole_y
            boobs_y = asshole_x
        print(boobs_x)
        print(boobs_y)
        urutan = np.sort(temp['Segmen'].unique())

        xbaru = np.array([1, 2, 3, 4, 5])
        ybaru = np.array([1, 2, 3, 4, 5])
        wehx = np.array([1, 2, 3, 4, 5])
        wehy = np.array([1, 2, 3, 4, 5])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]][boobs_x],
                        temp[temp['Segmen'] == urutan[i]][
                            boobs_y],
                        label=urutan[i])
        plt.xticks(xbaru, wehx)
        plt.yticks(ybaru, wehy)
        plt.title('Data Hasil Cluster')
        plt.xlabel(boobs_x.replace("_", " "))
        plt.ylabel(boobs_y.replace("_", " "))
        plt.legend()
        plt.savefig(
            'D:\\Projek WebApp\\web1\\web1\\static\\images\\sumber_informasi_mengenai_produkXstrategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk.png')

        return render(request, "hasil_segmentasi_makananlayanantar.html")
    elif request.user.last_name == 'Makanan - penyedia saja (layan antar oleh Gojek/Grab)':
        obj = buat_survey_makanan_penyedia_jasa.objects.all().values()
        data = pd.DataFrame(obj)
        temp = data[data['username'] == username]
        if temp.shape[0] <= 4:
            messages.error(request, 'Data Tidak Mencukupi, minimal data adalah 12')
            return redirect('/owner')
        temp = temp.drop(['id', 'username'], axis=1)
        asshole = temp.groupby('Segmen').mean()
        asshole = asshole.std(axis=0)
        asshole_x = asshole.idxmax()
        asshole_y = asshole.drop(asshole_x).idxmax()
        print(asshole)
        print(asshole_x)
        print(asshole_y)
        total_x = 0
        total_y = 0
        for i in asshole_x:
            total_x = total_x + 1
        for i in asshole_y:
            total_y = total_y + 1
        print(total_x)
        print(total_y)
        if total_x >= total_y:
            boobs_x = asshole_x
            boobs_y = asshole_y
        elif total_x < total_y:
            boobs_x = asshole_y
            boobs_y = asshole_x
        print(boobs_x)
        print(boobs_y)
        urutan = np.sort(temp['Segmen'].unique())

        xbaru = np.array([1, 2, 3, 4, 5])
        ybaru = np.array([1, 2, 3, 4, 5])
        wehx = np.array([1, 2, 3, 4, 5])
        wehy = np.array([1, 2, 3, 4, 5])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]][boobs_x],
                        temp[temp['Segmen'] == urutan[i]][
                            boobs_y],
                        label=urutan[i])
        plt.xticks(xbaru, wehx)
        plt.yticks(ybaru, wehy)
        plt.title('Data Hasil Cluster')
        plt.xlabel(boobs_x.replace("_", " "))
        plt.ylabel(boobs_y.replace("_", " "))
        plt.legend()
        plt.savefig(
            'D:\\Projek WebApp\\web1\\web1\\static\\images\\sumber_informasi_mengenai_produkXstrategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk.png')

        return render(request, "hasil_segmentasi_makananpenyediasaja.html")


def hasil_segmentasi_fashion(request):
    try:
        username = request.user.id
        print(username)
        obj = buat_survey_fashion.objects.all().values()
        data = pd.DataFrame(obj)
        data=data[data['username'] == username]
        temp=data.drop(['id','username','responden_name'],axis=1)
        webapp=data.drop(['id','username','responden_name'],axis=1)
        umur = temp['umur']
        njai = []
        for i in range(0, len(umur), 1):
            if umur[i] == '<18 Tahun':
                njai.append(1)
            elif umur[i] == '18-23 Tahun':
                njai.append(2)
            elif umur[i] == '24-30 Tahun':
                njai.append(3)
            elif umur[i] == '31-35 Tahun':
                njai.append(4)
            elif umur[i] == '36-40 Tahun':
                njai.append(5)
            elif umur[i] == '41-45 Tahun':
                njai.append(6)
            elif umur[i] == '>45 Tahun':
                njai.append(7)
        temp['umur'] = pd.DataFrame(njai)

        umur = temp['pendapatan']
        njai = []
        for i in range(0, len(umur), 1):
            if umur[i] == '< Rp2.500.000':
                njai.append(1)
            elif umur[i] == 'Rp2.500.000 - Rp5.000.000':
                njai.append(2)
            elif umur[i] == 'Rp5.000.000 - Rp10.000.000':
                njai.append(3)
            elif umur[i] == 'Rp10.000.000 - Rp15.000.000':
                njai.append(4)
            elif umur[i] == 'Rp15.000.000 - Rp25.000.000':
                njai.append(5)
            elif umur[i] == '>Rp25.000.000':
                njai.append(6)
        temp['pendapatan'] = pd.DataFrame(njai)

        umur = temp['frekuensi_pembelian_produk_per_tahun']
        njai = []
        for i in range(0, len(umur), 1):
            if umur[i] == '1 - 2 kali':
                njai.append(1)
            elif umur[i] == '3 - 5 kali':
                njai.append(2)
            elif umur[i] == '> 5 kali':
                njai.append(3)
        temp['frekuensi_pembelian_produk_per_tahun'] = pd.DataFrame(njai)

        umur = temp['jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian']
        njai = []
        for i in range(0, len(umur), 1):
            if umur[i] == 'Rp100.000 - Rp200.000':
                njai.append(1)
            elif umur[i] == 'Rp200.000 - Rp500.000':
                njai.append(2)
            elif umur[i] == 'Rp500.000 - Rp1.000.000':
                njai.append(3)
            elif umur[i] == 'Rp1.000.000 - Rp1.500.000':
                njai.append(4)
            elif umur[i] == '> Rp1.500.000':
                njai.append(5)
        temp['jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'] = pd.DataFrame(njai)

        data = pd.get_dummies(temp)
        range_n_clusters = [2, 3]

        cost = []
        klust = []
        for klaster in range_n_clusters:
            clusterer = KModes(n_clusters=klaster, init='Huang', n_init=11, verbose=1)
            preds = clusterer.fit_predict(data)

            score = silhouette_score(data, preds)
            cost.append(score)
            klust.append(klaster)

        cost = pd.DataFrame(cost)
        cost.index = klust
        n_cluster = int(cost.idxmax())

        # define the k-modes model
        km = KModes(n_clusters=n_cluster, init='Huang', n_init=11, verbose=1)
        # fit the clusters to the skills dataframe
        clusters = km.fit_predict(data)
        # get an array of cluster modes
        kmodes = km.cluster_centroids_
        shape = kmodes.shape

        webapp['Segmen'] = clusters
        temp['Segmen'] = clusters
        urutan = np.sort(temp['Segmen'].unique())

        # pekerjaan squad
        # pekerjaan dan status menikah
        ybaru = ['Pelajar / Mahasiswa', 'Pekerja penuh waktu',
                 'Pekerja paruh waktu', 'Ibu Rumah Tangga', 'Sedang tidak bekerja',
                 'Pekerja profesional mandiri',
                 'Wirausaha', 'Pensiun']
        xbaru = ['Belum Menikah', 'Sudah Menikah, sudah mempunyai anak',
                 'Sudah Menikah, belum mempunyai anak']
        wehy = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        wehx = np.array([0, 1, 2])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['status'],
                        temp[temp['Segmen'] == urutan[i]]['pekerjaan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pekerjaan vs Status Perkawinan')
        plt.xlabel('Pekerjaan')
        plt.ylabel('Status Perkawinan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pekerjaanXstatus_menikah.png')

        # pekerjaan dan Pendapatan perbulan
        ybaru = ['Pelajar / Mahasiswa', 'Pekerja penuh waktu',
                 'Pekerja paruh waktu', 'Ibu Rumah Tangga', 'Sedang tidak bekerja',
                 'Pekerja profesional mandiri',
                 'Wirausaha', 'Pensiun']
        xbaru = ['< Rp2.500.000', 'Rp2.500.000 - Rp5.000.000', 'Rp5.000.000 - Rp10.000.000', 'Rp10.000.000 - Rp15.000.000',
                 'Rp15.000.000 - Rp25.000.000', '> Rp25.000.000']
        wehy = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        wehx = np.array([1, 2, 3, 4, 5, 6])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['pendapatan'],
                        temp[temp['Segmen'] == urutan[i]]['pekerjaan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pekerjaan vs Pendapatan perbulan')
        plt.xlabel('Pendapatan perbulan')
        plt.ylabel('Pekerjaan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pekerjaanXpendapatanperbulan.png')

        # pekerjaan dan umur
        ybaru = ['Pelajar / Mahasiswa', 'Pekerja penuh waktu',
                 'Pekerja paruh waktu', 'Ibu Rumah Tangga', 'Sedang tidak bekerja',
                 'Pekerja profesional mandiri',
                 'Wirausaha', 'Pensiun']
        xbaru = ['<18 tahun', '18 - 23 tahun', '24 - 30 tahun', '31 - 35 tahun', '36 - 40 tahun', '41 - 45 tahun',
                 '> 45 tahun']
        wehy = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        wehx = np.array([1, 2, 3, 4, 5, 6, 7])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['umur'],
                        temp[temp['Segmen'] == urutan[i]]['pekerjaan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pekerjaan vs Umur')
        plt.xlabel('Umur')
        plt.ylabel('Pekerjaan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pekerjaanXumur.png')

        # pekerjaan dan Bentuk Iklan
        ybaru = ['Pelajar / Mahasiswa', 'Pekerja penuh waktu',
                 'Pekerja paruh waktu', 'Ibu Rumah Tangga', 'Sedang tidak bekerja',
                 'Pekerja profesional mandiri',
                 'Wirausaha', 'Pensiun']
        xbaru = ['Menggunakan satu gambar produk',
                 'Menggunakan beberapa gambar dari beberapa sisi produk',
                 'Menggunakan video']
        wehy = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        wehx = np.array([0, 1, 2])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['bentuk_iklan_yang_paling_menarik'],
                        temp[temp['Segmen'] == urutan[i]]['pekerjaan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pekerjaan vs Bentuk Iklan yang Paling Menarik')
        plt.xlabel('Bentuk Iklan yang Paling Menarik')
        plt.ylabel('Pekerjaan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pekerjaanXbentuk_iklan_yang_paling_menarik.png')

        # pekerjaan dan Frekuensi Membeli
        ybaru = ['Pelajar / Mahasiswa', 'Pekerja penuh waktu',
                 'Pekerja paruh waktu', 'Ibu Rumah Tangga', 'Sedang tidak bekerja',
                 'Pekerja profesional mandiri',
                 'Wirausaha', 'Pensiun']
        xbaru = ['1 - 2 kali', '3 - 5 kali', '> 5 kali']
        wehy = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        wehx = np.array([1, 2, 3])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['frekuensi_pembelian_produk_per_tahun'],
                        temp[temp['Segmen'] == urutan[i]]['pekerjaan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pekerjaan vs Frekuensi Pembelian per Tahun')
        plt.xlabel('Frekuensi Pembelian per Tahun')
        plt.ylabel('Pekerjaan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pekerjaanXfrekuensi_pembelian.png')

        # pekerjaan dan Pengeluaran rata-rata
        ybaru = ['Pelajar / Mahasiswa', 'Pekerja penuh waktu',
                 'Pekerja paruh waktu', 'Ibu Rumah Tangga', 'Sedang tidak bekerja',
                 'Pekerja profesional mandiri',
                 'Wirausaha', 'Pensiun']
        xbaru = ['Rp100.000 - Rp200.000', 'Rp200.000 - Rp500.000', 'Rp500.000 - Rp1.000.000', 'Rp1.000.000 - Rp1.500.000',
                 '> Rp1.500.000']
        wehy = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        wehx = np.array([1, 2, 3, 4, 5])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'],
                        temp[temp['Segmen'] == urutan[i]]['pekerjaan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pekerjaan vs Pengeluaran Rata-Rata dalam Sekali Pembelian')
        plt.xlabel('Pengeluaran Rata-Rata dalam Sekali Pembelian')
        plt.ylabel('Pekerjaan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pekerjaanXjumlah_pengeluaran_rata_rata_dalam_sekali_pembelian.png')

        # pekerjaan dan Konten Iklan
        ybaru = ['Pelajar / Mahasiswa', 'Pekerja penuh waktu',
                 'Pekerja paruh waktu', 'Ibu Rumah Tangga', 'Sedang tidak bekerja',
                 'Pekerja profesional mandiri',
                 'Wirausaha', 'Pensiun']
        xbaru = ['Menggunakan foto produk sepatu yang diiklankan',
                 'Menggunakan model / orang yang menggunakan produk sepatu yang diiklankan']
        wehy = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        wehx = np.array([0, 1])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['konten_iklan_yang_paling_menarik'],
                        temp[temp['Segmen'] == urutan[i]]['pekerjaan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pekerjaan vs Konten Iklan yang Paling Menarik')
        plt.xlabel('Konten Iklan yang Paling Menarik')
        plt.ylabel('Pekerjaan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pekerjaanXkonten_iklan_yang_paling_menarik.png')

        # pekerjaan dan Strategi
        xbaru = ['Pelajar / Mahasiswa', 'Pekerja penuh waktu',
                 'Pekerja paruh waktu', 'Ibu Rumah Tangga', 'Sedang tidak bekerja',
                 'Pekerja profesional mandiri',
                 'Wirausaha', 'Pensiun']
        ybaru = ['Testimoni toko/produk yang baik',
                 'Diskon / potongan harga',
                 'Kemudahan pemesanan dan channel pembayaran (transfer bank, m-banking, dll)',
                 'Layanan yang baik termasuk pengajuan komplain, dan lain-lain',
                 'Mempunyai konten interaksi yang menarik (giveaway, dan lain-lain)']
        wehx = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        wehy = np.array([0, 1, 2, 3, 4])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['pekerjaan'],
                        temp[temp['Segmen'] == urutan[i]][
                            'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pekerjaan vs Strategi Pemasaran yang Paling Menarik')
        plt.xlabel('Strategi Pemasaran yang Paling Menarik')
        plt.ylabel('Pekerjaan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pekerjaanXstrategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk.png')

        # pekerjaan dan Sumber informasi
        ybaru = ['Pelajar / Mahasiswa', 'Pekerja penuh waktu',
                 'Pekerja paruh waktu', 'Ibu Rumah Tangga', 'Sedang tidak bekerja',
                 'Pekerja profesional mandiri',
                 'Wirausaha', 'Pensiun']
        xbaru = ['Sosial Media (cth : Instagram, Facebook)',
                 'Mengunjungi toko langsung secara offline',
                 'Mesin pencari online (cth : Google)',
                 'Artis / Fashion & Beauty Influencer', 'Teman-teman atau kerabat',
                 'Majalah atau media cetak']
        wehy = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        wehx = np.array([0, 1, 2, 3, 4, 5])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['sumber_informasi_mengenai_produk'],
                        temp[temp['Segmen'] == urutan[i]]['pekerjaan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pekerjaan vs Sumber Informasi')
        plt.xlabel('Sumber Informasi')
        plt.ylabel('Pekerjaan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pekerjaanXsumber_informasi_mengenai_produk.png')

        # pekerjaan dan tempat penayangan iklan
        ybaru = ['Pelajar / Mahasiswa', 'Pekerja penuh waktu',
                 'Pekerja paruh waktu', 'Ibu Rumah Tangga', 'Sedang tidak bekerja',
                 'Pekerja profesional mandiri',
                 'Wirausaha', 'Pensiun']
        xbaru = ['Story pada sosial media Instagram',
                 'Post / Feed pada sosial media Instagram',
                 'Post / Feed pada sosial media Facebook']
        wehy = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        wehx = np.array([0, 1, 2])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['tempat_penayangan_iklan_atau_placement_yang_paling_menarik'],
                        temp[temp['Segmen'] == urutan[i]]['pekerjaan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pekerjaan vs Tempat Penayangan Iklan yang Paling Menarik')
        plt.xlabel('Tempat Penayangan Iklan yang Paling Menarik')
        plt.ylabel('Pekerjaan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pekerjaanXtempat_penayangan_iklan_atau_placement_yang_paling_menarik.png')

        # pendapatan perbulan squad
        # pendapatan perbulan dan status menikah
        ybaru = ['< Rp2.500.000', 'Rp2.500.000 - Rp5.000.000', 'Rp5.000.000 - Rp10.000.000', 'Rp10.000.000 - Rp15.000.000',
                 'Rp15.000.000 - Rp25.000.000', '> Rp25.000.000']
        xbaru = ['Belum Menikah', 'Sudah Menikah, sudah mempunyai anak',
                 'Sudah Menikah, belum mempunyai anak']
        wehy = np.array([1, 2, 3, 4, 5, 6])
        wehx = np.array([0, 1, 2])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['status'],
                        temp[temp['Segmen'] == urutan[i]]['pendapatan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pendapatan Perbulan vs Status Perkawinan')
        plt.xlabel('Pendapatan Perbulan')
        plt.ylabel('Status Perkawinan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pendapatanXstatus_menikah.png')

        # pendapatan perbulan dan umur
        xbaru = ['<18 tahun', '18 - 23 tahun', '24 - 30 tahun', '31 - 35 tahun', '36 - 40 tahun', '41 - 45 tahun',
                 '> 45 tahun']
        ybaru = ['< Rp2.500.000', 'Rp2.500.000 - Rp5.000.000', 'Rp5.000.000 - Rp10.000.000', 'Rp10.000.000 - Rp15.000.000',
                 'Rp15.000.000 - Rp25.000.000', '> Rp25.000.000']
        wehx = np.array([1, 2, 3, 4, 5, 6, 7])
        wehy = np.array([1, 2, 3, 4, 5, 6])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['umur'],
                        temp[temp['Segmen'] == urutan[i]]['pendapatan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pendapatan perbulan vs Umur')
        plt.xlabel('Umur')
        plt.ylabel('Pendapatan perbulan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pendapatanXumur.png')

        # pendapatan perbulan dan Bentuk Iklan
        ybaru = ['< Rp2.500.000', 'Rp2.500.000 - Rp5.000.000', 'Rp5.000.000 - Rp10.000.000', 'Rp10.000.000 - Rp15.000.000',
                 'Rp15.000.000 - Rp25.000.000', '> Rp25.000.000']
        xbaru = ['Menggunakan satu gambar produk',
                 'Menggunakan beberapa gambar dari beberapa sisi produk',
                 'Menggunakan video']
        wehy = np.array([1, 2, 3, 4, 5, 6])
        wehx = np.array([0, 1, 2])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['bentuk_iklan_yang_paling_menarik'],
                        temp[temp['Segmen'] == urutan[i]]['pendapatan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pendapatan perbulan vs Bentuk Iklan yang Paling Menarik')
        plt.xlabel('Bentuk Iklan yang Paling Menarik')
        plt.ylabel('Pendapatan perbulan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pendapatanXbentuk_iklan_yang_paling_menarik.png')

        # pendapatan dan Frekuensi Membeli
        ybaru = ['< Rp2.500.000', 'Rp2.500.000 - Rp5.000.000', 'Rp5.000.000 - Rp10.000.000', 'Rp10.000.000 - Rp15.000.000',
                 'Rp15.000.000 - Rp25.000.000', '> Rp25.000.000']
        xbaru = ['1 - 2 kali', '3 - 5 kali', '> 5 kali']
        wehy = np.array([1, 2, 3, 4, 5, 6])
        wehx = np.array([1, 2, 3])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['frekuensi_pembelian_produk_per_tahun'],
                        temp[temp['Segmen'] == urutan[i]]['pendapatan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pendapatan perbulan vs Frekuensi Pembelian per Tahun')
        plt.xlabel('Frekuensi Pembelian per Tahun')
        plt.ylabel('Pendapatan perbulan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pendapatanXfrekuensi_pembelian.png')

        # Pendapatan perbulan dan Pengeluaran rata-rata
        ybaru = ['< Rp2.500.000', 'Rp2.500.000 - Rp5.000.000', 'Rp5.000.000 - Rp10.000.000', 'Rp10.000.000 - Rp15.000.000',
                 'Rp15.000.000 - Rp25.000.000', '> Rp25.000.000']
        xbaru = ['Rp100.000 - Rp200.000', 'Rp200.000 - Rp500.000', 'Rp500.000 - Rp1.000.000', 'Rp1.000.000 - Rp1.500.000',
                 '> Rp1.500.000']
        wehy = np.array([1, 2, 3, 4, 5, 6])
        wehx = np.array([1, 2, 3, 4, 5])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'],
                        temp[temp['Segmen'] == urutan[i]]['pendapatan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pendapatan perbulan vs Pengeluaran Rata-Rata dalam Sekali Pembelian')
        plt.xlabel('Pengeluaran Rata-Rata dalam Sekali Pembelian')
        plt.ylabel('Pendapatan perbulan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pendapatanXjumlah_pengeluaran_rata_rata_dalam_sekali_pembelian.png')

        # Pendapatan perbulan dan Konten Iklan
        ybaru = ['< Rp2.500.000', 'Rp2.500.000 - Rp5.000.000', 'Rp5.000.000 - Rp10.000.000', 'Rp10.000.000 - Rp15.000.000',
                 'Rp15.000.000 - Rp25.000.000', '> Rp25.000.000']
        xbaru = ['Menggunakan foto produk sepatu yang diiklankan',
                 'Menggunakan model / orang yang menggunakan produk sepatu yang diiklankan']
        wehy = np.array([1, 2, 3, 4, 5, 6])
        wehx = np.array([0, 1])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['konten_iklan_yang_paling_menarik'],
                        temp[temp['Segmen'] == urutan[i]]['pendapatan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pendapatan perbulan vs Konten Iklan yang Paling Menarik')
        plt.xlabel('Konten Iklan yang Paling Menarik')
        plt.ylabel('Pendapatan perbulan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pendapatanXkonten_iklan_yang_paling_menarik.png')

        # Pendapatan perbulan dan Strategi
        xbaru = ['< Rp2.500.000', 'Rp2.500.000 - Rp5.000.000', 'Rp5.000.000 - Rp10.000.000', 'Rp10.000.000 - Rp15.000.000',
                 'Rp15.000.000 - Rp25.000.000', '> Rp25.000.000']
        ybaru = ['Testimoni toko/produk yang baik',
                 'Diskon / potongan harga',
                 'Kemudahan pemesanan dan channel pembayaran (transfer bank, m-banking, dll)',
                 'Layanan yang baik termasuk pengajuan komplain, dan lain-lain',
                 'Mempunyai konten interaksi yang menarik (giveaway, dan lain-lain)']
        wehx = np.array([1, 2, 3, 4, 5, 6])
        wehy = np.array([0, 1, 2, 3, 4])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['pendapatan'],
                        temp[temp['Segmen'] == urutan[i]][
                            'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pendapatan perbulan vs Strategi Pemasaran yang Paling Menarik')
        plt.xlabel('Strategi Pemasaran yang Paling Menarik')
        plt.ylabel('Pendapatan perbulan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pendapatanXstrategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk.png')

        # Pendapatan perbulan dan Sumber informasi
        ybaru = ['< Rp2.500.000', 'Rp2.500.000 - Rp5.000.000', 'Rp5.000.000 - Rp10.000.000', 'Rp10.000.000 - Rp15.000.000',
                 'Rp15.000.000 - Rp25.000.000', '> Rp25.000.000']
        xbaru = ['Sosial Media (cth : Instagram, Facebook)',
                 'Mengunjungi toko langsung secara offline',
                 'Mesin pencari online (cth : Google)',
                 'Artis / Fashion & Beauty Influencer', 'Teman-teman atau kerabat',
                 'Majalah atau media cetak']
        wehy = np.array([1, 2, 3, 4, 5, 6])
        wehx = np.array([0, 1, 2, 3, 4, 5])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['sumber_informasi_mengenai_produk'],
                        temp[temp['Segmen'] == urutan[i]]['pendapatan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pendapatan perbulan vs Sumber Informasi')
        plt.xlabel('Sumber Informasi')
        plt.ylabel('Pendapatan perbulan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pendapatanXsumber_informasi_mengenai_produk.png')

        # Pendapatan perbulan dan tempat penayangan iklan
        ybaru = ['< Rp2.500.000', 'Rp2.500.000 - Rp5.000.000', 'Rp5.000.000 - Rp10.000.000', 'Rp10.000.000 - Rp15.000.000',
                 'Rp15.000.000 - Rp25.000.000', '> Rp25.000.000']
        xbaru = ['Story pada sosial media Instagram',
                 'Post / Feed pada sosial media Instagram',
                 'Post / Feed pada sosial media Facebook']
        wehy = np.array([1, 2, 3, 4, 5, 6])
        wehx = np.array([0, 1, 2])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['tempat_penayangan_iklan_atau_placement_yang_paling_menarik'],
                        temp[temp['Segmen'] == urutan[i]]['pendapatan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pendapatan perbulan vs Tempat Penayangan Iklan yang Paling Menarik')
        plt.xlabel('Tempat Penayangan Iklan yang Paling Menarik')
        plt.ylabel('Pendapatan perbulan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pendapatanXtempat_penayangan_iklan_atau_placement_yang_paling_menarik.png')

        # Status perkawinan squad
        # Status perkawinan  dan umur
        xbaru = ['<18 tahun', '18 - 23 tahun', '24 - 30 tahun', '31 - 35 tahun', '36 - 40 tahun', '41 - 45 tahun',
                 '> 45 tahun']
        ybaru = ['Belum Menikah', 'Sudah Menikah, sudah mempunyai anak',
                 'Sudah Menikah, belum mempunyai anak']
        wehx = np.array([1, 2, 3, 4, 5, 6, 7])
        wehy = np.array([0, 1, 2])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['umur'],
                        temp[temp['Segmen'] == urutan[i]]['status'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Status perkawinan vs Umur')
        plt.xlabel('Umur')
        plt.ylabel('Status perkawinan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\status_menikahXumur.png')

        # Status perkawinan  dan Bentuk Iklan
        ybaru = ['Belum Menikah', 'Sudah Menikah, sudah mempunyai anak',
                 'Sudah Menikah, belum mempunyai anak']
        xbaru = ['Menggunakan satu gambar produk',
                 'Menggunakan beberapa gambar dari beberapa sisi produk',
                 'Menggunakan video']
        wehy = np.array([0, 1, 2])
        wehx = np.array([0, 1, 2])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['bentuk_iklan_yang_paling_menarik'],
                        temp[temp['Segmen'] == urutan[i]]['status'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Status perkawinan vs Bentuk Iklan yang Paling Menarik')
        plt.xlabel('Bentuk Iklan yang Paling Menarik')
        plt.ylabel('Status perkawinan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\status_menikahXbentuk_iklan_yang_paling_menarik.png')

        # Status perkawinan  dan Frekuensi Membeli
        ybaru = ['Belum Menikah', 'Sudah Menikah, sudah mempunyai anak',
                 'Sudah Menikah, belum mempunyai anak']
        xbaru = ['1 - 2 kali', '3 - 5 kali', '> 5 kali']
        wehy = np.array([0, 1, 2])
        wehx = np.array([1, 2, 3])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['frekuensi_pembelian_produk_per_tahun'],
                        temp[temp['Segmen'] == urutan[i]]['status'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Status perkawinan vs Frekuensi Pembelian per Tahun')
        plt.xlabel('Frekuensi Pembelian per Tahun')
        plt.ylabel('Status perkawinan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\status_menikahXfrekuensi_pembelian.png')

        # Status perkawinan dan Pengeluaran rata-rata
        ybaru = ['Belum Menikah', 'Sudah Menikah, sudah mempunyai anak',
                 'Sudah Menikah, belum mempunyai anak']
        xbaru = ['Rp100.000 - Rp200.000', 'Rp200.000 - Rp500.000', 'Rp500.000 - Rp1.000.000', 'Rp1.000.000 - Rp1.500.000',
                 '> Rp1.500.000']
        wehy = np.array([0, 1, 2])
        wehx = np.array([1, 2, 3, 4, 5])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'],
                        temp[temp['Segmen'] == urutan[i]]['status'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Status perkawinan vs Pengeluaran Rata-Rata dalam Sekali Pembelian')
        plt.xlabel('Pengeluaran Rata-Rata dalam Sekali Pembelian')
        plt.ylabel('Status perkawinan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\status_menikahXjumlah_pengeluaran_rata_rata_dalam_sekali_pembelian.png')

        # Status perkawinan  dan Konten Iklan
        ybaru = ['Belum Menikah', 'Sudah Menikah, sudah mempunyai anak',
                 'Sudah Menikah, belum mempunyai anak']
        xbaru = ['Menggunakan foto produk sepatu yang diiklankan',
                 'Menggunakan model / orang yang menggunakan produk sepatu yang diiklankan']
        wehy = np.array([0, 1, 2])
        wehx = np.array([0, 1])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['konten_iklan_yang_paling_menarik'],
                        temp[temp['Segmen'] == urutan[i]]['status'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Status perkawinan vs Konten Iklan yang Paling Menarik')
        plt.xlabel('Konten Iklan yang Paling Menarik')
        plt.ylabel('Status perkawinan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\status_menikahXkonten_iklan_yang_paling_menarik.png')

        # Status perkawinan dan Strategi
        xbaru = ['Belum Menikah', 'Sudah Menikah, sudah mempunyai anak',
                 'Sudah Menikah, belum mempunyai anak']
        ybaru = ['Testimoni toko/produk yang baik',
                 'Diskon / potongan harga',
                 'Kemudahan pemesanan dan channel pembayaran (transfer bank, m-banking, dll)',
                 'Layanan yang baik termasuk pengajuan komplain, dan lain-lain',
                 'Mempunyai konten interaksi yang menarik (giveaway, dan lain-lain)']
        wehx = np.array([0, 1, 2])
        wehy = np.array([0, 1, 2, 3, 4])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'],
                        temp[temp['Segmen'] == urutan[i]]['status'],
                        label=urutan[i])
        plt.xticks(wehy, ybaru)
        plt.yticks(wehx, xbaru)
        plt.title('Status perkawinan vs Strategi Pemasaran yang Paling Menarik')
        plt.xlabel('Strategi Pemasaran yang Paling Menarik')
        plt.ylabel('Status perkawinan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\status_menikahXstrategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk.png')

        # Status perkawinan dan Sumber informasi
        ybaru = ['Belum Menikah', 'Sudah Menikah, sudah mempunyai anak',
                 'Sudah Menikah, belum mempunyai anak']
        xbaru = ['Sosial Media (cth : Instagram, Facebook)',
                 'Mengunjungi toko langsung secara offline',
                 'Mesin pencari online (cth : Google)',
                 'Artis / Fashion & Beauty Influencer', 'Teman-teman atau kerabat',
                 'Majalah atau media cetak']
        wehy = np.array([0, 1, 2])
        wehx = np.array([0, 1, 2, 3, 4, 5])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['sumber_informasi_mengenai_produk'],
                        temp[temp['Segmen'] == urutan[i]]['status'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Status perkawinan vs Sumber Informasi')
        plt.xlabel('Sumber Informasi')
        plt.ylabel('Status perkawinan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\status_menikahXsumber_informasi_mengenai_produk.png')

        # Status perkawinan  dan tempat penayangan iklan
        ybaru = ['Belum Menikah', 'Sudah Menikah, sudah mempunyai anak',
                 'Sudah Menikah, belum mempunyai anak']
        xbaru = ['Story pada sosial media Instagram',
                 'Post / Feed pada sosial media Instagram',
                 'Post / Feed pada sosial media Facebook']
        wehy = np.array([0, 1, 2])
        wehx = np.array([0, 1, 2])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['tempat_penayangan_iklan_atau_placement_yang_paling_menarik'],
                        temp[temp['Segmen'] == urutan[i]]['status'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Status perkawinan vs Tempat Penayangan Iklan yang Paling Menarik')
        plt.xlabel('Tempat Penayangan Iklan yang Paling Menarik')
        plt.ylabel('Status perkawinan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\status_menikahXtempat_penayangan_iklan_atau_placement_yang_paling_menarik.png')

        # umur squad
        # umur dan Bentuk Iklan
        ybaru = ['<18 tahun', '18 - 23 tahun', '24 - 30 tahun', '31 - 35 tahun', '36 - 40 tahun', '41 - 45 tahun',
                 '> 45 tahun']
        xbaru = ['Menggunakan satu gambar produk',
                 'Menggunakan beberapa gambar dari beberapa sisi produk',
                 'Menggunakan video']
        wehy = np.array([1, 2, 3, 4, 5, 6, 7])
        wehx = np.array([0, 1, 2])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['bentuk_iklan_yang_paling_menarik'],
                        temp[temp['Segmen'] == urutan[i]]['umur'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Umur vs Bentuk Iklan yang Paling Menarik')
        plt.xlabel('Bentuk Iklan yang Paling Menarik')
        plt.ylabel('Umur')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\umurXbentuk_iklan_yang_paling_menarik.png')

        # umur  dan Frekuensi Membeli
        ybaru = ['<18 tahun', '18 - 23 tahun', '24 - 30 tahun', '31 - 35 tahun', '36 - 40 tahun', '41 - 45 tahun',
                 '> 45 tahun']
        xbaru = ['1 - 2 kali', '3 - 5 kali', '> 5 kali']
        wehy = np.array([1, 2, 3, 4, 5, 6, 7])
        wehx = np.array([1, 2, 3])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['frekuensi_pembelian_produk_per_tahun'],
                        temp[temp['Segmen'] == urutan[i]]['umur'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Umur vs Frekuensi Pembelian per Tahun')
        plt.xlabel('Frekuensi Pembelian per Tahun')
        plt.ylabel('Umur')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\umurXfrekuensi_pembelian.png')

        # umur dan Pengeluaran rata-rata
        ybaru = ['<18 tahun', '18 - 23 tahun', '24 - 30 tahun', '31 - 35 tahun', '36 - 40 tahun', '41 - 45 tahun',
                 '> 45 tahun']
        xbaru = ['Rp100.000 - Rp200.000', 'Rp200.000 - Rp500.000', 'Rp500.000 - Rp1.000.000', 'Rp1.000.000 - Rp1.500.000',
                 '> Rp1.500.000']
        wehy = np.array([1, 2, 3, 4, 5, 6, 7])
        wehx = np.array([1, 2, 3, 4, 5])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['jumlah_pengeluaran_rata_rata_dalam_sekali_pembelian'],
                        temp[temp['Segmen'] == urutan[i]]['umur'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Umur vs Pengeluaran Rata-Rata dalam Sekali Pembelian')
        plt.xlabel('Pengeluaran Rata-Rata dalam Sekali Pembelian')
        plt.ylabel('Umur')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\umurXjumlah_pengeluaran_rata_rata_dalam_sekali_pembelian.png')

        # umur  dan Konten Iklan
        ybaru = ['<18 tahun', '18 - 23 tahun', '24 - 30 tahun', '31 - 35 tahun', '36 - 40 tahun', '41 - 45 tahun',
                 '> 45 tahun']
        xbaru = ['Menggunakan foto produk sepatu yang diiklankan',
                 'Menggunakan model / orang yang menggunakan produk sepatu yang diiklankan']
        wehy = np.array([1, 2, 3, 4, 5, 6, 7])
        wehx = np.array([0, 1])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['konten_iklan_yang_paling_menarik'],
                        temp[temp['Segmen'] == urutan[i]]['umur'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Umur vs Konten Iklan yang Paling Menarik')
        plt.xlabel('Konten Iklan yang Paling Menarik')
        plt.ylabel('Umur')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\umurXkonten_iklan_yang_paling_menarik.png')

        # umur dan Strategi
        xbaru = ['<18 tahun', '18 - 23 tahun', '24 - 30 tahun', '31 - 35 tahun', '36 - 40 tahun', '41 - 45 tahun',
                 '> 45 tahun']
        ybaru = ['Testimoni toko/produk yang baik',
                 'Diskon / potongan harga',
                 'Kemudahan pemesanan dan channel pembayaran (transfer bank, m-banking, dll)',
                 'Layanan yang baik termasuk pengajuan komplain, dan lain-lain',
                 'Mempunyai konten interaksi yang menarik (giveaway, dan lain-lain)']
        wehx = np.array([1, 2, 3, 4, 5, 6, 7])
        wehy = np.array([0, 1, 2, 3, 4])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['umur'],
                        temp[temp['Segmen'] == urutan[i]][
                            'strategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Umur vs Strategi Pemasaran yang Paling Menarik')
        plt.xlabel('Strategi Pemasaran yang Paling Menarik')
        plt.ylabel('Umur')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\umurXstrategi_pemasaran_yang_paling_menarik_dalam_pembelian_produk.png')

        # umur dan Sumber informasi
        ybaru = ['<18 tahun', '18 - 23 tahun', '24 - 30 tahun', '31 - 35 tahun', '36 - 40 tahun', '41 - 45 tahun',
                 '> 45 tahun']
        xbaru = ['Sosial Media (cth : Instagram, Facebook)',
                 'Mengunjungi toko langsung secara offline',
                 'Mesin pencari online (cth : Google)',
                 'Artis / Fashion & Beauty Influencer', 'Teman-teman atau kerabat',
                 'Majalah atau media cetak']
        wehy = np.array([1, 2, 3, 4, 5, 6, 7])
        wehx = np.array([0, 1, 2, 3, 4, 5])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['sumber_informasi_mengenai_produk'],
                        temp[temp['Segmen'] == urutan[i]]['umur'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Umur vs Sumber Informasi')
        plt.xlabel('Sumber Informasi')
        plt.ylabel('Umur')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\umurXsumber_informasi_mengenai_produk.png')

        # umur  dan tempat penayangan iklan
        ybaru = ['<18 tahun', '18 - 23 tahun', '24 - 30 tahun', '31 - 35 tahun', '36 - 40 tahun', '41 - 45 tahun',
                 '> 45 tahun']
        xbaru = ['Story pada sosial media Instagram',
                 'Post / Feed pada sosial media Instagram',
                 'Post / Feed pada sosial media Facebook']
        wehy = np.array([1, 2, 3, 4, 5, 6, 7])
        wehx = np.array([0, 1, 2])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['tempat_penayangan_iklan_atau_placement_yang_paling_menarik'],
                        temp[temp['Segmen'] == urutan[i]]['umur'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Umur vs Tempat Penayangan Iklan yang Paling Menarik')
        plt.xlabel('Tempat Penayangan Iklan yang Paling Menarik')
        plt.ylabel('Umur')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\umurXtempat_penayangan_iklan_atau_placement_yang_paling_menarik.png')

        return render(request, "hasil_segmentasi_fashion.html")
    except:
        messages.error(request, 'Data Tidak Tersedia')
        return redirect('fashion')

def hasil_segmentasi_makananresto(request):
    try:
        username = request.user.id
        obj = buat_survey_makanan_resto.objects.all().values()
        data = pd.DataFrame(obj)
        data=data[data['username'] == username]
        temp=data.drop(['id','username','responden_name'],axis=1)
        webapp=data.drop(['id','username','responden_name'],axis=1)
        umur = temp['umur']
        njai = []
        for i in range(0, len(umur), 1):
            if umur[i] == '<18 Tahun':
                njai.append(1)
            elif umur[i] == '18-23 Tahun':
                njai.append(2)
            elif umur[i] == '24-30 Tahun':
                njai.append(3)
            elif umur[i] == '31-35 Tahun':
                njai.append(4)
            elif umur[i] == '36-40 Tahun':
                njai.append(5)
            elif umur[i] == '41-45 Tahun':
                njai.append(6)
            elif umur[i] == '>45 Tahun':
                njai.append(7)
        temp['umur'] = pd.DataFrame(njai)

        umur = temp['pendapatan']
        njai = []
        for i in range(0, len(umur), 1):
            if umur[i] == '< Rp2.500.000':
                njai.append(1)
            elif umur[i] == 'Rp2.500.000 - Rp5.000.000':
                njai.append(2)
            elif umur[i] == 'Rp5.000.000 - Rp10.000.000':
                njai.append(3)
            elif umur[i] == 'Rp10.000.000 - Rp15.000.000':
                njai.append(4)
            elif umur[i] == 'Rp15.000.000 - Rp25.000.000':
                njai.append(5)
            elif umur[i] == '>Rp25.000.000':
                njai.append(6)
        temp['pendapatan'] = pd.DataFrame(njai)

        data = pd.get_dummies(temp)
        range_n_clusters = [2, 3]

        cost = []
        klust = []
        for klaster in range_n_clusters:
            clusterer = KModes(n_clusters=klaster, init='Huang', n_init=11, verbose=1)
            preds = clusterer.fit_predict(data)

            score = silhouette_score(data, preds)
            cost.append(score)
            klust.append(klaster)

        cost = pd.DataFrame(cost)
        cost.index = klust
        n_cluster = int(cost.idxmax())

        # define the k-modes model
        km = KModes(n_clusters=n_cluster, init='Huang', n_init=11, verbose=1)
        # fit the clusters to the skills dataframe
        clusters = km.fit_predict(data)
        # get an array of cluster modes
        kmodes = km.cluster_centroids_
        shape = kmodes.shape

        webapp['Segmen'] = clusters
        temp['Segmen'] = clusters
        urutan = np.sort(temp['Segmen'].unique())

        # pekerjaan squad
        # pekerjaan dan status menikah
        ybaru = ['Pelajar / Mahasiswa', 'Pekerja penuh waktu',
                 'Pekerja paruh waktu', 'Ibu Rumah Tangga', 'Sedang tidak bekerja',
                 'Pekerja profesional mandiri',
                 'Wirausaha', 'Pensiun']
        xbaru = ['Belum Menikah', 'Sudah Menikah, sudah mempunyai anak',
                 'Sudah Menikah, belum mempunyai anak']
        wehy = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        wehx = np.array([0, 1, 2])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['status'],
                        temp[temp['Segmen'] == urutan[i]]['pekerjaan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pekerjaan vs Status Perkawinan')
        plt.xlabel('Pekerjaan')
        plt.ylabel('Status Perkawinan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pekerjaanXstatus_menikah.png')

        # pekerjaan dan Pendapatan perbulan
        ybaru = ['Pelajar / Mahasiswa', 'Pekerja penuh waktu',
                 'Pekerja paruh waktu', 'Ibu Rumah Tangga', 'Sedang tidak bekerja',
                 'Pekerja profesional mandiri',
                 'Wirausaha', 'Pensiun']
        xbaru = ['< Rp2.500.000', 'Rp2.500.000 - Rp5.000.000', 'Rp5.000.000 - Rp10.000.000', 'Rp10.000.000 - Rp15.000.000',
                 'Rp15.000.000 - Rp25.000.000', '> Rp25.000.000']
        wehy = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        wehx = np.array([1, 2, 3, 4, 5, 6])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['pendapatan'],
                        temp[temp['Segmen'] == urutan[i]]['pekerjaan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pekerjaan vs Pendapatan perbulan')
        plt.xlabel('Pendapatan perbulan')
        plt.ylabel('Pekerjaan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pekerjaanXpendapatanperbulan.png')

        # pekerjaan dan umur
        ybaru = ['Pelajar / Mahasiswa', 'Pekerja penuh waktu',
                 'Pekerja paruh waktu', 'Ibu Rumah Tangga', 'Sedang tidak bekerja',
                 'Pekerja profesional mandiri',
                 'Wirausaha', 'Pensiun']
        xbaru = ['<18 tahun', '18 - 23 tahun', '24 - 30 tahun', '31 - 35 tahun', '36 - 40 tahun', '41 - 45 tahun',
                 '> 45 tahun']
        wehy = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        wehx = np.array([1, 2, 3, 4, 5, 6, 7])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['umur'],
                        temp[temp['Segmen'] == urutan[i]]['pekerjaan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pekerjaan vs Umur')
        plt.xlabel('Umur')
        plt.ylabel('Pekerjaan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pekerjaanXumur.png')


        # pendapatan perbulan squad
        # pendapatan perbulan dan status menikah
        ybaru = ['< Rp2.500.000', 'Rp2.500.000 - Rp5.000.000', 'Rp5.000.000 - Rp10.000.000', 'Rp10.000.000 - Rp15.000.000',
                 'Rp15.000.000 - Rp25.000.000', '> Rp25.000.000']
        xbaru = ['Belum Menikah', 'Sudah Menikah, sudah mempunyai anak',
                 'Sudah Menikah, belum mempunyai anak']
        wehy = np.array([1, 2, 3, 4, 5, 6])
        wehx = np.array([0, 1, 2])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['status'],
                        temp[temp['Segmen'] == urutan[i]]['pendapatan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pendapatan Perbulan vs Status Perkawinan')
        plt.xlabel('Pendapatan Perbulan')
        plt.ylabel('Status Perkawinan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pendapatanXstatus_menikah.png')

        # pendapatan perbulan dan umur
        xbaru = ['<18 tahun', '18 - 23 tahun', '24 - 30 tahun', '31 - 35 tahun', '36 - 40 tahun', '41 - 45 tahun',
                 '> 45 tahun']
        ybaru = ['< Rp2.500.000', 'Rp2.500.000 - Rp5.000.000', 'Rp5.000.000 - Rp10.000.000', 'Rp10.000.000 - Rp15.000.000',
                 'Rp15.000.000 - Rp25.000.000', '> Rp25.000.000']
        wehx = np.array([1, 2, 3, 4, 5, 6, 7])
        wehy = np.array([1, 2, 3, 4, 5, 6])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['umur'],
                        temp[temp['Segmen'] == urutan[i]]['pendapatan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pendapatan perbulan vs Umur')
        plt.xlabel('Umur')
        plt.ylabel('Pendapatan perbulan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pendapatanXumur.png')


        # Status perkawinan squad
        # Status perkawinan  dan umur
        xbaru = ['<18 tahun', '18 - 23 tahun', '24 - 30 tahun', '31 - 35 tahun', '36 - 40 tahun', '41 - 45 tahun',
                 '> 45 tahun']
        ybaru = ['Belum Menikah', 'Sudah Menikah, sudah mempunyai anak',
                 'Sudah Menikah, belum mempunyai anak']
        wehx = np.array([1, 2, 3, 4, 5, 6, 7])
        wehy = np.array([0, 1, 2])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['umur'],
                        temp[temp['Segmen'] == urutan[i]]['status'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Status perkawinan vs Umur')
        plt.xlabel('Umur')
        plt.ylabel('Status perkawinan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\status_menikahXumur.png')


        return render(request, "hasil_segmentasi_makananresto.html")
    except:
        messages.error(request, 'Data Tidak Tersedia')
        return redirect('makananresto')

def hasil_segmentasi_makanansaji(request):
    try:
        username = request.user.id
        obj = buat_survey_makanan_saji.objects.all().values()
        data = pd.DataFrame(obj)
        data=data[data['username'] == username]
        temp=data.drop(['id','username','responden_name'],axis=1)
        webapp=data.drop(['id','username','responden_name'],axis=1)
        umur = temp['umur']
        njai = []
        for i in range(0, len(umur), 1):
            if umur[i] == '<18 Tahun':
                njai.append(1)
            elif umur[i] == '18-23 Tahun':
                njai.append(2)
            elif umur[i] == '24-30 Tahun':
                njai.append(3)
            elif umur[i] == '31-35 Tahun':
                njai.append(4)
            elif umur[i] == '36-40 Tahun':
                njai.append(5)
            elif umur[i] == '41-45 Tahun':
                njai.append(6)
            elif umur[i] == '>45 Tahun':
                njai.append(7)
        temp['umur'] = pd.DataFrame(njai)

        umur = temp['pendapatan']
        njai = []
        for i in range(0, len(umur), 1):
            if umur[i] == '< Rp2.500.000':
                njai.append(1)
            elif umur[i] == 'Rp2.500.000 - Rp5.000.000':
                njai.append(2)
            elif umur[i] == 'Rp5.000.000 - Rp10.000.000':
                njai.append(3)
            elif umur[i] == 'Rp10.000.000 - Rp15.000.000':
                njai.append(4)
            elif umur[i] == 'Rp15.000.000 - Rp25.000.000':
                njai.append(5)
            elif umur[i] == '>Rp25.000.000':
                njai.append(6)
        temp['pendapatan'] = pd.DataFrame(njai)

        data = pd.get_dummies(temp)
        range_n_clusters = [2, 3]

        cost = []
        klust = []
        for klaster in range_n_clusters:
            clusterer = KModes(n_clusters=klaster, init='Huang', n_init=11, verbose=1)
            preds = clusterer.fit_predict(data)

            score = silhouette_score(data, preds)
            cost.append(score)
            klust.append(klaster)

        cost = pd.DataFrame(cost)
        cost.index = klust
        n_cluster = int(cost.idxmax())

        # define the k-modes model
        km = KModes(n_clusters=n_cluster, init='Huang', n_init=11, verbose=1)
        # fit the clusters to the skills dataframe
        clusters = km.fit_predict(data)
        # get an array of cluster modes
        kmodes = km.cluster_centroids_
        shape = kmodes.shape

        webapp['Segmen'] = clusters
        temp['Segmen'] = clusters
        urutan = np.sort(temp['Segmen'].unique())

        # pekerjaan squad
        # pekerjaan dan status menikah
        ybaru = ['Pelajar / Mahasiswa', 'Pekerja penuh waktu',
                 'Pekerja paruh waktu', 'Ibu Rumah Tangga', 'Sedang tidak bekerja',
                 'Pekerja profesional mandiri',
                 'Wirausaha', 'Pensiun']
        xbaru = ['Belum Menikah', 'Sudah Menikah, sudah mempunyai anak',
                 'Sudah Menikah, belum mempunyai anak']
        wehy = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        wehx = np.array([0, 1, 2])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['status'],
                        temp[temp['Segmen'] == urutan[i]]['pekerjaan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pekerjaan vs Status Perkawinan')
        plt.xlabel('Pekerjaan')
        plt.ylabel('Status Perkawinan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pekerjaanXstatus_menikah.png')

        # pekerjaan dan Pendapatan perbulan
        ybaru = ['Pelajar / Mahasiswa', 'Pekerja penuh waktu',
                 'Pekerja paruh waktu', 'Ibu Rumah Tangga', 'Sedang tidak bekerja',
                 'Pekerja profesional mandiri',
                 'Wirausaha', 'Pensiun']
        xbaru = ['< Rp2.500.000', 'Rp2.500.000 - Rp5.000.000', 'Rp5.000.000 - Rp10.000.000', 'Rp10.000.000 - Rp15.000.000',
                 'Rp15.000.000 - Rp25.000.000', '> Rp25.000.000']
        wehy = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        wehx = np.array([1, 2, 3, 4, 5, 6])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['pendapatan'],
                        temp[temp['Segmen'] == urutan[i]]['pekerjaan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pekerjaan vs Pendapatan perbulan')
        plt.xlabel('Pendapatan perbulan')
        plt.ylabel('Pekerjaan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pekerjaanXpendapatanperbulan.png')

        # pekerjaan dan umur
        ybaru = ['Pelajar / Mahasiswa', 'Pekerja penuh waktu',
                 'Pekerja paruh waktu', 'Ibu Rumah Tangga', 'Sedang tidak bekerja',
                 'Pekerja profesional mandiri',
                 'Wirausaha', 'Pensiun']
        xbaru = ['<18 tahun', '18 - 23 tahun', '24 - 30 tahun', '31 - 35 tahun', '36 - 40 tahun', '41 - 45 tahun',
                 '> 45 tahun']
        wehy = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        wehx = np.array([1, 2, 3, 4, 5, 6, 7])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['umur'],
                        temp[temp['Segmen'] == urutan[i]]['pekerjaan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pekerjaan vs Umur')
        plt.xlabel('Umur')
        plt.ylabel('Pekerjaan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pekerjaanXumur.png')


        # pendapatan perbulan squad
        # pendapatan perbulan dan status menikah
        ybaru = ['< Rp2.500.000', 'Rp2.500.000 - Rp5.000.000', 'Rp5.000.000 - Rp10.000.000', 'Rp10.000.000 - Rp15.000.000',
                 'Rp15.000.000 - Rp25.000.000', '> Rp25.000.000']
        xbaru = ['Belum Menikah', 'Sudah Menikah, sudah mempunyai anak',
                 'Sudah Menikah, belum mempunyai anak']
        wehy = np.array([1, 2, 3, 4, 5, 6])
        wehx = np.array([0, 1, 2])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['status'],
                        temp[temp['Segmen'] == urutan[i]]['pendapatan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pendapatan Perbulan vs Status Perkawinan')
        plt.xlabel('Pendapatan Perbulan')
        plt.ylabel('Status Perkawinan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pendapatanXstatus_menikah.png')

        # pendapatan perbulan dan umur
        xbaru = ['<18 tahun', '18 - 23 tahun', '24 - 30 tahun', '31 - 35 tahun', '36 - 40 tahun', '41 - 45 tahun',
                 '> 45 tahun']
        ybaru = ['< Rp2.500.000', 'Rp2.500.000 - Rp5.000.000', 'Rp5.000.000 - Rp10.000.000', 'Rp10.000.000 - Rp15.000.000',
                 'Rp15.000.000 - Rp25.000.000', '> Rp25.000.000']
        wehx = np.array([1, 2, 3, 4, 5, 6, 7])
        wehy = np.array([1, 2, 3, 4, 5, 6])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['umur'],
                        temp[temp['Segmen'] == urutan[i]]['pendapatan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pendapatan perbulan vs Umur')
        plt.xlabel('Umur')
        plt.ylabel('Pendapatan perbulan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pendapatanXumur.png')


        # Status perkawinan squad
        # Status perkawinan  dan umur
        xbaru = ['<18 tahun', '18 - 23 tahun', '24 - 30 tahun', '31 - 35 tahun', '36 - 40 tahun', '41 - 45 tahun',
                 '> 45 tahun']
        ybaru = ['Belum Menikah', 'Sudah Menikah, sudah mempunyai anak',
                 'Sudah Menikah, belum mempunyai anak']
        wehx = np.array([1, 2, 3, 4, 5, 6, 7])
        wehy = np.array([0, 1, 2])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['umur'],
                        temp[temp['Segmen'] == urutan[i]]['status'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Status perkawinan vs Umur')
        plt.xlabel('Umur')
        plt.ylabel('Status perkawinan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\status_menikahXumur.png')


        return render(request, "hasil_segmentasi_makanansaji.html")
    except:
        messages.error(request, 'Data Tidak Tersedia')
        return redirect('makanansaji')

def hasil_segmentasi_makananlayanantar(request):
    try:
        username = request.user.id
        obj = buat_survey_makanan_layan_antar.objects.all().values()
        data = pd.DataFrame(obj)
        data=data[data['username'] == username]
        temp=data.drop(['id','username','responden_name'],axis=1)
        webapp=data.drop(['id','username','responden_name'],axis=1)
        umur = temp['umur']
        njai = []
        for i in range(0, len(umur), 1):
            if umur[i] == '<18 Tahun':
                njai.append(1)
            elif umur[i] == '18-23 Tahun':
                njai.append(2)
            elif umur[i] == '24-30 Tahun':
                njai.append(3)
            elif umur[i] == '31-35 Tahun':
                njai.append(4)
            elif umur[i] == '36-40 Tahun':
                njai.append(5)
            elif umur[i] == '41-45 Tahun':
                njai.append(6)
            elif umur[i] == '>45 Tahun':
                njai.append(7)
        temp['umur'] = pd.DataFrame(njai)

        umur = temp['pendapatan']
        njai = []
        for i in range(0, len(umur), 1):
            if umur[i] == '< Rp2.500.000':
                njai.append(1)
            elif umur[i] == 'Rp2.500.000 - Rp5.000.000':
                njai.append(2)
            elif umur[i] == 'Rp5.000.000 - Rp10.000.000':
                njai.append(3)
            elif umur[i] == 'Rp10.000.000 - Rp15.000.000':
                njai.append(4)
            elif umur[i] == 'Rp15.000.000 - Rp25.000.000':
                njai.append(5)
            elif umur[i] == '>Rp25.000.000':
                njai.append(6)
        temp['pendapatan'] = pd.DataFrame(njai)

        data = pd.get_dummies(temp)
        range_n_clusters = [2, 3]

        cost = []
        klust = []
        for klaster in range_n_clusters:
            clusterer = KModes(n_clusters=klaster, init='Huang', n_init=11, verbose=1)
            preds = clusterer.fit_predict(data)

            score = silhouette_score(data, preds)
            cost.append(score)
            klust.append(klaster)

        cost = pd.DataFrame(cost)
        cost.index = klust
        n_cluster = int(cost.idxmax())

        # define the k-modes model
        km = KModes(n_clusters=n_cluster, init='Huang', n_init=11, verbose=1)
        # fit the clusters to the skills dataframe
        clusters = km.fit_predict(data)
        # get an array of cluster modes
        kmodes = km.cluster_centroids_
        shape = kmodes.shape

        webapp['Segmen'] = clusters
        temp['Segmen'] = clusters
        urutan = np.sort(temp['Segmen'].unique())

        # pekerjaan squad
        # pekerjaan dan status menikah
        ybaru = ['Pelajar / Mahasiswa', 'Pekerja penuh waktu',
                 'Pekerja paruh waktu', 'Ibu Rumah Tangga', 'Sedang tidak bekerja',
                 'Pekerja profesional mandiri',
                 'Wirausaha', 'Pensiun']
        xbaru = ['Belum Menikah', 'Sudah Menikah, sudah mempunyai anak',
                 'Sudah Menikah, belum mempunyai anak']
        wehy = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        wehx = np.array([0, 1, 2])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['status'],
                        temp[temp['Segmen'] == urutan[i]]['pekerjaan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pekerjaan vs Status Perkawinan')
        plt.xlabel('Pekerjaan')
        plt.ylabel('Status Perkawinan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pekerjaanXstatus_menikah.png')

        # pekerjaan dan Pendapatan perbulan
        ybaru = ['Pelajar / Mahasiswa', 'Pekerja penuh waktu',
                 'Pekerja paruh waktu', 'Ibu Rumah Tangga', 'Sedang tidak bekerja',
                 'Pekerja profesional mandiri',
                 'Wirausaha', 'Pensiun']
        xbaru = ['< Rp2.500.000', 'Rp2.500.000 - Rp5.000.000', 'Rp5.000.000 - Rp10.000.000', 'Rp10.000.000 - Rp15.000.000',
                 'Rp15.000.000 - Rp25.000.000', '> Rp25.000.000']
        wehy = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        wehx = np.array([1, 2, 3, 4, 5, 6])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['pendapatan'],
                        temp[temp['Segmen'] == urutan[i]]['pekerjaan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pekerjaan vs Pendapatan perbulan')
        plt.xlabel('Pendapatan perbulan')
        plt.ylabel('Pekerjaan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pekerjaanXpendapatanperbulan.png')

        # pekerjaan dan umur
        ybaru = ['Pelajar / Mahasiswa', 'Pekerja penuh waktu',
                 'Pekerja paruh waktu', 'Ibu Rumah Tangga', 'Sedang tidak bekerja',
                 'Pekerja profesional mandiri',
                 'Wirausaha', 'Pensiun']
        xbaru = ['<18 tahun', '18 - 23 tahun', '24 - 30 tahun', '31 - 35 tahun', '36 - 40 tahun', '41 - 45 tahun',
                 '> 45 tahun']
        wehy = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        wehx = np.array([1, 2, 3, 4, 5, 6, 7])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['umur'],
                        temp[temp['Segmen'] == urutan[i]]['pekerjaan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pekerjaan vs Umur')
        plt.xlabel('Umur')
        plt.ylabel('Pekerjaan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pekerjaanXumur.png')


        # pendapatan perbulan squad
        # pendapatan perbulan dan status menikah
        ybaru = ['< Rp2.500.000', 'Rp2.500.000 - Rp5.000.000', 'Rp5.000.000 - Rp10.000.000', 'Rp10.000.000 - Rp15.000.000',
                 'Rp15.000.000 - Rp25.000.000', '> Rp25.000.000']
        xbaru = ['Belum Menikah', 'Sudah Menikah, sudah mempunyai anak',
                 'Sudah Menikah, belum mempunyai anak']
        wehy = np.array([1, 2, 3, 4, 5, 6])
        wehx = np.array([0, 1, 2])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['status'],
                        temp[temp['Segmen'] == urutan[i]]['pendapatan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pendapatan Perbulan vs Status Perkawinan')
        plt.xlabel('Pendapatan Perbulan')
        plt.ylabel('Status Perkawinan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pendapatanXstatus_menikah.png')

        # pendapatan perbulan dan umur
        xbaru = ['<18 tahun', '18 - 23 tahun', '24 - 30 tahun', '31 - 35 tahun', '36 - 40 tahun', '41 - 45 tahun',
                 '> 45 tahun']
        ybaru = ['< Rp2.500.000', 'Rp2.500.000 - Rp5.000.000', 'Rp5.000.000 - Rp10.000.000', 'Rp10.000.000 - Rp15.000.000',
                 'Rp15.000.000 - Rp25.000.000', '> Rp25.000.000']
        wehx = np.array([1, 2, 3, 4, 5, 6, 7])
        wehy = np.array([1, 2, 3, 4, 5, 6])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['umur'],
                        temp[temp['Segmen'] == urutan[i]]['pendapatan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pendapatan perbulan vs Umur')
        plt.xlabel('Umur')
        plt.ylabel('Pendapatan perbulan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pendapatanXumur.png')


        # Status perkawinan squad
        # Status perkawinan  dan umur
        xbaru = ['<18 tahun', '18 - 23 tahun', '24 - 30 tahun', '31 - 35 tahun', '36 - 40 tahun', '41 - 45 tahun',
                 '> 45 tahun']
        ybaru = ['Belum Menikah', 'Sudah Menikah, sudah mempunyai anak',
                 'Sudah Menikah, belum mempunyai anak']
        wehx = np.array([1, 2, 3, 4, 5, 6, 7])
        wehy = np.array([0, 1, 2])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['umur'],
                        temp[temp['Segmen'] == urutan[i]]['status'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Status perkawinan vs Umur')
        plt.xlabel('Umur')
        plt.ylabel('Status perkawinan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\status_menikahXumur.png')


        return render(request, "hasil_segmentasi_makananlayanantar.html")
    except:
        messages.error(request, 'Data Tidak Tersedia')
        return redirect('makananlayanantar')

def hasil_segmentasi_makananpenyediasaja(request):
    try:
        username = request.user.id
        obj = buat_survey_makanan_penyedia_jasa.objects.all().values()
        data = pd.DataFrame(obj)
        data=data[data['username'] == username]
        temp=data.drop(['id','username','responden_name'],axis=1)
        webapp=data.drop(['id','username','responden_name'],axis=1)
        umur = temp['umur']
        njai = []
        for i in range(0, len(umur), 1):
            if umur[i] == '<18 Tahun':
                njai.append(1)
            elif umur[i] == '18-23 Tahun':
                njai.append(2)
            elif umur[i] == '24-30 Tahun':
                njai.append(3)
            elif umur[i] == '31-35 Tahun':
                njai.append(4)
            elif umur[i] == '36-40 Tahun':
                njai.append(5)
            elif umur[i] == '41-45 Tahun':
                njai.append(6)
            elif umur[i] == '>45 Tahun':
                njai.append(7)
        temp['umur'] = pd.DataFrame(njai)

        umur = temp['pendapatan']
        njai = []
        for i in range(0, len(umur), 1):
            if umur[i] == '< Rp2.500.000':
                njai.append(1)
            elif umur[i] == 'Rp2.500.000 - Rp5.000.000':
                njai.append(2)
            elif umur[i] == 'Rp5.000.000 - Rp10.000.000':
                njai.append(3)
            elif umur[i] == 'Rp10.000.000 - Rp15.000.000':
                njai.append(4)
            elif umur[i] == 'Rp15.000.000 - Rp25.000.000':
                njai.append(5)
            elif umur[i] == '>Rp25.000.000':
                njai.append(6)
        temp['pendapatan'] = pd.DataFrame(njai)

        data = pd.get_dummies(temp)
        range_n_clusters = [2, 3]

        cost = []
        klust = []
        for klaster in range_n_clusters:
            clusterer = KModes(n_clusters=klaster, init='Huang', n_init=11, verbose=1)
            preds = clusterer.fit_predict(data)

            score = silhouette_score(data, preds)
            cost.append(score)
            klust.append(klaster)

        cost = pd.DataFrame(cost)
        cost.index = klust
        n_cluster = int(cost.idxmax())

        # define the k-modes model
        km = KModes(n_clusters=n_cluster, init='Huang', n_init=11, verbose=1)
        # fit the clusters to the skills dataframe
        clusters = km.fit_predict(data)
        # get an array of cluster modes
        kmodes = km.cluster_centroids_
        shape = kmodes.shape

        webapp['Segmen'] = clusters
        temp['Segmen'] = clusters
        urutan = np.sort(temp['Segmen'].unique())

        # pekerjaan squad
        # pekerjaan dan status menikah
        ybaru = ['Pelajar / Mahasiswa', 'Pekerja penuh waktu',
                 'Pekerja paruh waktu', 'Ibu Rumah Tangga', 'Sedang tidak bekerja',
                 'Pekerja profesional mandiri',
                 'Wirausaha', 'Pensiun']
        xbaru = ['Belum Menikah', 'Sudah Menikah, sudah mempunyai anak',
                 'Sudah Menikah, belum mempunyai anak']
        wehy = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        wehx = np.array([0, 1, 2])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['status'],
                        temp[temp['Segmen'] == urutan[i]]['pekerjaan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pekerjaan vs Status Perkawinan')
        plt.xlabel('Pekerjaan')
        plt.ylabel('Status Perkawinan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pekerjaanXstatus_menikah.png')

        # pekerjaan dan Pendapatan perbulan
        ybaru = ['Pelajar / Mahasiswa', 'Pekerja penuh waktu',
                 'Pekerja paruh waktu', 'Ibu Rumah Tangga', 'Sedang tidak bekerja',
                 'Pekerja profesional mandiri',
                 'Wirausaha', 'Pensiun']
        xbaru = ['< Rp2.500.000', 'Rp2.500.000 - Rp5.000.000', 'Rp5.000.000 - Rp10.000.000', 'Rp10.000.000 - Rp15.000.000',
                 'Rp15.000.000 - Rp25.000.000', '> Rp25.000.000']
        wehy = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        wehx = np.array([1, 2, 3, 4, 5, 6])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['pendapatan'],
                        temp[temp['Segmen'] == urutan[i]]['pekerjaan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pekerjaan vs Pendapatan perbulan')
        plt.xlabel('Pendapatan perbulan')
        plt.ylabel('Pekerjaan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pekerjaanXpendapatanperbulan.png')

        # pekerjaan dan umur
        ybaru = ['Pelajar / Mahasiswa', 'Pekerja penuh waktu',
                 'Pekerja paruh waktu', 'Ibu Rumah Tangga', 'Sedang tidak bekerja',
                 'Pekerja profesional mandiri',
                 'Wirausaha', 'Pensiun']
        xbaru = ['<18 tahun', '18 - 23 tahun', '24 - 30 tahun', '31 - 35 tahun', '36 - 40 tahun', '41 - 45 tahun',
                 '> 45 tahun']
        wehy = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        wehx = np.array([1, 2, 3, 4, 5, 6, 7])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['umur'],
                        temp[temp['Segmen'] == urutan[i]]['pekerjaan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pekerjaan vs Umur')
        plt.xlabel('Umur')
        plt.ylabel('Pekerjaan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pekerjaanXumur.png')


        # pendapatan perbulan squad
        # pendapatan perbulan dan status menikah
        ybaru = ['< Rp2.500.000', 'Rp2.500.000 - Rp5.000.000', 'Rp5.000.000 - Rp10.000.000', 'Rp10.000.000 - Rp15.000.000',
                 'Rp15.000.000 - Rp25.000.000', '> Rp25.000.000']
        xbaru = ['Belum Menikah', 'Sudah Menikah, sudah mempunyai anak',
                 'Sudah Menikah, belum mempunyai anak']
        wehy = np.array([1, 2, 3, 4, 5, 6])
        wehx = np.array([0, 1, 2])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['status'],
                        temp[temp['Segmen'] == urutan[i]]['pendapatan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pendapatan Perbulan vs Status Perkawinan')
        plt.xlabel('Pendapatan Perbulan')
        plt.ylabel('Status Perkawinan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pendapatanXstatus_menikah.png')

        # pendapatan perbulan dan umur
        xbaru = ['<18 tahun', '18 - 23 tahun', '24 - 30 tahun', '31 - 35 tahun', '36 - 40 tahun', '41 - 45 tahun',
                 '> 45 tahun']
        ybaru = ['< Rp2.500.000', 'Rp2.500.000 - Rp5.000.000', 'Rp5.000.000 - Rp10.000.000', 'Rp10.000.000 - Rp15.000.000',
                 'Rp15.000.000 - Rp25.000.000', '> Rp25.000.000']
        wehx = np.array([1, 2, 3, 4, 5, 6, 7])
        wehy = np.array([1, 2, 3, 4, 5, 6])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['umur'],
                        temp[temp['Segmen'] == urutan[i]]['pendapatan'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Pendapatan perbulan vs Umur')
        plt.xlabel('Umur')
        plt.ylabel('Pendapatan perbulan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\pendapatanXumur.png')


        # Status perkawinan squad
        # Status perkawinan  dan umur
        xbaru = ['<18 tahun', '18 - 23 tahun', '24 - 30 tahun', '31 - 35 tahun', '36 - 40 tahun', '41 - 45 tahun',
                 '> 45 tahun']
        ybaru = ['Belum Menikah', 'Sudah Menikah, sudah mempunyai anak',
                 'Sudah Menikah, belum mempunyai anak']
        wehx = np.array([1, 2, 3, 4, 5, 6, 7])
        wehy = np.array([0, 1, 2])
        plt.figure(figsize=(30, 8))
        for i in range(0, len(urutan), 1):
            plt.scatter(temp[temp['Segmen'] == urutan[i]]['umur'],
                        temp[temp['Segmen'] == urutan[i]]['status'],
                        label=urutan[i])
        plt.xticks(wehx, xbaru)
        plt.yticks(wehy, ybaru)
        plt.title('Status perkawinan vs Umur')
        plt.xlabel('Umur')
        plt.ylabel('Status perkawinan')
        plt.legend()
        plt.savefig('D:\\Projek WebApp\\web1\\web1\\static\\images\\status_menikahXumur.png')


        return render(request, "hasil_segmentasi_makananpenyediasaja.html")
    except:
        messages.error(request, 'Data Tidak Tersedia')
        return redirect('makananpenyediasaja')