# CLAUDE.md — Instruções para o Claude Code neste projeto

## Antes de escrever qualquer código
Leia, nesta ordem:
1. `PRD.md` — o que estamos construindo e por quê
2. `ARCHITECTURE.md` — stack e decisões técnicas já tomadas
3. `DATA_MODEL.md` — schema de dados (não invente campos/tabelas fora daqui)
4. `RULES.md` — regras de negócio obrigatórias

## Regras de trabalho
- Não tome decisões de arquitetura não documentadas aqui — se precisar de algo que não está definido, pare e pergunte, não invente.
- Trabalhe em tarefas pequenas (ver `TASKS.md`, quando existir). Não implemente múltiplos módulos numa única sessão sem revisão.
- Sempre que um model, regra de negócio ou decisão de arquitetura mudar durante o desenvolvimento, atualize o arquivo correspondente (`DATA_MODEL.md`, `RULES.md` etc.) — a documentação tem que continuar refletindo a realidade do código.
- Produto físico e digital compartilham o model `Product` (ver `DATA_MODEL.md`) — não crie models separados para cada tipo.

## Stack (resumo — ver ARCHITECTURE.md para detalhes)
- Django + DRF + Wagtail
- PostgreSQL
- S3 para arquivos digitais
- Stripe para pagamento

## Convenções de código
- Nomes de **campo** de model são em português (`nome`, `preco`, `criado_em`, `tipo_cliente`). Nomes de **model**/classe/tabela continuam em inglês (`Product`, `Order`, `Customer`). Valores internos de `enum`/`choices` armazenados no banco continuam em inglês (`'wholesale'`, `'paid'`, `'digital'`) — só o rótulo exibido (`get_<campo>_display()`) é em português. Essa convenção vale pra todo model novo, não só CRM/Financeiro — ver `DATA_MODEL.md`.

## Comandos úteis
- Ativar venv: `.venv\Scripts\Activate.ps1` (PowerShell)
- Rodar servidor: `python manage.py runserver` (usa `contemplart.settings.dev` por padrão, lê `.env`)
- Rodar migrations: `python manage.py migrate` (requer Postgres — ver `docker-compose.yml`, precisa `docker compose up -d` antes)
- Gerar migrations: `python manage.py makemigrations`

## O que NUNCA fazer
- Não hardcode conteúdo de layout/marketing em templates — isso deve vir do Wagtail.
- Não gere link de download digital antes da confirmação de pagamento via webhook.
- Não calcule frete sobre itens digitais.
