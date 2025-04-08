from django.shortcuts import render, redirect
from django.urls import reverse, NoReverseMatch
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from bocaboca_profile.models import NewUser


def index(request):
    try:
        profissional_url = reverse('profissional', args=['eletricista'])
    except NoReverseMatch as e:
        profissional_url = str(e)
    
    return render(request, 'bocaboca/pages/index.html', {
        'profissional_url': profissional_url,
    })

def profissional_sem_categoria(request):
    return render(request, 'bocaboca/pages/profissional.html', {'categoria': None})


def profissional_view(request, categoria):
    return render(request, 'bocaboca/pages/profissional.html', {'categoria': categoria})

def register_view(request):
    """
    View responsável por renderizar o template de registro.
    """
    if request.method == 'POST':
        # Lógica para processar o formulário, se necessário
        # Por exemplo: validação, criação de usuário, etc.
        pass

    return render(request, 'bocaboca/pages/register.html')

def login(request):
    return render(request, 'bocaboca/pages/login.html')

def profile(request):
    return render(request, 'bocaboca/pages/profile.html')

@login_required
def submit_profile(request):
    if request.method == 'POST':
        user = request.user
        name = request.POST.get('name')
        nickname = request.POST.get('nickname')
        professional_title = request.POST.get('professional_title')
        about = request.POST.get('about')
        professional_experience = request.POST.get('professional_experience')
        ability = request.POST.get('ability')
        interest_area_ids = request.POST.getlist('interest_areas')  # IDs são esperados aqui como strings numéricas

        newUser, created = NewUser.objects.update_or_create(
            user=user,
            defaults={
                'name': name,
                'nickname': nickname,
                'professional_title': professional_title,
                'about': about,
                'professional_experience': professional_experience,
                'ability': ability
            }
        )

        # Atualizar as áreas de interesse usando os IDs
        if interest_area_ids:
            newUser.interest_areas.clear()
            newUser.interest_areas.add(*[InterestArea.objects.get(id=int(area_id)) for area_id in interest_area_ids if area_id.isdigit()])

        messages.success(request, 'Perfil cadastrado com sucesso!')
        return HttpResponse("Perfil cadastrado com sucesso!")
    else:
        return render(request, 'nome_do_template.html')

