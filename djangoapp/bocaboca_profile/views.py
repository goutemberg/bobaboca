from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import PendingUser, NewUser
from django.http import HttpResponseBadRequest
from django.contrib.auth import login
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json


def create_username(full_name):
    cleaned_name = '-'.join(full_name.strip().split())
    username = f"{cleaned_name}-{get_random_string(5)}"
    return username


def send_activation_link(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")

        if not all([full_name, email, password, role]):
            return HttpResponseBadRequest("Todos os campos são obrigatórios.")
        
        username = create_username(full_name)
        user = User.objects.create_user(username=username, email=email, password=password, first_name=full_name)
        user.is_active = False
        user.save()

        activation_key = get_random_string(64)
        while PendingUser.objects.filter(token=activation_key).exists():
            activation_key = get_random_string(64)

        PendingUser.objects.create(user=user, token=activation_key, nickname=username, user_type=role)

        activation_url = f"http://localhost:8000/activate/{activation_key}/"
        send_activation_email(user, activation_url)

        # ✅ Redireciona com email como query param para a tela de sucesso
        return redirect(f"{reverse('bocaboca_profile:activation_success')}?email={email}")

    return render(request, 'bocaboca/pages/register.html')


def send_activation_email(user, activation_url):
    full_name = user.first_name
    email = user.email
    text_content = f"""
    Olá {full_name},

    Obrigado por se registrar! Use o link abaixo para ativar sua conta:
    {activation_url}

    Este link expira em 24 horas.
    """

    html_content = f"""
<html>
  <body style="margin:0; padding:0; font-family:Arial, sans-serif; background-color:#f4f4f4;">
    <table width="100%" bgcolor="#f4f4f4" cellpadding="0" cellspacing="0">
      <tr>
        <td align="center">
          <table width="600" cellpadding="40" cellspacing="0" bgcolor="#ffffff" style="margin-top: 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
            <tr>
              <td align="center" style="color:#007bff;">
                <h1>Ativação de Conta</h1>
              </td>
            </tr>
            <tr>
              <td style="color:#333333; font-size:16px; line-height:1.6;">
                <p>Olá <strong>{full_name}</strong>,</p>
                <p>Obrigado por se registrar! Por favor, clique no botão abaixo para ativar sua conta:</p>
                <p style="text-align: center; margin: 30px 0;">
                  <a href="{activation_url}" style="background-color:#007bff; color:#ffffff; text-decoration:none; padding: 12px 24px; border-radius:5px; display:inline-block;">
                    Ativar Conta
                  </a>
                </p>
                <p>Este link expira em 24 horas.</p>
                <p>Se você não solicitou este e-mail, por favor ignore-o.</p>
              </td>
            </tr>
            <tr>
              <td align="center" style="padding-top:30px; font-size:14px; color:#666;">
                Se por algum motivo não conseguir ativar a sua conta, fale com a nossa equipe: <br>
                <a href="mailto:suporte@bocaboca.com.br" style="color:#007bff;">suporte@bocaboca.com.br</a>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""


    send_mail(
    "Ative sua conta",
    text_content,
    None,
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
        login(request, user)
        request.session['nickname'] = pending_user.nickname
        request.session['full_name'] = user.first_name

        pending_user.delete()

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
        new_user.interest_areas = ",".join(request.POST.getlist('interest_areas'))
        new_user.ability = request.POST.get('ability', new_user.ability)
        new_user.save()

        return redirect('bocaboca_profile:dashboard')

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
        new_client.interest_areas = ",".join(request.POST.getlist('interest_areas'))
        new_client.ability = request.POST.get('ability', new_client.ability)
        new_client.save()

        return redirect('bocaboca_profile:dashboard')

    context = {
        'user': user,
        'profile': new_client,
        'nickname': request.session.get('nickname', user.username),
        'full_name': request.session.get('full_name', user.first_name)
    }
    return render(request, 'bocaboca/pages/profile.html', context)


def activation_success(request):
    email = request.GET.get('email', '')
    return render(request, 'bocaboca/pages/activation_success.html', {'email': email})


def activation_client_success(request):
    email = request.GET.get('email', '')
    return render(request, 'bocaboca/pages/activation_success.html', {'email': email})


def dashboard(request):
    return render(request, 'bocaboca/pages/dashboard.html')


def role_selection(request):
    if request.method == "POST":
        role = request.POST.get("role")
        request.session['role'] = role
        return redirect('bocaboca:client')
    return render(request, 'bocaboca/pages/register.html')

@require_http_methods(["GET", "POST"])
def edit_new_user(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(NewUser, user=user)

    if request.method == 'POST':
        profile.name = request.POST.get('name', profile.name)
        profile.nickname = request.POST.get('nickname', profile.nickname)
        profile.professional_title = request.POST.get('professional_title', profile.professional_title)
        profile.about = request.POST.get('about', profile.about)
        profile.professional_experience = request.POST.get('professional_experience', profile.professional_experience)
        profile.interest_areas = ",".join(request.POST.getlist('interest_areas'))
        profile.ability = request.POST.get('ability', profile.ability)
        profile.save()
        return redirect('bocaboca_profile:dashboard')

    context = {
        'user': user,
        'profile': profile,
        'nickname': profile.nickname,
        'full_name': profile.name
    }
    return render(request, 'bocaboca/pages/profile_edit.html', context)


@require_http_methods(["GET", "POST"])
def edit_new_client(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(NewUser, user=user)

    if request.method == 'POST':
        profile.name = request.POST.get('name', profile.name)
        profile.nickname = request.POST.get('nickname', profile.nickname)
        profile.professional_title = request.POST.get('professional_title', profile.professional_title)
        profile.about = request.POST.get('about', profile.about)
        profile.professional_experience = request.POST.get('professional_experience', profile.professional_experience)
        profile.interest_areas = ",".join(request.POST.getlist('interest_areas'))
        profile.ability = request.POST.get('ability', profile.ability)
        profile.save()
        return redirect('bocaboca_profile:dashboard')

    context = {
        'user': user,
        'profile': profile,
        'nickname': profile.nickname,
        'full_name': profile.name
    }
    return render(request, 'bocaboca/pages/profile_edit.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def handle_profile_submission(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        username = data.get("username")
        user = get_object_or_404(User, username=username)
        profile = NewUser.objects.get(user=user)

        profile.name = data.get("name", profile.name)
        profile.nickname = data.get("nickname", profile.nickname)
        profile.professional_title = data.get("professional_title", profile.professional_title)
        profile.about = data.get("about", profile.about)
        profile.professional_experience = data.get("professional_experience", profile.professional_experience)
        profile.interest_areas = ",".join(data.get("interest_areas", profile.interest_areas.split(",")))
        profile.ability = data.get("ability", profile.ability)
        profile.save()

        return JsonResponse({"message": "Perfil atualizado com sucesso."}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
