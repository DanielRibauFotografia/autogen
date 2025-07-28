"""
JARVIS CLI - Interface de Linha de Comando

Interface amigável para interagir com o sistema JARVIS.
Permite executar tarefas, monitorar agentes e gerenciar o sistema.

Autor: Daniel Ribau Fotografia
Data: 2024
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich import print as rprint

# Adiciona paths para importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import aio_pika
from aio_pika import connect, Message


class JarvisCLI:
    """Interface de linha de comando para o sistema JARVIS."""

    def __init__(self):
        """Inicializa a CLI."""
        self.console = Console()
        self.rabbitmq_url = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None

    async def connect(self) -> bool:
        """Conecta ao RabbitMQ."""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Conectando ao JARVIS...", total=None)
                
                self.connection = await connect(self.rabbitmq_url)
                self.channel = await self.connection.channel()
                
                progress.update(task, description="✅ Conectado!")
            
            return True
            
        except Exception as e:
            self.console.print(f"❌ [red]Erro ao conectar: {e}[/red]")
            return False

    async def disconnect(self) -> None:
        """Desconecta do RabbitMQ."""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()

    async def send_task_to_agent(self, agent_name: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Envia tarefa para um agente específico."""
        try:
            if not self.channel:
                await self.connect()
            
            message_data = {
                'type': 'task_request',
                'from': 'cli',
                'to': agent_name,
                'timestamp': datetime.now().isoformat(),
                'task': task_data
            }
            
            message_body = json.dumps(message_data).encode()
            message = Message(message_body)
            
            # Envia para queue específica do agente
            await self.channel.default_exchange.publish(
                message,
                routing_key=f"{agent_name}.queue"
            )
            
            return {'status': 'sent', 'message': f'Tarefa enviada para {agent_name}'}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    async def get_system_status(self) -> Dict[str, Any]:
        """Obtém status do sistema (simulado para demo)."""
        # Em implementação real, consultaria o orchestrator
        return {
            'system_status': 'running',
            'agents_online': 5,
            'agents_total': 7,
            'uptime': '2h 15m',
            'timestamp': datetime.now().isoformat()
        }

    def show_welcome(self) -> None:
        """Mostra tela de boas-vindas."""
        welcome_text = """
[bold blue]🤖 JARVIS - Sistema Multi-Agente[/bold blue]

Bem-vindo ao sistema inteligente de automação fotográfica!

[dim]Use os comandos abaixo para interagir com o sistema:[/dim]
        """
        
        panel = Panel(
            welcome_text,
            title="[bold green]Bem-vindo![/bold green]",
            border_style="blue"
        )
        
        self.console.print(panel)

    def show_status_table(self, status_data: Dict[str, Any]) -> None:
        """Mostra tabela de status do sistema."""
        table = Table(title="📊 Status do Sistema JARVIS")
        
        table.add_column("Componente", style="cyan", no_wrap=True)
        table.add_column("Status", style="green")
        table.add_column("Detalhes", style="dim")
        
        # Status geral
        table.add_row(
            "Sistema", 
            f"🟢 {status_data.get('system_status', 'unknown').upper()}",
            f"Tempo ativo: {status_data.get('uptime', 'N/A')}"
        )
        
        # Agentes
        agents_online = status_data.get('agents_online', 0)
        agents_total = status_data.get('agents_total', 0)
        
        if agents_online == agents_total:
            agent_status = "🟢 TODOS ONLINE"
        elif agents_online > 0:
            agent_status = "🟡 PARCIAL"
        else:
            agent_status = "🔴 OFFLINE"
        
        table.add_row(
            "Agentes",
            agent_status,
            f"{agents_online}/{agents_total} agentes conectados"
        )
        
        # RabbitMQ
        table.add_row(
            "Comunicação",
            "🟢 CONECTADO",
            "RabbitMQ operacional"
        )
        
        self.console.print(table)

    def show_agents_help(self) -> None:
        """Mostra ajuda sobre os agentes disponíveis."""
        agents_info = [
            ("📸 photo-agent", "Gerenciamento e processamento de fotos"),
            ("📈 marketing-agent", "Estratégias e campanhas de marketing"),
            ("📱 social-media-agent", "Gestão de redes sociais"),
            ("👥 crm-agent", "Relacionamento com clientes"),
            ("📅 calendar-agent", "Gerenciamento de agenda"),
            ("💰 finance-agent", "Controle financeiro"),
            ("✅ task-agent", "Gerenciamento de tarefas")
        ]
        
        table = Table(title="🤖 Agentes Disponíveis")
        table.add_column("Agente", style="cyan")
        table.add_column("Descrição", style="dim")
        
        for agent_name, description in agents_info:
            table.add_row(agent_name, description)
        
        self.console.print(table)

    def show_task_examples(self) -> None:
        """Mostra exemplos de tarefas."""
        examples = [
            ("Organizar fotos", "jarvis task photo-agent organize_photos --path /fotos"),
            ("Criar campanha", "jarvis task marketing-agent create_campaign --type ensaio_casal"),
            ("Agendar post", "jarvis task social-media-agent schedule_post --content 'Nova sessão!'"),
            ("Ver estatísticas", "jarvis status --detailed"),
            ("Ping agente", "jarvis ping photo-agent")
        ]
        
        table = Table(title="💡 Exemplos de Comandos")
        table.add_column("Descrição", style="cyan")
        table.add_column("Comando", style="green")
        
        for description, command in examples:
            table.add_row(description, command)
        
        self.console.print(table)


