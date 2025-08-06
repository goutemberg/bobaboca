from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import PendingUser, NewUser
from django.http import HttpResponseBadRequest, HttpResponse
from django.contrib.auth import login
from django.utils.crypto import get_random_string


def create_username(full_name):
    cleaned_name = '-'.join(full_name.strip().split())
    username = f"{cleaned_name}-{get_random_string(5)}"
    return username

def send_activation_link(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")  # Aqui vamos pegar o role que foi enviado no formulário

        if not all([full_name, email, password, role]):
            return HttpResponseBadRequest("Todos os campos são obrigatórios.")
        
        # Criar o usuário
        username = create_username(full_name)
        user = User.objects.create_user(username=username, email=email, password=password, first_name=full_name)
        user.is_active = False
        user.save()

        # Criar o token de ativação e registrar o usuário pendente
        activation_key = get_random_string(64)
        while PendingUser.objects.filter(token=activation_key).exists():
            activation_key = get_random_string(64)

        PendingUser.objects.create(user=user, token=activation_key, nickname=username, user_type=role)

        # Gerar o link de ativação
        activation_url = f"http://localhost:8000/activate/{activation_key}/"

        # Enviar e-mail de ativação
        send_activation_email(user, activation_url)
        
        return redirect('bocaboca_profile:activation_success')

    return render(request, 'bocaboca/pages/register.html')


def send_activation_email(user, activation_url):
    full_name = user.first_name
    email = user.email
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
            </style>
        </head>
        <body>
            <div class="email-container">
                <h1>Ativação de Conta</h1>
                <p>Olá {full_name},</p>
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

        # Redireciona para a página de edição de perfil com base no tipo de usuário
        if pending_user.user_type == 'contratar':
            return redirect('bocaboca_profile:new_client', username=user.username)
        elif pending_user.user_type == 'trabalhar':
            return redirect('bocaboca_profile:new_user', username=user.username)

    return HttpResponseBadRequest("Token inválido ou já utilizado.")

def new_user(request, username):
    user = get_object_or_404(User, username=username)
    new_user, created = NewUser.objects.get_or_create(user=user)

    if request.method == 'POST':
        new_user.name = request.POST.get('name', new_user.name)
        new_user.nickname = request.POST.get('nickname', new_user.nickname)
        new_user.professional_title = request.POST.get('professional_title', new_user.professional_title)
        new_user.about = request.POST.get('about', new_user.about)
        new_user.professional_experience = request.POST.get('professional_experience', new_user.professional_experience)
        
        # Captura as áreas de interesse se necessário
        interest_area_labels = request.POST.getlist('interest_areas')
        new_user.interest_areas = ",".join(interest_area_labels)

        new_user.ability = request.POST.get('ability', new_user.ability)
        new_user.save()

        return redirect('bocaboca_profile:dashboard')  # Ou qualquer outro redirecionamento desejado

    context = {
        'user': user,
        'profile': new_user,
        'nickname': request.session.get('nickname', user.username),
        'full_name': request.session.get('full_name', user.first_name)
    }
    return render(request, 'bocaboca/pages/profile.html', context)

def new_client(request, username):
    user = get_object_or_404(User, username=username)
    new_client, created = NewUser.objects.get_or_create(user=user)

    if request.method == 'POST':
        new_client.name = request.POST.get('name', new_client.name)
        new_client.nickname = request.POST.get('nickname', new_client.nickname)
        new_client.professional_title = request.POST.get('professional_title', new_client.professional_title)
        new_client.about = request.POST.get('about', new_client.about)
        new_client.professional_experience = request.POST.get('professional_experience', new_client.professional_experience)
        
        # Captura as áreas de interesse se necessário
        interest_area_labels = request.POST.getlist('interest_areas')
        new_client.interest_areas = ",".join(interest_area_labels)

        new_client.ability = request.POST.get('ability', new_client.ability)
        new_client.save()

        return redirect('bocaboca_profile:dashboard')  # Ou qualquer outro redirecionamento desejado

    context = {
        'user': user,
        'profile': new_client,
        'nickname': request.session.get('nickname', user.username),
        'full_name': request.session.get('full_name', user.first_name)
    }
    return render(request, 'bocaboca/pages/profile.html', context)

def role_selection(request):
    if request.method == "POST":
        role = request.POST.get("role")

        # Armazenar o valor de role na sessão
        request.session['role'] = role

        # Redireciona para o próximo passo (a página de cadastro)
        return redirect('bocaboca:client')
    return render(request, 'bocaboca/pages/register.html')

