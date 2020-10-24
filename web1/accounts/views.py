from django.shortcuts import render, redirect
from django.contrib import messages
from travello.models import akses_kode
from django.contrib.auth.models import User, auth

# Create your views here.

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request,user)
            return redirect('/owner')
            #elif user.last_name == 'Fashion':
                #return redirect('/fashion')
            #elif user.last_name == 'Makanan - restoran & pesan antar':
                #return redirect('/makananresto')
            #elif user.last_name == 'Makanan - saji di tempat saja':
                #return redirect('/makanansaji')
            #elif user.last_name == 'Makanan - layan antar saja':
                #return redirect('/makananlayanantar')
            #elif user.last_name == 'Makanan - penyedia saja (layan antar oleh Gojek/Grab)':
                #return redirect('/makananpenyediasaja')
        else:
            messages.error(request, 'Username atau Password Salah')
            return redirect('login')

    else:
        return render(request, "login.html")
def signup(request):
    if request.method=='POST':
        first_name = request.POST['business_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        last_name = request.POST['tipe_bisnis']

        if first_name == "" or username == "" or email == "" or password == "" or last_name == "":
            messages.error(request, 'Form Tidak Boleh Kosong')
            return redirect('signup')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username Sudah Ada')
            return redirect('signup')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email Sudah Ada')
            return redirect('signup')
        else:
            user = User.objects.create_user(username=username,password=password,email=email,first_name=first_name,last_name=last_name)
            user.save();
            print('user created')
            return redirect('login')

    else:
        return render(request, "testingsignup.html")
