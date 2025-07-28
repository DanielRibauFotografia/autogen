"""
Orchestrator - Orquestrador Principal do Sistema JARVIS

O Orchestrator é responsável por:
- Inicializar e monitorar todos os agentes
- Coordenar comunicação entre agentes
- Gerenciar o ciclo de vida do sistema
- Monitorar saúde dos componentes
- Distribuir tarefas complexas

Autor: Daniel Ribau Fotografia
Data: 2024
"""

import asyncio
import json
import logging
import os
import signal
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

import aio_pika
from aio_pika import connect


class JarvisOrchestrator:
    """
    Orquestrador principal do sistema JARVIS.
    
    Gerencia todos os agentes e coordena a comunicação entre eles,
    além de monitorar a saúde geral do sistema.
    """

    def __init__(self):
        """Inicializa o orquestrador."""
        self.logger = self._setup_logging()
        
        # Configurações de conexão
        self.rabbitmq_url = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')
        
        # Estado do sistema
        self.agents = {}
        self.system_status = 'starting'
        self.start_time = datetime.now()
        
        # Conexões RabbitMQ
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchange: Optional[aio_pika.Exchange] = None
        self.management_queue: Optional[aio_pika.Queue] = None
        
        # Flag para shutdown gracioso
        self.shutdown_requested = False
        
        # Lista de agentes esperados
        self.expected_agents = [
            'photo-agent',
            'marketing-agent', 
            'social-media-agent',
            'crm-agent',
            'calendar-agent',
            'finance-agent',
            'task-agent'
        ]
        
        self.logger.info("Orquestrador JARVIS inicializado")

    def _setup_logging(self) -> logging.Logger:
        """Configura sistema de logging."""
        logger = logging.getLogger("jarvis.orchestrator")
        logger.setLevel(logging.INFO)
        
        # Remove handlers existentes
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formato de log
        formatter = logging.Formatter(
            '%(asctime)s - ORCHESTRATOR - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        return logger

    async def start(self) -> None:
        """Inicia o orquestrador e todos os serviços."""
        self.logger.info("🚀 Iniciando sistema JARVIS...")
        
        try:
            # Configura handlers para shutdown gracioso
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            # Conecta ao RabbitMQ
            await self._connect_to_rabbitmq()
            
            # Inicia monitoramento de agentes
            await self._start_agent_monitoring()
            
            # Atualiza status do sistema
            self.system_status = 'running'
            
            self.logger.info("✅ Sistema JARVIS iniciado com sucesso")
            await self._publish_system_event('system.started', {
                'start_time': self.start_time.isoformat(),
                'expected_agents': self.expected_agents
            })
            
            # Loop principal de monitoramento
            await self._main_loop()
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao iniciar sistema: {e}")
            self.system_status = 'error'
            raise

    async def _connect_to_rabbitmq(self) -> None:
        """Conecta ao RabbitMQ e configura exchanges/queues."""
        try:
            self.logger.info("Conectando ao RabbitMQ...")
            
            # Conecta
            self.connection = await connect(self.rabbitmq_url)
            self.channel = await self.connection.channel()
            
            # Configura exchange principal
            self.exchange = await self.channel.declare_exchange(
                'jarvis.events',
                aio_pika.ExchangeType.FANOUT,
                durable=True
            )
            
            # Queue para gerenciamento
            self.management_queue = await self.channel.declare_queue(
                'orchestrator.management',
                durable=True
            )
            
            # Conecta queue ao exchange
            await self.management_queue.bind(self.exchange)
            
            self.logger.info("✅ Conectado ao RabbitMQ")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao conectar com RabbitMQ: {e}")
            raise

    async def _start_agent_monitoring(self) -> None:
        """Inicia monitoramento de agentes."""
        self.logger.info("Iniciando monitoramento de agentes...")
        
        # Configura consumo de mensagens
        await self.management_queue.consume(self._handle_agent_message)
        
        # Inicializa estado dos agentes
        for agent_name in self.expected_agents:
            self.agents[agent_name] = {
                'status': 'expected',
                'last_seen': None,
                'messages_received': 0,
                'errors': 0
            }

    async def _handle_agent_message(self, message) -> None:
        """Processa mensagens dos agentes."""
        async with message.process():
            try:
                message_data = json.loads(message.body.decode())
                event_type = message_data.get('event_type', '')
                agent_source = message_data.get('agent_source', '')
                
                # Atualiza informações do agente
                if agent_source in self.agents:
                    self.agents[agent_source]['last_seen'] = datetime.now()
                    self.agents[agent_source]['messages_received'] += 1
                    
                    if event_type == 'agent.started':
                        self.agents[agent_source]['status'] = 'online'
                        self.logger.info(f"✅ Agente {agent_source} conectado")
                        
                    elif event_type == 'agent.stopped':
                        self.agents[agent_source]['status'] = 'offline'
                        self.logger.info(f"⚠️ Agente {agent_source} desconectado")
                
                # Log de eventos importantes
                if event_type in ['agent.started', 'agent.stopped', 'system.error']:
                    self.logger.info(f"Evento recebido: {event_type} de {agent_source}")
                
            except Exception as e:
                self.logger.error(f"Erro ao processar mensagem: {e}")

    async def _main_loop(self) -> None:
        """Loop principal de monitoramento."""
        self.logger.info("Iniciando loop principal de monitoramento...")
        
        while not self.shutdown_requested:
            try:
                # Verifica saúde dos agentes
                await self._check_agent_health()
                
                # Publica estatísticas do sistema
                await self._publish_system_stats()
                
                # Aguarda próximo ciclo
                await asyncio.sleep(30)  # Verifica a cada 30 segundos
                
            except Exception as e:
                self.logger.error(f"Erro no loop principal: {e}")
                await asyncio.sleep(5)

    async def _check_agent_health(self) -> None:
        """Verifica saúde de todos os agentes."""
        current_time = datetime.now()
        
        for agent_name, agent_info in self.agents.items():
            last_seen = agent_info.get('last_seen')
            
            if last_seen is None:
                # Agente nunca se conectou
                if agent_info['status'] != 'expected':
                    agent_info['status'] = 'expected'
                    self.logger.warning(f"⏳ Aguardando agente {agent_name}")
                    
            else:
                # Verifica se agente está silent há muito tempo
                silence_time = (current_time - last_seen).total_seconds()
                
                if silence_time > 300:  # 5 minutos sem sinais
                    if agent_info['status'] != 'unresponsive':
                        agent_info['status'] = 'unresponsive'
                        self.logger.warning(f"⚠️ Agente {agent_name} não responde há {silence_time:.0f}s")
                        
                        await self._publish_system_event('agent.unresponsive', {
                            'agent_name': agent_name,
                            'silence_duration': silence_time
                        })

    async def _publish_system_stats(self) -> None:
        """Publica estatísticas do sistema."""
        try:
            uptime = (datetime.now() - self.start_time).total_seconds()
            
            stats = {
                'system_status': self.system_status,
                'uptime_seconds': uptime,
                'agents': dict(self.agents),
                'agents_online': len([a for a in self.agents.values() if a['status'] == 'online']),
                'agents_expected': len(self.expected_agents),
                'timestamp': datetime.now().isoformat()
            }
            
            await self._publish_system_event('system.stats', stats)
            
        except Exception as e:
            self.logger.error(f"Erro ao publicar estatísticas: {e}")

    async def _publish_system_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Publica evento do sistema."""
        try:
            if not self.exchange:
                return
            
            message_data = {
                'event_type': event_type,
                'agent_source': 'orchestrator',
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            
            message_body = json.dumps(message_data).encode()
            message = aio_pika.Message(message_body)
            
            await self.exchange.publish(message, routing_key='')
            
        except Exception as e:
            self.logger.error(f"Erro ao publicar evento: {e}")

    async def execute_distributed_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa tarefa distribuída entre múltiplos agentes.
        
        Args:
            task_data: Dados da tarefa
            
        Returns:
            Resultado da execução
        """
        try:
            task_type = task_data.get('type', '')
            self.logger.info(f"Executando tarefa distribuída: {task_type}")
            
            # Exemplo de coordenação de tarefa complexa
            if task_type == 'complete_photo_workflow':
                return await self._execute_photo_workflow(task_data)
            
            elif task_type == 'marketing_campaign_launch':
                return await self._execute_marketing_campaign(task_data)
            
            elif task_type == 'client_onboarding':
                return await self._execute_client_onboarding(task_data)
            
            else:
                return {
                    'status': 'error',
                    'message': f'Tipo de tarefa não reconhecido: {task_type}'
                }
                
        except Exception as e:
            self.logger.error(f"Erro na tarefa distribuída: {e}")
            return {'status': 'error', 'message': str(e)}

    async def _execute_photo_workflow(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Executa workflow completo de processamento de fotos."""
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 1. PhotoAgent: organiza e processa fotos
        await self._send_task_to_agent('photo-agent', {
            'type': 'organize_photos',
            'path': task_data.get('photo_path', '/app/photos'),
            'workflow_id': workflow_id
        })
        
        # 2. MarketingAgent: cria sugestões de conteúdo
        await self._send_task_to_agent('marketing-agent', {
            'type': 'suggest_content',
            'context': {'photos_processed': True},
            'workflow_id': workflow_id
        })
        
        # 3. SocialMediaAgent: programa posts
        await self._send_task_to_agent('social-media-agent', {
            'type': 'schedule_posts',
            'workflow_id': workflow_id
        })
        
        return {
            'status': 'initiated',
            'workflow_id': workflow_id,
            'message': 'Workflow de fotos iniciado'
        }

    async def _execute_marketing_campaign(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Executa lançamento de campanha de marketing."""
        campaign_data = task_data.get('campaign_data', {})
        
        # 1. MarketingAgent: cria campanha
        await self._send_task_to_agent('marketing-agent', {
            'type': 'create_campaign',
            'campaign_data': campaign_data
        })
        
        # 2. SocialMediaAgent: prepara posts
        await self._send_task_to_agent('social-media-agent', {
            'type': 'prepare_campaign_posts',
            'campaign_data': campaign_data
        })
        
        # 3. CRMAgent: identifica público-alvo
        await self._send_task_to_agent('crm-agent', {
            'type': 'segment_audience',
            'campaign_data': campaign_data
        })
        
        return {
            'status': 'initiated',
            'message': 'Campanha de marketing iniciada'
        }

    async def _execute_client_onboarding(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Executa processo de onboarding de novo cliente."""
        client_data = task_data.get('client_data', {})
        
        # 1. CRMAgent: registra cliente
        await self._send_task_to_agent('crm-agent', {
            'type': 'register_client',
            'client_data': client_data
        })
        
        # 2. PhotoAgent: cria pasta do cliente
        await self._send_task_to_agent('photo-agent', {
            'type': 'create_client_folder',
            'client_name': client_data.get('name', '')
        })
        
        # 3. CalendarAgent: agenda primeira consulta
        await self._send_task_to_agent('calendar-agent', {
            'type': 'schedule_consultation',
            'client_data': client_data
        })
        
        return {
            'status': 'initiated',
            'message': 'Onboarding de cliente iniciado'
        }

    async def _send_task_to_agent(self, agent_name: str, task_data: Dict[str, Any]) -> None:
        """Envia tarefa específica para um agente."""
        try:
            if not self.channel:
                return
            
            message_data = {
                'type': 'task_request',
                'from': 'orchestrator',
                'to': agent_name,
                'timestamp': datetime.now().isoformat(),
                'task': task_data
            }
            
            message_body = json.dumps(message_data).encode()
            message = aio_pika.Message(message_body)
            
            # Envia para queue específica do agente
            await self.channel.default_exchange.publish(
                message,
                routing_key=f"{agent_name}.queue"
            )
            
            self.logger.debug(f"Tarefa enviada para {agent_name}: {task_data.get('type', 'unknown')}")
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar tarefa para {agent_name}: {e}")

    def _signal_handler(self, signum, frame) -> None:
        """Handler para sinais de sistema (Ctrl+C, etc.)."""
        self.logger.info(f"Sinal {signum} recebido. Iniciando shutdown gracioso...")
        self.shutdown_requested = True

    async def stop(self) -> None:
        """Para o orquestrador graciosamente."""
        self.logger.info("⏹️ Parando orquestrador...")
        
        self.system_status = 'stopping'
        
        # Publica evento de shutdown
        await self._publish_system_event('system.stopping', {
            'stop_time': datetime.now().isoformat()
        })
        
        # Fecha conexões
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
        
        self.system_status = 'stopped'
        self.logger.info("✅ Orquestrador parado")

    async def get_system_status(self) -> Dict[str, Any]:
        """Retorna status completo do sistema."""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'system_status': self.system_status,
            'start_time': self.start_time.isoformat(),
            'uptime_seconds': uptime,
            'uptime_human': f"{uptime // 3600:.0f}h {(uptime % 3600) // 60:.0f}m",
            'agents': dict(self.agents),
            'agents_summary': {
                'total': len(self.expected_agents),
                'online': len([a for a in self.agents.values() if a['status'] == 'online']),
                'offline': len([a for a in self.agents.values() if a['status'] == 'offline']),
                'unresponsive': len([a for a in self.agents.values() if a['status'] == 'unresponsive']),
                'expected': len([a for a in self.agents.values() if a['status'] == 'expected'])
            },
            'timestamp': datetime.now().isoformat()
        }


async def main():
    """Função principal do orquestrador."""
    orchestrator = JarvisOrchestrator()
    
    try:
        await orchestrator.start()
    except KeyboardInterrupt:
        print("\nShutdown solicitado pelo usuário...")
    except Exception as e:
        orchestrator.logger.error(f"Erro fatal: {e}")
    finally:
        await orchestrator.stop()


if __name__ == "__main__":
    asyncio.run(main())