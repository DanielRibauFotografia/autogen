# Makefile para automação de comandos do JARVIS
# Este arquivo simplifica operações comuns do sistema

.PHONY: help setup up down logs status clean rebuild test lint format debug install

# Configurações
DOCKER_COMPOSE = docker-compose
PYTHON = python3
PIP = pip3

# Cores para output (compatível com macOS)
GREEN = \033[0;32m
YELLOW = \033[0;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## 📖 Mostra esta ajuda
	@echo "$(GREEN)🤖 JARVIS - Sistema Multi-Agente$(NC)"
	@echo "$(YELLOW)Comandos disponíveis:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## 🚀 Configuração inicial completa
	@echo "$(GREEN)Iniciando configuração do JARVIS...$(NC)"
	@$(PYTHON) -m venv venv || echo "$(YELLOW)Ambiente virtual já existe$(NC)"
	@source venv/bin/activate && $(PIP) install --upgrade pip
	@source venv/bin/activate && $(PIP) install -r requirements.txt
	@mkdir -p logs data/photos memory/data
	@$(DOCKER_COMPOSE) build
	@echo "$(GREEN)✅ Configuração concluída!$(NC)"
	@echo "$(YELLOW)Execute 'make up' para iniciar o sistema$(NC)"

install: ## 📦 Instala dependências Python
	@echo "$(GREEN)Instalando dependências...$(NC)"
	@$(PIP) install -r requirements.txt
	@echo "$(GREEN)✅ Dependências instaladas!$(NC)"

up: ## ▶️ Inicia todos os serviços
	@echo "$(GREEN)Iniciando JARVIS...$(NC)"
	@$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✅ JARVIS está rodando!$(NC)"
	@echo "$(YELLOW)RabbitMQ Management: http://localhost:15672 (guest/guest)$(NC)"
	@echo "$(YELLOW)Use 'make logs' para ver os logs$(NC)"

down: ## ⏹️ Para todos os serviços
	@echo "$(YELLOW)Parando JARVIS...$(NC)"
	@$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✅ JARVIS parado$(NC)"

logs: ## 📄 Mostra logs de todos os serviços
	@$(DOCKER_COMPOSE) logs --tail=100

logs-follow: ## 📄 Mostra logs em tempo real
	@$(DOCKER_COMPOSE) logs -f

logs-photo: ## 📸 Logs do PhotoAgent
	@$(DOCKER_COMPOSE) logs photo-agent --tail=50

logs-marketing: ## 📈 Logs do MarketingAgent
	@$(DOCKER_COMPOSE) logs marketing-agent --tail=50

logs-social: ## 📱 Logs do SocialMediaAgent
	@$(DOCKER_COMPOSE) logs social-media-agent --tail=50

logs-crm: ## 👥 Logs do CRMAgent
	@$(DOCKER_COMPOSE) logs crm-agent --tail=50

logs-calendar: ## 📅 Logs do CalendarAgent
	@$(DOCKER_COMPOSE) logs calendar-agent --tail=50

logs-finance: ## 💰 Logs do FinanceAgent
	@$(DOCKER_COMPOSE) logs finance-agent --tail=50

logs-task: ## ✅ Logs do TaskAgent
	@$(DOCKER_COMPOSE) logs task-agent --tail=50

logs-orchestrator: ## 🎭 Logs do Orchestrator
	@$(DOCKER_COMPOSE) logs orchestrator --tail=50

logs-rabbitmq: ## 🐰 Logs do RabbitMQ
	@$(DOCKER_COMPOSE) logs rabbitmq --tail=50

status: ## 📊 Status de todos os serviços
	@echo "$(GREEN)Status dos serviços JARVIS:$(NC)"
	@$(DOCKER_COMPOSE) ps

clean: ## 🧹 Limpa containers, imagens e volumes
	@echo "$(YELLOW)Limpando containers e volumes...$(NC)"
	@$(DOCKER_COMPOSE) down -v
	@docker system prune -f
	@echo "$(GREEN)✅ Limpeza concluída$(NC)"

rebuild: ## 🔄 Reconstrói todas as imagens
	@echo "$(GREEN)Reconstruindo imagens...$(NC)"
	@$(DOCKER_COMPOSE) build --no-cache
	@echo "$(GREEN)✅ Imagens reconstruídas$(NC)"

restart: ## 🔄 Reinicia todos os serviços
	@echo "$(YELLOW)Reiniciando JARVIS...$(NC)"
	@$(DOCKER_COMPOSE) restart
	@echo "$(GREEN)✅ JARVIS reiniciado$(NC)"

test: ## 🧪 Executa testes
	@echo "$(GREEN)Executando testes...$(NC)"
	@source venv/bin/activate && pytest tests/ -v
	@echo "$(GREEN)✅ Testes concluídos$(NC)"

lint: ## 🔍 Verifica qualidade do código
	@echo "$(GREEN)Verificando código...$(NC)"
	@source venv/bin/activate && flake8 agents/ orchestrator/ cli/ memory/
	@source venv/bin/activate && mypy agents/ orchestrator/ cli/ memory/ --ignore-missing-imports
	@echo "$(GREEN)✅ Verificação concluída$(NC)"

format: ## 🎨 Formata código automaticamente
	@echo "$(GREEN)Formatando código...$(NC)"
	@source venv/bin/activate && black agents/ orchestrator/ cli/ memory/ examples/
	@echo "$(GREEN)✅ Código formatado$(NC)"

# Comandos de debug individuais
debug-photo: ## 🐛 Debug PhotoAgent
	@$(DOCKER_COMPOSE) run --rm photo-agent python -c "import agent; print('PhotoAgent OK')"

debug-marketing: ## 🐛 Debug MarketingAgent
	@$(DOCKER_COMPOSE) run --rm marketing-agent python -c "import agent; print('MarketingAgent OK')"

debug-rabbitmq: ## 🐛 Testa conexão RabbitMQ
	@$(DOCKER_COMPOSE) exec rabbitmq rabbitmqctl status

# Comandos de CLI
cli: ## 💻 Abre CLI interativo
	@source venv/bin/activate && python cli/jarvis_cli.py

cli-task: ## 💻 Executa tarefa via CLI (uso: make cli-task TASK="sua tarefa")
	@source venv/bin/activate && python cli/jarvis_cli.py task "$(TASK)"

# Exemplos
example-communication: ## 🔄 Testa comunicação entre agentes
	@echo "$(GREEN)Executando exemplo de comunicação...$(NC)"
	@source venv/bin/activate && python examples/agent_communication_demo.py

example-simple: ## 🚀 Executa exemplo simples
	@echo "$(GREEN)Executando exemplo simples...$(NC)"
	@source venv/bin/activate && python examples/simple_task.py

# Utilitários
check-deps: ## ✅ Verifica dependências do sistema
	@echo "$(GREEN)Verificando dependências...$(NC)"
	@echo "Python: $$(python3 --version)"
	@echo "Docker: $$(docker --version)"
	@echo "Docker Compose: $$(docker-compose --version)"
	@echo "$(GREEN)✅ Dependências verificadas$(NC)"

backup-memory: ## 💾 Backup do sistema de memória
	@echo "$(GREEN)Fazendo backup da memória...$(NC)"
	@tar -czf backup_memory_$$(date +%Y%m%d_%H%M%S).tar.gz memory/
	@echo "$(GREEN)✅ Backup concluído$(NC)"

monitor: ## 📊 Monitora recursos dos containers
	@echo "$(GREEN)Monitorando recursos (Ctrl+C para sair)...$(NC)"
	@docker stats

# Configuração de desenvolvimento
dev-setup: ## 🛠️ Configuração para desenvolvimento
	@echo "$(GREEN)Configurando ambiente de desenvolvimento...$(NC)"
	@$(PYTHON) -m venv venv
	@source venv/bin/activate && $(PIP) install -r requirements.txt
	@source venv/bin/activate && $(PIP) install pytest black flake8 mypy
	@echo "$(GREEN)✅ Ambiente de desenvolvimento configurado$(NC)"

# Default target
.DEFAULT_GOAL := help