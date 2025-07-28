"""
Base Agent - Classe base para todos os agentes do sistema JARVIS

Esta classe fornece a estrutura fundamental que todos os agentes especializados
devem seguir, incluindo:
- Conexão com RabbitMQ
- Sistema de logging
- Gerenciamento de memória
- Padrões de comunicação assíncrona

Autor: Daniel Ribau Fotografia
Data: 2024
"""

import asyncio
import json
import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

import aio_pika
from aio_pika import Message, connect
from aio_pika.abc import AbstractIncomingMessage


class BaseAgent(ABC):
    """
    Classe base para todos os agentes do sistema JARVIS.
    
    Esta classe implementa funcionalidades comuns a todos os agentes:
    - Conexão assíncrona com RabbitMQ
    - Sistema de logging estruturado
    - Padrões de comunicação pub/sub
    - Interface padronizada para processamento de mensagens
    """

    def __init__(self, agent_name: str, log_level: str = "INFO"):
        """
        Inicializa o agente base.
        
        Args:
            agent_name: Nome único do agente (ex: 'photo-agent')
            log_level: Nível de logging ('DEBUG', 'INFO', 'WARNING', 'ERROR')
        """
        self.agent_name = agent_name
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchange: Optional[aio_pika.Exchange] = None
        self.queue: Optional[aio_pika.Queue] = None
        
        # Configuração de logging
        self._setup_logging(log_level)
        
        # URLs de conexão (pode ser sobrescrita por variável de ambiente)
        self.rabbitmq_url = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')
        
        self.logger.info(f"Agente {agent_name} inicializado")

    def _setup_logging(self, log_level: str) -> None:
        """Configura o sistema de logging do agente."""
        # Cria logger específico para este agente
        self.logger = logging.getLogger(f"jarvis.{self.agent_name}")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Remove handlers existentes para evitar duplicação
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Configura handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level.upper()))
        
        # Formato de log com informações do agente
        formatter = logging.Formatter(
            f'%(asctime)s - {self.agent_name} - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)

    async def connect_to_rabbitmq(self) -> None:
        """
        Estabelece conexão com RabbitMQ e configura exchange/queue.
        
        Raises:
            ConnectionError: Se não conseguir conectar ao RabbitMQ
        """
        try:
            # Conecta ao RabbitMQ
            self.connection = await connect(self.rabbitmq_url)
            self.channel = await self.connection.channel()
            
            # Configura exchange principal (fanout para broadcast)
            self.exchange = await self.channel.declare_exchange(
                'jarvis.events', 
                aio_pika.ExchangeType.FANOUT,
                durable=True
            )
            
            # Cria queue específica para este agente
            self.queue = await self.channel.declare_queue(
                f"{self.agent_name}.queue",
                durable=True
            )
            
            # Conecta queue ao exchange
            await self.queue.bind(self.exchange)
            
            self.logger.info("Conectado ao RabbitMQ com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao conectar com RabbitMQ: {e}")
            raise ConnectionError(f"Falha na conexão com RabbitMQ: {e}")

    async def start_consuming(self) -> None:
        """
        Inicia o consumo de mensagens da queue.
        
        Este método configura o agente para escutar mensagens
        e processá-las conforme chegam.
        """
        if not self.queue:
            raise RuntimeError("Queue não configurada. Execute connect_to_rabbitmq() primeiro.")
        
        # Configura consumo de mensagens
        await self.queue.consume(self._handle_message)
        self.logger.info(f"Agente {self.agent_name} iniciou consumo de mensagens")

    async def _handle_message(self, message: AbstractIncomingMessage) -> None:
        """
        Manipula mensagens recebidas da queue.
        
        Args:
            message: Mensagem recebida do RabbitMQ
        """
        async with message.process():
            try:
                # Decodifica mensagem JSON
                message_data = json.loads(message.body.decode())
                
                self.logger.debug(f"Mensagem recebida: {message_data}")
                
                # Processa mensagem usando método abstrato
                await self.process_message(message_data)
                
            except json.JSONDecodeError as e:
                self.logger.error(f"Erro ao decodificar mensagem JSON: {e}")
            except Exception as e:
                self.logger.error(f"Erro ao processar mensagem: {e}")

    async def publish_message(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Publica uma mensagem no exchange para outros agentes.
        
        Args:
            event_type: Tipo do evento (ex: 'photos.processed', 'task.completed')
            data: Dados da mensagem
        """
        if not self.exchange:
            raise RuntimeError("Exchange não configurado. Execute connect_to_rabbitmq() primeiro.")
        
        # Prepara mensagem com metadados
        message_data = {
            'event_type': event_type,
            'agent_source': self.agent_name,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        # Converte para JSON e publica
        message_body = json.dumps(message_data).encode()
        message = Message(message_body)
        
        await self.exchange.publish(message, routing_key='')
        
        self.logger.info(f"Mensagem publicada: {event_type}")
        self.logger.debug(f"Dados da mensagem: {message_data}")

    async def send_direct_message(self, target_agent: str, data: Dict[str, Any]) -> None:
        """
        Envia mensagem direta para um agente específico.
        
        Args:
            target_agent: Nome do agente de destino
            data: Dados da mensagem
        """
        if not self.channel:
            raise RuntimeError("Canal não configurado. Execute connect_to_rabbitmq() primeiro.")
        
        # Prepara mensagem direta
        message_data = {
            'type': 'direct_message',
            'from': self.agent_name,
            'to': target_agent,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        # Envia para queue específica do agente de destino
        target_queue = f"{target_agent}.queue"
        message_body = json.dumps(message_data).encode()
        message = Message(message_body)
        
        await self.channel.default_exchange.publish(
            message, 
            routing_key=target_queue
        )
        
        self.logger.info(f"Mensagem direta enviada para {target_agent}")

    async def start(self) -> None:
        """
        Inicia o agente: conecta ao RabbitMQ e começa a consumir mensagens.
        
        Este é o método principal para iniciar um agente.
        """
        self.logger.info(f"Iniciando agente {self.agent_name}...")
        
        await self.connect_to_rabbitmq()
        await self.start_consuming()
        
        # Publica evento de que o agente está online
        await self.publish_message('agent.started', {
            'agent_name': self.agent_name,
            'status': 'online'
        })
        
        self.logger.info(f"Agente {self.agent_name} iniciado com sucesso")

    async def stop(self) -> None:
        """Para o agente e fecha conexões."""
        self.logger.info(f"Parando agente {self.agent_name}...")
        
        # Publica evento de que o agente está saindo
        if self.exchange:
            await self.publish_message('agent.stopped', {
                'agent_name': self.agent_name,
                'status': 'offline'
            })
        
        # Fecha conexões
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
        
        self.logger.info(f"Agente {self.agent_name} parado")

    @abstractmethod
    async def process_message(self, message: Dict[str, Any]) -> None:
        """
        Processa uma mensagem recebida.
        
        Este método deve ser implementado por cada agente especializado
        para definir como as mensagens são processadas.
        
        Args:
            message: Dados da mensagem recebida
        """
        pass

    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma tarefa específica do agente.
        
        Este método deve ser implementado por cada agente especializado
        para definir suas funcionalidades específicas.
        
        Args:
            task: Dados da tarefa a ser executada
            
        Returns:
            Resultado da execução da tarefa
        """
        pass

    def __repr__(self) -> str:
        """Representação string do agente."""
        return f"<{self.__class__.__name__}(name='{self.agent_name}')>"