# Configuração do Click CLI
@click.group()
@click.version_option(version="1.0.0", prog_name="JARVIS CLI")
@click.pass_context
def cli(ctx):
    """
    🤖 JARVIS - Sistema Multi-Agente para Fotografia
    
    Interface de linha de comando para interagir com o sistema JARVIS.
    """
    ctx.ensure_object(dict)
    ctx.obj['cli'] = JarvisCLI()


@cli.command()
@click.pass_context
def welcome(ctx):
    """Mostra tela de boas-vindas e informações básicas."""
    jarvis_cli = ctx.obj['cli']
    jarvis_cli.show_welcome()
    jarvis_cli.show_agents_help()
    jarvis_cli.show_task_examples()


@cli.command()
@click.option('--detailed', is_flag=True, help='Mostra status detalhado')
@click.pass_context
def status(ctx, detailed):
    """Mostra status do sistema JARVIS."""
    async def _status():
        jarvis_cli = ctx.obj['cli']
        
        # Obtém status do sistema
        status_data = await jarvis_cli.get_system_status()
        
        jarvis_cli.show_status_table(status_data)
        
        if detailed:
            rprint("\n[dim]💡 Dica: Use 'jarvis task --help' para ver comandos de tarefas[/dim]")
    
    asyncio.run(_status())


@cli.command()
@click.argument('agent_name')
@click.pass_context
def ping(ctx, agent_name):
    """Testa conectividade com um agente específico."""
    async def _ping():
        jarvis_cli = ctx.obj['cli']
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=jarvis_cli.console
        ) as progress:
            task = progress.add_task(f"Testando {agent_name}...", total=None)
            
            result = await jarvis_cli.send_task_to_agent(agent_name, {
                'type': 'ping',
                'timestamp': datetime.now().isoformat()
            })
            
            if result['status'] == 'sent':
                progress.update(task, description=f"✅ {agent_name} alcançável")
                jarvis_cli.console.print(f"[green]✅ Ping enviado para {agent_name}[/green]")
            else:
                progress.update(task, description=f"❌ Erro ao conectar")
                jarvis_cli.console.print(f"[red]❌ Erro: {result['message']}[/red]")
    
    asyncio.run(_ping())


