
# 📌 Plano do MVP — Plataforma Boca Boca

Este documento detalha os entregáveis do MVP da plataforma de recomendação de profissionais, bem como o cronograma de entregas e sugestões para organização no GitHub.

---

## ✅ Entregáveis do MVP

### 🔹 1. Cadastro e Autenticação
- [x] Cadastro de usuário com e-mail
- [x] Link de ativação por e-mail
- [x] Login e logout
- [ ] Cadastro de usuário via telefone (opcional)

### 🔹 2. Cadastro de Profissional
- [x] Cadastro básico (nome e slug)
- [ ] Inclusão de:
  - [ ] Endereço (bairro, cidade, estado, CEP)
  - [ ] Telefone ou WhatsApp
  - [ ] Categoria (relacionar com `Category`)
  - [ ] Campo “indicado por” (usuário que cadastrou)

### 🔹 3. Avaliação
- [ ] Modelo de Avaliação com:
  - Estrelas (1 a 5)
  - Comentário
  - Data e autor
- [ ] Página do profissional exibindo média e avaliações

### 🔹 4. Busca e Navegação
- [x] Listagem por categoria
- [ ] Filtros de busca:
  - [ ] Cidade/Estado
  - [ ] Nome ou serviço
  - [ ] Nota (maiores primeiro)

### 🔹 5. Visual e Navegação
- [x] Templates base e parciais
- [x] Páginas principais: home, login, registro
- [ ] Página pública do profissional
- [ ] Página com listagem de categorias

### 🔹 6. Painel Administrativo
- [x] Admin de `Profissional`, `Category` e `Page`
- [x] `BocabocaSetup` com inline links
- [ ] Dashboard básico com métricas

### 🔹 7. Deploy e Entrega
- [x] Docker + docker-compose configurado
- [ ] Deploy no Render com domínio
- [ ] Testes básicos manuais

---

## 🗓️ Cronograma de Entregas

| Semana   | Início     | Fim        | Entregável                                                                 |
|----------|------------|------------|----------------------------------------------------------------------------|
| Semana 1 | 06/08/2025 | 12/08/2025 | Finalizar cadastro completo de profissional (endereços, categorias, telefone) |
| Semana 2 | 13/08/2025 | 19/08/2025 | Implementar modelo de Avaliação e página do profissional com média e comentários |
| Semana 3 | 20/08/2025 | 26/08/2025 | Adicionar filtros de busca (nome, cidade, nota) e refinar listagem        |
| Semana 4 | 27/08/2025 | 02/09/2025 | Concluir página pública do profissional e listagem de categorias          |
| Semana 5 | 03/09/2025 | 09/09/2025 | Refatorar painel admin + ajustes finais no layout (mobile + responsivo)   |
| Semana 6 | 10/09/2025 | 16/09/2025 | Deploy no Render + testes + entrega final                                 |

---

## 🛠️ Sugestão de Organização no GitHub

### 📌 Issues Sugeridas:
- `[Backend] Adicionar campos de endereço ao modelo Profissional`
- `[Backend] Criar modelo de Avaliação com estrelas e comentários`
- `[Frontend] Exibir avaliações na página do profissional`
- `[Busca] Implementar filtro por cidade e nota`
- `[Layout] Criar página pública de perfil do profissional`
- `[Admin] Mostrar dashboard com métricas básicas`
- `[Deploy] Subir sistema para Render com domínio`
- `[QA] Testar cadastro, avaliação e busca em produção`

### 🗂 Labels recomendadas:
- `frontend`, `backend`, `prioridade alta`, `visual`, `melhoria`, `bug`, `deploy`

---

**Responsável técnico**: Goutemberg Pessoa  
**Versão inicial**: Agosto de 2025  
