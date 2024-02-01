from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from .forms import UserForm


def signup(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password, first_name=first_name, last_name=last_name)
            login(request, user)
            return redirect('index')
    else:
        form = UserForm()
    return render(request, 'common/signup.html', {'form': form})

def page_not_found(request, exception):
    return render(request, 'common/404.html', {})