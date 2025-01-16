from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import PendingUser, NewUser, InterestArea
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseRedirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.db import transaction



def create_username(full_name):
    # Remove espaços extras e substitui espaços por hífens
    cleaned_name = '-'.join(full_name.strip().split())
    # Adiciona uma string aleatória no final
    username = f"{cleaned_name}-{get_random_string(5)}"
    return username

def send_activation_link(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        if not all([full_name, email, password]):
            return HttpResponseBadRequest("Todos os campos são obrigatórios.")
        
        username = create_username(full_name)
        user = User.objects.create_user(username=username, email=email, password=password, first_name=full_name)
        user.is_active = False
        user.save()

        activation_key = get_random_string(64)
        while PendingUser.objects.filter(token=activation_key).exists():
            activation_key = get_random_string(64)
        
        PendingUser.objects.create(user=user, token=activation_key, nickname=username)

        activation_url = f"http://localhost:8000/activate/{activation_key}/"
        
        text_content = f"""
        Olá {full_name},
        
        Obrigado por se registrar! Use o link abaixo para ativar sua conta:
        {activation_url}
        
        Este link expira em 24 horas.
        
        Se você não solicitou este e-mail, por favor ignore.
        """

        html_content = f"""
        <html>
            <head>
                <meta charset="UTF-8">
                <title>Ativação de Conta</title>
                <style>
                    body {{ font-family: Arial, sans-serif; background-color: #f8f9fa; color: #333; }}
                    .email-container {{ width: 100%; max-width: 600px; margin: 20px auto; padding: 20px; background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
                    h1 {{ color: #007bff; }}
                    a {{ color: #ffffff; background-color: #007bff; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
                    p {{ line-height: 1.5; font-size: 16px; }}
                    .footer {{ background-color: #f8f9fa; text-align: center; padding: 10px; font-size: 12px; color: #666; }}
                    .uppercase {{ text-transform: uppercase; }}
                </style>
            </head>
            <body>
                <div class="email-container">
                    <h1>Ativação de Conta</h1>
                    <p>Olá <span class="uppercase">{full_name}</span>,</p>
                    <p>Obrigado por se registrar! Por favor, clique no link abaixo para ativar sua conta:</p>
                    <p><a href="{activation_url}">Ativar Conta</a></p>
                    <p>Este link expira em 24 horas.</p>
                    <p>Se você não solicitou este e-mail, por favor ignore-o.</p>
                </div>
                <div class="footer">
                    <p>Se por algum motivo não conseguir ativar a sua conta, fale com a nossa equipe: suporte@bocaboca.com.br.</p>
                </div>
            </body>
        </html>
        """

        send_mail(
            "Ative sua conta",
            text_content,
            "noreply@example.com",
            [email],
            html_message=html_content
        )
        
        request.session['activation_email'] = email
        return redirect('bocaboca_profile:activation_success')
    else:
        return render(request, 'bocaboca/pages/register.html')
    

def complete_registration(request, activation_key):
    pending_user = get_object_or_404(PendingUser, token=activation_key)

    if pending_user.token_expired():
        return HttpResponseBadRequest("Token de ativação expirado.")

    user = pending_user.user
    if not user.is_active:
        user.is_active = True
        user.save()
        login(request, user)  # Faz login automático após a ativação
        request.session['nickname'] = pending_user.nickname
        request.session['full_name'] = user.first_name

        pending_user.delete()  # Limpa o registro pendente após a ativação

        # Redireciona para a página de edição de perfil
        return redirect('bocaboca_profile:edit_new_user', username=user.username)

    return HttpResponseBadRequest("Token inválido ou já utilizado.")


def activation_success(request):
    email = request.session.get('activation_email', 'no email provided')
    return render(request, 'bocaboca/pages/activation_success.html', {'email': email})


@login_required
def handle_profile_submission(request):
    if request.method == 'POST':
        user = request.user
        try:
            with transaction.atomic():  # Garante que toda a operação é atômica
                newUser, created = NewUser.objects.get_or_create(user=user)
                newUser.name = request.POST.get('name', newUser.name)
                newUser.nickname = request.POST.get('nickname', newUser.nickname)
                newUser.professional_title = request.POST.get('professional_title', newUser.professional_title)
                newUser.about = request.POST.get('about', newUser.about)
                newUser.professional_experience = request.POST.get('professional_experience', newUser.professional_experience)
                
                # Capturando os rótulos das áreas de interesse como uma string
                interest_area_labels = request.POST.getlist('interest_areas')
                newUser.interest_areas = ",".join(interest_area_labels)

                newUser.ability = request.POST.get('ability', newUser.ability)
                newUser.save()

            return redirect('bocaboca_profile:dashboard') 
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")
            return HttpResponse(f"Error processing your request: {e}", status=500)
    else:
        return HttpResponse("Invalid request", status=400)
    

def edit_new_user(request, username):
    user = get_object_or_404(User, username=username)
    newuser, created = NewUser.objects.get_or_create(user=user)

    if request.method == 'POST':
        if handle_profile_submission(request, user):
            return HttpResponseRedirect(f'/edit_new_user/{username}/')
        else:
            context = {
                'user': user,
                'profile': newuser,
                'error': 'Erro ao salvar o perfil.'
            }
            return render(request, 'bocaboca/pages/profile.html', context)
    else:
        context = {
            'user': user,
            'profile': newuser,
            'nickname': request.session.get('nickname', user.username),
            'full_name': request.session.get('full_name', user.first_name)
        }
        return render(request, 'bocaboca/pages/profile.html', context)

@login_required(login_url='/')
def dashboard(request):
    # Example context data
    context = {
        'username': request.user.username,
        'earnings': 0.00,  # Example static data
        'projects': [],  # This could be dynamic, fetched from your database
        'proposals': []
    }
    return render(request, 'bocaboca/pages/dashboard.html', context)