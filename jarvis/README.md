# 🤖 JARVIS - Sistema Multi-Agente Local

![JARVIS Architecture](docs/jarvis_architecture.png)

**JARVIS** é um sistema inteligente multi-agente 100% local, desenvolvido em Python com Docker, projetado para automatizar e otimizar processos de negócios de forma modular e escalável.

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Arquitetura do Sistema](#-arquitetura-do-sistema)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Uso Rápido](#-uso-rápido)
- [Agentes Disponíveis](#-agentes-disponíveis)
- [Sistema de Memória](#-sistema-de-memória)
- [Comunicação Entre Agentes](#-comunicação-entre-agentes)
- [Desenvolvimento](#-desenvolvimento)
- [Troubleshooting](#-troubleshooting)
- [Recursos de Aprendizado](#-recursos-de-aprendizado)

## 🎯 Visão Geral

JARVIS é um sistema multi-agente inspirado no conceito de **Inteligência Artificial Distribuída**, onde diferentes agentes especializados trabalham em conjunto para executar tarefas complexas. Cada agente tem uma responsabilidade específica e se comunica com outros através de um sistema de mensagens assíncrono.

### Por que Multi-Agente?

- **Modularidade**: Cada agente é independente e pode ser desenvolvido/mantido separadamente
- **Escalabilidade**: Novos agentes podem ser adicionados facilmente
- **Robustez**: Se um agente falha, os outros continuam funcionando
- **Especialização**: Cada agente foca em uma área específica de expertise

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                        JARVIS SYSTEM                        │
├─────────────────────────────────────────────────────────────┤
│  CLI Interface          │          Orchestrator             │
├─────────────────────────────────────────────────────────────┤
│                    RabbitMQ Message Bus                     │
├─────────────────────────────────────────────────────────────┤
│ PhotoAgent │ Marketing │ SocialMedia │ CRM │ Calendar │ ... │
├─────────────────────────────────────────────────────────────┤
│                    Central Memory System                     │
│  Episódica │ Semântica │ Procedural │ Emocional │ Trabalho  │
└─────────────────────────────────────────────────────────────┘
```

### Componentes Principais:

1. **Agentes Especializados**: Cada agente tem uma função específica
2. **Sistema de Memória Centralizado**: Armazena conhecimento compartilhado
3. **Message Bus (RabbitMQ)**: Comunicação assíncrona entre agentes
4. **Orchestrador**: Gerencia o ciclo de vida dos agentes
5. **CLI**: Interface de linha de comando para interação

## 💻 Pré-requisitos

### Sistema Operacional
- **macOS ARM64** (Apple Silicon M1/M2/M3)
- **Versões Testadas**: macOS Ventura 13.0+ e macOS Sonoma 14.0+

### Software Necessário

```bash
# 1. Python 3.10 ou superior
python3 --version  # Deve mostrar 3.10+

# 2. Docker Desktop para Mac (ARM64)
docker --version   # Teste se está funcionando

# 3. Docker Compose (incluído no Docker Desktop)
docker compose version  # ou docker-compose --version

# 4. Git
git --version
```

### Instalação do Docker Desktop (macOS ARM64)

1. Baixe o [Docker Desktop para Mac ARM64](https://desktop.docker.com/mac/main/arm64/Docker.dmg)
2. Execute o instalador
3. Inicie o Docker Desktop
4. Verifique a instalação:

```bash
docker run hello-world
```

### Extensões Recomendadas para VS Code

Para uma melhor experiência de desenvolvimento, instale estas extensões no VS Code:

```bash
# Instale o VS Code se ainda não tiver
brew install --cask visual-studio-code

# Extensões essenciais (instale via VS Code):
# 1. Python (ms-python.python)
# 2. Docker (ms-azuretools.vscode-docker)
# 3. YAML (redhat.vscode-yaml)
# 4. GitLens (eamodio.gitlens)
# 5. Thunder Client (rangav.vscode-thunder-client) - para testar APIs
```

## 🚀 Instalação

### Instalação Rápida (Recomendada)

```bash
# 1. Clone o repositório
git clone https://github.com/DanielRibauFotografia/autogen.git
cd autogen/jarvis

# 2. Execute o script de setup automático
make setup

# 3. Inicie o sistema
make up
```

### Instalação Manual

```bash
# 1. Clone o repositório
git clone https://github.com/DanielRibauFotografia/autogen.git
cd autogen/jarvis

# 2. Crie o ambiente virtual Python
python3 -m venv venv
source venv/bin/activate

# 3. Instale dependências
pip install -r requirements.txt

# 4. Construa as imagens Docker
docker compose build

# 5. Inicie os serviços
docker compose up -d
```

## ⚡ Uso Rápido

### 🎬 Demo Rápido (5 minutos)

```bash
# Execute o demo interativo (não requer Docker)
./demo.sh
```

### Comandos Básicos

```bash
# Iniciar todo o sistema
make up

# Parar o sistema
make down

# Ver logs de todos os agentes
make logs

# Ver logs de um agente específico
make logs-photo

# Executar comando via CLI
python cli/jarvis_cli.py --help

# Executar exemplo de comunicação entre agentes
python examples/agent_communication_demo.py
```

### Primeiro Teste

```bash
# 1. Certifique-se que o sistema está rodando
make status

# 2. Teste comunicação entre agentes
python examples/simple_task.py

# 3. Interaja via CLI
python cli/jarvis_cli.py task "Organize minha agenda para amanhã"
```

## 🤖 Agentes Disponíveis

### 📸 PhotoAgent
**Especialização**: Gerenciamento e processamento de imagens
- Organização de bibliotecas de fotos
- Análise de metadados
- Processamento básico de imagens
- Backup e sincronização

```python
# Exemplo de uso
from agents.photo_agent import PhotoAgent
agent = PhotoAgent()
result = await agent.organize_photos("/path/to/photos")
```

### 📈 MarketingAgent
**Especialização**: Análise e estratégias de marketing
- Análise de campanhas
- Sugestões de conteúdo
- Métricas de performance
- Planejamento de estratégias

### 📱 SocialMediaAgent
**Especialização**: Gestão de redes sociais
- Agendamento de posts
- Análise de engajamento
- Monitoramento de menções
- Relatórios de performance

### 👥 CRMAgent
**Especialização**: Gestão de relacionamento com clientes
- Gestão de contatos
- Histórico de interações
- Segmentação de clientes
- Automação de follow-up

### 📅 CalendarAgent
**Especialização**: Gerenciamento de agenda
- Agendamento inteligente
- Otimização de horários
- Lembretes automáticos
- Integração com calendários

### 💰 FinanceAgent
**Especialização**: Gestão financeira
- Controle de orçamento
- Análise de despesas
- Relatórios financeiros
- Previsões e metas

### ✅ TaskAgent
**Especialização**: Gerenciamento de tarefas
- Criação e atribuição de tarefas
- Acompanhamento de progresso
- Priorização automática
- Relatórios de produtividade

## 🧠 Sistema de Memória

O sistema de memória do JARVIS é dividido em cinco tipos, baseado na neurociência cognitiva:

### 📚 Memória Episódica
**O que é**: Armazena eventos específicos com contexto temporal
**Exemplo**: "Em 15/01/2024, o cliente João solicitou orçamento para ensaio de casamento"

### 🔬 Memória Semântica
**O que é**: Armazena conhecimento geral e fatos
**Exemplo**: "Ensaios de casamento geralmente duram 2-3 horas"

### ⚙️ Memória Procedural
**O que é**: Armazena como fazer coisas (procedimentos)
**Exemplo**: "Para processar fotos de casamento: 1) Fazer backup, 2) Selecionar melhores, 3) Editar..."

### 💝 Memória Emocional
**O que é**: Armazena contexto emocional e preferências
**Exemplo**: "Cliente prefere cores quentes e estilo natural"

### 💼 Memória de Trabalho
**O que é**: Armazena informação temporária para tarefas ativas
**Exemplo**: "Tarefa atual: Editar 50 fotos do casamento da Maria"

### Como Usar o Sistema de Memória

```python
from memory.memory_manager import MemoryManager

memory = MemoryManager()

# Armazenar memória episódica
memory.store_episodic("cliente_joao_pedido", {
    "evento": "solicitacao_orcamento",
    "cliente": "João Silva",
    "tipo_servico": "ensaio_casamento",
    "data": "2024-01-15T10:30:00"
})

# Recuperar memória semântica
conhecimento = memory.get_semantic("procedimentos_ensaio_casamento")
```

## 🔄 Comunicação Entre Agentes

### RabbitMQ Message Bus

O JARVIS usa **RabbitMQ** como sistema de mensagens. RabbitMQ é um "message broker" (corretor de mensagens) que permite que diferentes partes do sistema se comuniquem de forma assíncrona.

**Por que RabbitMQ?**
- **Confiável**: Garante que mensagens não sejam perdidas
- **Escalável**: Suporta milhões de mensagens
- **Flexível**: Diferentes padrões de comunicação
- **Padrão da Indústria**: Usado por empresas como Uber, Netflix

### Padrões de Comunicação

#### 1. Pub/Sub (Publisher/Subscriber)
Um agente publica uma mensagem e vários agentes podem recebê-la:

```python
# PhotoAgent publica que processou fotos
await publisher.publish("photos.processed", {
    "session_id": "abc123",
    "photos_count": 50,
    "status": "completed"
})

# MarketingAgent e SocialMediaAgent podem receber
```

#### 2. Request/Response
Um agente faz uma pergunta e espera resposta específica:

```python
# TaskAgent pergunta ao CalendarAgent
response = await request("calendar.check_availability", {
    "date": "2024-01-20",
    "duration": "2h"
})
```

### Exemplo Prático de Comunicação

```python
# Arquivo: examples/agent_communication_demo.py

import asyncio
from agents.photo_agent import PhotoAgent
from agents.marketing_agent import MarketingAgent

async def demo_comunicacao():
    """Demonstra comunicação entre PhotoAgent e MarketingAgent"""
    
    photo_agent = PhotoAgent()
    marketing_agent = MarketingAgent()
    
    # PhotoAgent processa fotos
    await photo_agent.start()
    resultado = await photo_agent.process_photos("/demo/photos")
    
    # MarketingAgent recebe notificação e cria campanha
    await marketing_agent.start()
    campanha = await marketing_agent.create_campaign_from_photos(resultado)
    
    print(f"Campanha criada: {campanha['title']}")

# Execute: python examples/agent_communication_demo.py
asyncio.run(demo_comunicacao())
```

## 🛠️ Desenvolvimento

### Estrutura de Pastas

```
jarvis/
├── agents/                 # Agentes especializados
│   ├── base/              # Classe base para todos os agentes
│   ├── photo_agent/       # Agente de fotografia
│   ├── marketing_agent/   # Agente de marketing
│   └── ...
├── memory/                # Sistema de memória centralizado
│   ├── episodic/         # Memória episódica
│   ├── semantic/         # Memória semântica
│   └── ...
├── orchestrator/          # Orquestrador do sistema
├── cli/                   # Interface de linha de comando
├── examples/              # Exemplos de uso
├── tests/                 # Testes automatizados
├── docs/                  # Documentação adicional
├── docker-compose.yml     # Configuração Docker
├── Makefile              # Comandos automatizados
└── README.md             # Este arquivo
```

### Criando um Novo Agente

1. **Crie a estrutura**:

```bash
mkdir agents/meu_agente
cd agents/meu_agente
```

2. **Crie os arquivos base**:

```python
# agents/meu_agente/agent.py
from agents.base.base_agent import BaseAgent

class MeuAgente(BaseAgent):
    def __init__(self):
        super().__init__("meu_agente")
    
    async def process_message(self, message):
        """Processa mensagens recebidas"""
        # Sua lógica aqui
        pass
    
    async def execute_task(self, task):
        """Executa uma tarefa específica"""
        # Sua lógica aqui
        return {"status": "completed", "result": "..."}
```

3. **Crie o Dockerfile**:

```dockerfile
# agents/meu_agente/Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "agent.py"]
```

4. **Adicione ao docker-compose.yml**:

```yaml
meu-agente:
  build: ./agents/meu_agente
  depends_on:
    - rabbitmq
  environment:
    - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
```

### Comandos de Desenvolvimento

```bash
# Executar testes
make test

# Executar um agente específico em modo debug
make debug-photo

# Reconstruir todas as imagens
make rebuild

# Limpar containers e volumes
make clean

# Ver logs em tempo real
make logs-follow

# Executar linting (verificação de código)
make lint

# Formatar código automaticamente
make format
```

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Docker não está rodando
**Erro**: `Cannot connect to the Docker daemon`

**Solução**:
```bash
# Inicie o Docker Desktop
open /Applications/Docker.app

# Ou via linha de comando (se instalado via Homebrew)
brew services start docker
```

#### 2. Porta já está em uso
**Erro**: `Port 5672 is already allocated`

**Solução**:
```bash
# Veja o que está usando a porta
lsof -i :5672

# Pare o processo ou use porta diferente
make down && make up
```

#### 3. RabbitMQ não conecta
**Erro**: `Connection refused [Errno 61]`

**Solução**:
```bash
# Verifique se RabbitMQ está rodando
docker ps | grep rabbitmq

# Reinicie o RabbitMQ
docker compose restart rabbitmq

# Veja os logs do RabbitMQ
docker compose logs rabbitmq
```

#### 4. Agente não responde
**Sintomas**: Agente aparece como rodando mas não processa mensagens

**Diagnóstico**:
```bash
# Veja logs do agente específico
make logs-photo

# Teste comunicação direta
python cli/jarvis_cli.py ping photo-agent

# Verifique filas no RabbitMQ
# Acesse: http://localhost:15672 (guest/guest)
```

#### 5. Problemas de Performance
**Sintomas**: Sistema lento ou travando

**Soluções**:
```bash
# Verifique uso de recursos
docker stats

# Limite recursos por container (docker-compose.yml)
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '0.5'
```

### Logs e Monitoramento

```bash
# Ver todos os logs
make logs

# Logs específicos por serviço
docker compose logs photo-agent
docker compose logs rabbitmq
docker compose logs orchestrator

# Logs em tempo real
docker compose logs -f photo-agent

# Limpar logs
docker compose down && docker system prune -f
```

## 📚 Recursos de Aprendizado

### Python para Iniciantes
- [Tutorial Oficial Python (PT-BR)](https://docs.python.org/pt-br/3/tutorial/)
- [Python para Zumbis (Curso USP)](https://pycursos.com/python-para-zumbis/)
- [Real Python](https://realpython.com/) - Tutoriais avançados

### Docker e Containers
- [Docker Desktop para Mac](https://docs.docker.com/desktop/install/mac-install/)
- [Docker Tutorial (PT-BR)](https://docs.docker.com/get-started/)
- [Docker Compose Guide](https://docs.docker.com/compose/gettingstarted/)

### RabbitMQ e Mensageria
- [RabbitMQ Tutorial](https://www.rabbitmq.com/tutorials/tutorial-one-python.html)
- [Pika Documentation](https://pika.readthedocs.io/) - Biblioteca Python para RabbitMQ
- [Message Patterns](https://www.enterpriseintegrationpatterns.com/) - Padrões de mensageria

### Multi-Agent Systems
- [Introduction to Multi-Agent Systems](https://www.youtube.com/watch?v=7PMs5Qk0z1A)
- [Agent-Based Modeling](https://ccl.northwestern.edu/netlogo/)
- [AutoGen Framework](https://microsoft.github.io/autogen/) - Framework da Microsoft

### VS Code para Python
- [Python in VS Code](https://code.visualstudio.com/docs/python/python-tutorial)
- [Docker in VS Code](https://code.visualstudio.com/docs/containers/overview)
- [Best VS Code Extensions for Python](https://realpython.com/python-development-visual-studio-code/)

### Arquitetura de Software
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Microservices Patterns](https://microservices.io/patterns/)
- [Event-Driven Architecture](https://martinfowler.com/articles/201701-event-driven.html)

## 🤝 Contribuindo

Quer contribuir com o JARVIS? Ótimo! Aqui está como começar:

1. **Fork** o repositório
2. **Clone** seu fork: `git clone https://github.com/seu-usuario/autogen.git`
3. **Crie** uma branch: `git checkout -b minha-feature`
4. **Commit** suas mudanças: `git commit -m "Adiciona nova feature"`
5. **Push** para a branch: `git push origin minha-feature`
6. **Abra** um Pull Request

### Padrões de Código

```bash
# Antes de commitar, sempre execute:
make lint     # Verifica estilo do código
make test     # Executa testes
make format   # Formata código automaticamente
```

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📞 Suporte

- **GitHub Issues**: [Reporte bugs ou sugira features](https://github.com/DanielRibauFotografia/autogen/issues)
- **Discussões**: [Tire dúvidas na comunidade](https://github.com/DanielRibauFotografia/autogen/discussions)
- **Email**: daniel@ribaufotografia.com

---

**Desenvolvido com ❤️ por Daniel Ribau Fotografia**

*"A inteligência artificial não substitui a criatividade humana, ela a potencializa."*