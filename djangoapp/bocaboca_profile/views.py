from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import PendingUser, NewUser
from django.http import HttpResponseBadRequest, JsonResponse
from django.contrib.auth import login, authenticate, get_user_model
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import random
import re
from django.contrib import messages
from django.conf import settings
from .models import CustomUser
from django.contrib.auth.hashers import make_password
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError


def _is_json_request(request):
    return request.headers.get("Content-Type", "").startswith("application/json")

INTEREST_AREAS = [
    "tecnologia", "ciencia", "engenharia",
    "arte", "matematica", "fisica",
    "historia", "literatura", "filosofia",
    "biologia", "quimica", "geografia",
]


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

def finalize_phone_registration(request):
    telefone = request.GET.get('telefone', '')

    if request.method == 'POST':
        nome = request.POST.get('nome')
        senha = request.POST.get('senha')

        if not telefone or not nome or not senha:
            messages.error(request, "Preencha todos os campos.")
            return redirect('bocaboca_profile:finalize_phone_registration')  # ou use reverse + query params

        username = telefone.replace('+', '').replace(' ', '').replace('-', '')
        user = User.objects.create_user(username=username, first_name=nome, password=senha)
        user.is_active = True
        user.save()

        login(request, user)
        request.session['full_name'] = nome
        request.session['nickname'] = nome.split()[0]

        return redirect('bocaboca_profile:new_client', username=username)  # ou new_user, dependendo da role

    return render(request, 'bocaboca/pages/finalize_phone_registration.html', {
        'telefone': telefone
    })


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
        'full_name': request.session.get('full_name', user.first_name),
        'interest_areas': INTEREST_AREAS,
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
        'full_name': request.session.get('full_name', user.first_name),
        'interest_areas': INTEREST_AREAS,
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
        'full_name': profile.name,
        'interest_areas': INTEREST_AREAS,

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
        'full_name': profile.name,
        'interest_areas': INTEREST_AREAS,

    }
    return render(request, 'bocaboca/pages/profile_edit.html', context)


