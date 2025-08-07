#!/bin/bash

echo "🔄 Parando e removendo containers + volumes..."
docker compose down -v

echo "🧨 Removendo volume nomeado do banco de dados..."
docker volume rm bocaboca_db_data || true

echo "🧼 Removendo arquivos de migração antigos..."
rm -rf djangoapp/bocabocaApp/migrations
rm -rf djangoapp/bocaboca_profile/migrations
rm -rf djangoapp/bocaboca_setup/migrations
rm -rf djangoapp/bocaboca/migrations

echo "📁 Criando pastas de migração novamente com __init__.py..."
mkdir -p djangoapp/bocabocaApp/migrations && touch djangoapp/bocabocaApp/migrations/__init__.py
mkdir -p djangoapp/bocaboca_profile/migrations && touch djangoapp/bocaboca_profile/migrations/__init__.py
mkdir -p djangoapp/bocaboca_setup/migrations && touch djangoapp/bocaboca_setup/migrations/__init__.py
mkdir -p djangoapp/bocaboca/migrations && touch djangoapp/bocaboca/migrations/__init__.py

echo "🧹 Limpando __pycache__ (se houver)..."
find . -type d -name "__pycache__" -exec rm -rf {} +

echo "🚀 Subindo containers novamente..."
docker compose up -d --build

echo "⌛ Aguardando containers subirem (5s)..."
sleep 5

echo "⚙️ Gerando migrações do zero (em ordem)..."
docker exec -it djangoapp sh -c "python manage.py makemigrations bocaboca_profile"
docker exec -it djangoapp sh -c "python manage.py makemigrations bocabocaApp"
docker exec -it djangoapp sh -c "python manage.py makemigrations bocaboca_setup"

echo "📦 Aplicando migrações no banco de dados..."
docker exec -it djangoapp sh -c "python manage.py migrate"

echo "✅ Banco de dados e migrações prontos. Tudo limpo e funcionando!"