@cli.command()
@click.argument('agent_name')
@click.argument('task_type')
@click.option('--params', help='Parâmetros da tarefa em formato JSON')
@click.option('--path', help='Caminho de arquivo/diretório')
@click.option('--type', 'service_type', help='Tipo de serviço')
@click.option('--content', help='Conteúdo textual')
@click.pass_context
def task(ctx, agent_name, task_type, params, path, service_type, content):
    """
    Executa tarefa em um agente específico.
    
    Exemplos:
    jarvis task photo-agent organize_photos --path /fotos
    jarvis task marketing-agent create_campaign --type ensaio_casal
    """
    async def _task():
        jarvis_cli = ctx.obj['cli']
        
        # Constrói dados da tarefa
        task_data = {'type': task_type}
        
        # Adiciona parâmetros específicos
        if params:
            try:
                extra_params = json.loads(params)
                task_data.update(extra_params)
            except json.JSONDecodeError:
                jarvis_cli.console.print("[red]❌ Formato JSON inválido em --params[/red]")
                return
        
        if path:
            task_data['path'] = path
        if service_type:
            task_data['service_type'] = service_type
        if content:
            task_data['content'] = content
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=jarvis_cli.console
        ) as progress:
            task_progress = progress.add_task(f"Executando {task_type}...", total=None)
            
            result = await jarvis_cli.send_task_to_agent(agent_name, task_data)
            
            if result['status'] == 'sent':
                progress.update(task_progress, description="✅ Tarefa enviada")
                jarvis_cli.console.print(f"[green]✅ Tarefa '{task_type}' enviada para {agent_name}[/green]")
                jarvis_cli.console.print(f"[dim]📝 Dados: {json.dumps(task_data, indent=2)}[/dim]")
            else:
                progress.update(task_progress, description="❌ Erro")
                jarvis_cli.console.print(f"[red]❌ Erro: {result['message']}[/red]")
    
    asyncio.run(_task())


@cli.command()
@click.pass_context
def interactive(ctx):
    """Modo interativo do JARVIS CLI."""
    async def _interactive():
        jarvis_cli = ctx.obj['cli']
        
        jarvis_cli.console.print("[bold blue]🤖 Modo Interativo JARVIS[/bold blue]")
        jarvis_cli.console.print("[dim]Digite 'help' para ajuda ou 'quit' para sair[/dim]\n")
        
        # Conecta ao sistema
        if not await jarvis_cli.connect():
            return
        
        try:
            while True:
                command = Prompt.ask("[bold cyan]JARVIS[/bold cyan]")
                
                if command.lower() in ['quit', 'exit', 'sair']:
                    jarvis_cli.console.print("👋 Até logo!")
                    break
                
                elif command.lower() == 'help':
                    jarvis_cli.show_task_examples()
                
                elif command.lower() == 'status':
                    status_data = await jarvis_cli.get_system_status()
                    jarvis_cli.show_status_table(status_data)
                
                elif command.lower() == 'agents':
                    jarvis_cli.show_agents_help()
                
                elif command.startswith('ping '):
                    agent_name = command.split(' ', 1)[1]
                    result = await jarvis_cli.send_task_to_agent(agent_name, {'type': 'ping'})
                    if result['status'] == 'sent':
                        jarvis_cli.console.print(f"[green]✅ Ping enviado para {agent_name}[/green]")
                    else:
                        jarvis_cli.console.print(f"[red]❌ Erro: {result['message']}[/red]")
                
                else:
                    jarvis_cli.console.print("[yellow]❓ Comando não reconhecido. Digite 'help' para ajuda.[/yellow]")
        
        finally:
            await jarvis_cli.disconnect()
    
    asyncio.run(_interactive())


@cli.command()
@click.pass_context
def monitor(ctx):
    """Monitora sistema em tempo real (demo)."""
    jarvis_cli = ctx.obj['cli']
    
    jarvis_cli.console.print("[bold blue]📊 Monitor do Sistema JARVIS[/bold blue]")
    jarvis_cli.console.print("[dim]Pressione Ctrl+C para sair[/dim]\n")
    
    try:
        while True:
            import time
            
            # Simula dados de monitoramento
            timestamp = datetime.now().strftime("%H:%M:%S")
            jarvis_cli.console.print(f"[{timestamp}] Sistema operacional - 5/7 agentes online")
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        jarvis_cli.console.print("\n👋 Monitor finalizado")


if __name__ == '__main__':
    cli()