@csrf_exempt
@require_http_methods(["POST"])
@csrf_exempt
def handle_profile_submission(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Método inválido")

    data = {}
    if _is_json_request(request):
        try:
            import json
            data = json.loads(request.body.decode("utf-8"))
        except Exception:
            return JsonResponse({"error": "JSON inválido"}, status=400)
    else:
        data = request.POST

    name = (data.get("name") or "").strip()
    nickname = (data.get("nickname") or "").strip()
    professional_title = (data.get("professional_title") or "").strip()
    about = (data.get("about") or "").strip()
    professional_experience = (data.get("professional_experience") or "").strip()
    if hasattr(data, "getlist"):
        interest_areas = data.getlist("interest_areas")
    else:
        interest_areas = data.get("interest_areas") or []
        if isinstance(interest_areas, str):
            interest_areas = [x.strip() for x in interest_areas.split(",") if x.strip()]
    ability = (data.get("ability") or "").strip()

    telefone = (data.get("phone") or data.get("telefone") or "").strip()
    username = (data.get("username") or "").strip()

    if not name or not nickname:
        msg = "Preencha nome e apelido."
        if _is_json_request(request):
            return JsonResponse({"error": msg}, status=400)
        return HttpResponseBadRequest(msg)

    user = None
    if username:
        user = get_object_or_404(User, username=username)
    elif request.user.is_authenticated:
        user = request.user
    else:
        base = slugify(name) or "usuario"
        username = f"{base}-{get_random_string(6)}"
        user = User.objects.create_user(username=username, first_name=name, is_active=True)

    profile, _ = NewUser.objects.get_or_create(user=user)
    profile.name = name or profile.name
    profile.nickname = nickname or profile.nickname
    profile.professional_title = professional_title or profile.professional_title
    profile.about = about or profile.about
    profile.professional_experience = professional_experience or profile.professional_experience
    profile.interest_areas = ",".join(interest_areas) if interest_areas else profile.interest_areas
    profile.ability = ability or profile.ability
    profile.save()

    if _is_json_request(request):
        return JsonResponse({"message": "Perfil salvo", "username": user.username}, status=200)

    return redirect("bocaboca_profile:dashboard")


PHONE_CLEAN_RE = re.compile(r"[^\d]+")

def normalize_phone(phone: str) -> str:
    """Deixa só dígitos e remove espaços/traços/etc."""
    if not phone:
        return ""
    return PHONE_CLEAN_RE.sub("", phone)

def generate_code() -> str:
    """Gera código numérico de 6 dígitos."""
    return f"{random.randint(0, 999999):06d}"
    

@csrf_exempt
@require_POST
def send_sms_code(request):
    """
    Espera: form-data com 'phone'
    Retorna: JSON { ok: true, message, (debug_code opcional) }
    E salva em sessão: sms_verification_code, phone_number
    """
    phone = normalize_phone(request.POST.get("phone", ""))

    if not phone or len(phone) < 10:
        return JsonResponse({"ok": False, "message": "Informe um telefone válido."}, status=400)

    code = generate_code()
    request.session["sms_verification_code"] = code
    request.session["phone_number"] = phone

    print(f"[SMS DEBUG] Código para {phone}: {code}")

    payload = {
        "ok": True,
        "message": f"Código enviado para {phone}.",
    }
    if getattr(settings, "DEBUG", True):
        payload["debug_code"] = code

    return JsonResponse(payload, status=200)


@csrf_exempt
@require_POST
def validate_sms_code(request):
    """
    Valida o código guardado na sessão, cria/recupera o User com username=telefone,
    faz login imediatamente e redireciona para a finalização do cadastro.
    """
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        data = request.POST

    entered_code = (data.get("sms_code") or "").strip()
    correct_code = (request.session.get("sms_verification_code") or "").strip()
    phone_raw = request.session.get("phone_number")

    if not phone_raw:
        return JsonResponse({"ok": False, "message": "Sessão expirada. Reenvie o código."}, status=400)
    if not entered_code:
        return JsonResponse({"ok": False, "message": "Informe o código de verificação."}, status=400)
    if entered_code != correct_code:
        return JsonResponse({"ok": False, "message": "Código inválido. Tente novamente."}, status=400)

    # Normaliza telefone (mesma função que você já usa)
    phone = normalize_phone(phone_raw)
    User = get_user_model()

    # Cria/pega o usuário com username=telefone e ativa se necessário
    try:
        with transaction.atomic():
            user, created = User.objects.get_or_create(
                username=phone,
                defaults={"is_active": True, "first_name": ""}  # ajuste se quiser
            )
            if not user.is_active:
                user.is_active = True
                user.save(update_fields=["is_active"])
    except IntegrityError:
        # Em caso de corrida, recupera o usuário
        user = User.objects.get(username=phone)
        if not user.is_active:
            user.is_active = True
            user.save(update_fields=["is_active"])

    # ✅ cria a sessão AGORA
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    # limpa o código (mantém o phone opcionalmente se quiser reaproveitar na querystring)
    request.session.pop("sms_verification_code", None)

    next_url = f"{reverse('bocaboca_profile:finalizar_cadastro_telefone')}?telefone={phone}"
    return JsonResponse({"ok": True, "next_url": next_url}, status=200)

@login_required
def finalizar_cadastro_telefone(request):
    # telefone vem da querystring (ou da sessão se preferir)
    telefone = normalize_phone(request.GET.get("telefone") or request.session.get("phone_number") or "")

    if request.method == "POST":
        nome = (request.POST.get("name") or "").strip()
        nickname = (request.POST.get("nickname") or "").strip()
        professional_title = (request.POST.get("professional_title") or "").strip()
        about = (request.POST.get("about") or "").strip()
        professional_experience = (request.POST.get("professional_experience") or "").strip()
        interest_areas = request.POST.getlist("interest_areas")
        ability = (request.POST.get("ability") or "").strip()

        if not nome or not nickname:
            messages.error(request, "Preencha nome e apelido para continuar.")
            return redirect(f"{reverse('bocaboca_profile:finalizar_cadastro_telefone')}?telefone={telefone}")

        # ✅ atualiza o User logado (não cria outro)
        user = request.user
        if (user.first_name or "") != nome:
            user.first_name = nome
            user.save(update_fields=["first_name"])

        # ✅ cria/atualiza o perfil e grava o telefone
        profile, _ = NewUser.objects.get_or_create(user=user)
        profile.phone = telefone  # Campo que você adicionou com unique=True
        profile.name = nome
        profile.nickname = nickname
        profile.professional_title = professional_title
        profile.about = about
        profile.professional_experience = professional_experience
        profile.interest_areas = ",".join(interest_areas)
        profile.ability = ability
        profile.save()

        # Sessão para UX
        request.session["nickname"] = nickname or (user.username or "")
        request.session["full_name"] = nome or (user.first_name or "")

        # Limpa resto, se quiser
        request.session.pop("phone_number", None)

        return redirect("bocaboca_profile:dashboard")

    # GET: renderiza o formulário já logado
    context = {
        "full_name": request.user.first_name or "",
        "nickname": "",
        "telefone": telefone,
        "interest_areas": INTEREST_AREAS,
    }
    return render(request, "bocaboca/pages/profile.html", context)
@csrf_exempt
@require_POST
def password_login(request):
    identifier = (request.POST.get("identifier") or "").strip()
    password = (request.POST.get("password") or "").strip()

    if not identifier or not password:
        return HttpResponseBadRequest("Credenciais inválidas.")

    username = None
    if "@" in identifier:
        try:
            user = User.objects.get(email__iexact=identifier)
            username = user.username
        except User.DoesNotExist:
            username = None
    else:
        # se quiser aceitar username direto
        username = identifier

    user = authenticate(request, username=username, password=password) if username else None
    if user is None:
        return HttpResponseBadRequest("Credenciais inválidas.")

    if not user.is_active:
        return HttpResponseBadRequest("Usuário inativo.")

    login(request, user)
    return redirect("bocaboca_profile:dashboard")

# --- Login via telefone – enviar código ---
@csrf_exempt
@require_POST
def login_send_code(request):
    phone_raw = request.POST.get("phone")
    phone = normalize_phone(phone_raw)
    if not phone:
        return JsonResponse({"ok": False, "message": "Informe um telefone válido."}, status=400)

    # Tentar localizar usuário por perfil (phone) ou pelo username=telefone
    user = None
    try:
        nu = NewUser.objects.select_related("user").get(phone=phone)  # precisa ter campo phone em NewUser
        user = nu.user
    except Exception:
        try:
            user = User.objects.get(username=phone)  # fallback: username igual ao telefone
        except User.DoesNotExist:
            user = None

    if user is None:
        return JsonResponse({"ok": False, "message": "Telefone não encontrado. Cadastre-se."}, status=404)

    code = generate_code()
    request.session["login_sms_code"] = code
    request.session["login_phone"] = phone

    # DEBUG: aparece no terminal/docker logs
    print(f"[LOGIN SMS DEBUG] Código para {phone}: {code}")

    return JsonResponse({"ok": True, "message": f"Código enviado para {phone}."}, status=200)

# --- Login via telefone – validar código ---
@csrf_exempt
@require_POST
def login_validate_code(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        data = request.POST

    entered = (data.get("sms_code") or "").strip()
    correct = (request.session.get("login_sms_code") or "").strip()
    phone = request.session.get("login_phone")

    if not phone:
        return JsonResponse({"ok": False, "message": "Sessão expirada. Reenvie o código."}, status=400)

    if entered != correct:
        return JsonResponse({"ok": False, "message": "Código inválido."}, status=400)

    # Localiza usuário novamente
    user = None
    try:
        nu = NewUser.objects.select_related("user").get(phone=phone)
        user = nu.user
    except Exception:
        try:
            user = User.objects.get(username=phone)
        except User.DoesNotExist:
            return JsonResponse({"ok": False, "message": "Usuário não encontrado."}, status=404)

    if not user.is_active:
        user.is_active = True
        user.save()

    login(request, user)

    request.session.pop("login_sms_code", None)
    request.session.pop("login_phone", None)

    return JsonResponse({"ok": True, "next_url": "/dashboard/"}, status=200)


PHONE_CLEAN_RE = re.compile(r"[^\d]+")
def normalize_phone(p): return PHONE_CLEAN_RE.sub("", p or "")
def generate_code(): return f"{random.randint(0, 999999):06d}"


@csrf_exempt
@require_POST
def password_login(request):
    identifier = (request.POST.get("identifier") or "").strip()
    password = (request.POST.get("password") or "").strip()

    if not identifier or not password:
        return HttpResponseBadRequest("Credenciais inválidas.")

    username = None
    if "@" in identifier:
        try:
            user = User.objects.get(email__iexact=identifier)
            username = user.username
        except User.DoesNotExist:
            username = None
    else:
        
        username = identifier

    user = authenticate(request, username=username, password=password) if username else None
    if user is None:
        return HttpResponseBadRequest("Credenciais inválidas.")

    if not user.is_active:
        return HttpResponseBadRequest("Usuário inativo.")

    login(request, user)
    return redirect("bocaboca_profile:dashboard")


@csrf_exempt
@require_POST
def login_send_code(request):
    phone_raw = request.POST.get("phone")
    phone = normalize_phone(phone_raw)
    if not phone:
        return JsonResponse({"ok": False, "message": "Informe um telefone válido."}, status=400)

    user = None
    try:
        nu = NewUser.objects.select_related("user").get(phone=phone)  
        user = nu.user
    except Exception:
        try:
            user = User.objects.get(username=phone)  
        except User.DoesNotExist:
            user = None

    if user is None:
        return JsonResponse({"ok": False, "message": "Telefone não encontrado. Cadastre-se."}, status=404)

    code = generate_code()
    request.session["login_sms_code"] = code
    request.session["login_phone"] = phone

    
    print(f"[LOGIN SMS DEBUG] Código para {phone}: {code}")

    return JsonResponse({"ok": True, "message": f"Código enviado para {phone}."}, status=200)

@csrf_exempt
@require_POST
def login_validate_code(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        data = request.POST

    entered = (data.get("sms_code") or "").strip()
    correct = (request.session.get("login_sms_code") or "").strip()
    phone = request.session.get("login_phone")

    if not phone:
        return JsonResponse({"ok": False, "message": "Sessão expirada. Reenvie o código."}, status=400)

    if entered != correct:
        return JsonResponse({"ok": False, "message": "Código inválido."}, status=400)

    user = None
    try:
        nu = NewUser.objects.select_related("user").get(phone=phone)
        user = nu.user
    except Exception:
        try:
            user = User.objects.get(username=phone)
        except User.DoesNotExist:
            return JsonResponse({"ok": False, "message": "Usuário não encontrado."}, status=404)

    if not user.is_active:
        user.is_active = True
        user.save()

    login(request, user)

    request.session.pop("login_sms_code", None)
    request.session.pop("login_phone", None)

    return JsonResponse({"ok": True, "next_url": "/dashboard/"}, status=200)

@login_required
def dashboard(request):
    profile = NewUser.objects.filter(user=request.user).first()

    # nome para exibição sem depender do template acessar a sessão
    display_name = (
        (profile.name if profile and profile.name else None)
        or request.session.get('full_name')
        or (request.user.first_name or '').strip()
        or request.user.username
    )

    fields = [
        ('name', 15), ('nickname', 10), ('professional_title', 15),
        ('about', 20), ('professional_experience', 20),
        ('interest_areas', 10), ('ability', 10),
    ]
    total = sum(w for _, w in fields)
    score = 0
    if profile:
        for field, w in fields:
            if (getattr(profile, field, '') or '').strip():
                score += w
    profile_completion = round((score / total) * 100) if total else 0

    context = {
        'profile': profile,
        'display_name': display_name,
        'profile_completion': profile_completion,
        'kpis': {'earnings': 0, 'sent_proposals': 0, 'accepted_proposals': 0, 'profile_views': 1},
    }
    return render(request, 'bocaboca/pages/dashboard.html', context)