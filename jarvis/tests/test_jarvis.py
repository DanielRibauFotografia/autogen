"""
Testes básicos para o sistema JARVIS

Este módulo contém testes unitários para validar
o funcionamento dos componentes principais.

Autor: Daniel Ribau Fotografia
Data: 2024
"""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path

# Importa componentes para teste
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.memory_manager import MemoryManager
from agents.base.base_agent import BaseAgent


class TestMemoryManager:
    """Testes para o sistema de memória."""
    
    @pytest.fixture
    async def memory_manager(self):
        """Cria instância temporária do MemoryManager."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield MemoryManager(temp_dir)
    
    @pytest.mark.asyncio
    async def test_store_episodic(self, memory_manager):
        """Testa armazenamento de memória episódica."""
        event_id = "test_event_001"
        event_data = {
            "description": "Teste de evento",
            "type": "test",
            "value": 42
        }
        
        result = await memory_manager.store_episodic(event_id, event_data)
        assert result is True
        
        # Verifica se foi armazenado
        retrieved = await memory_manager.get_episodic(event_id)
        assert retrieved is not None
        assert retrieved['event_id'] == event_id
        assert retrieved['data'] == event_data
    
    @pytest.mark.asyncio
    async def test_store_semantic(self, memory_manager):
        """Testa armazenamento de memória semântica."""
        concept_id = "test_concept"
        knowledge_data = {
            "definition": "Conceito de teste",
            "examples": ["exemplo1", "exemplo2"],
            "related": ["conceito_a", "conceito_b"]
        }
        
        result = await memory_manager.store_semantic(concept_id, knowledge_data)
        assert result is True
        
        # Verifica se foi armazenado
        retrieved = await memory_manager.get_semantic(concept_id)
        assert retrieved is not None
        assert retrieved['concept_id'] == concept_id
        assert retrieved['knowledge'] == knowledge_data
    
    @pytest.mark.asyncio
    async def test_working_memory_expiration(self, memory_manager):
        """Testa expiração da memória de trabalho."""
        task_id = "test_task"
        working_data = {"status": "active", "progress": 50}
        
        # Armazena com TTL muito baixo (para teste)
        result = await memory_manager.store_working(task_id, working_data, ttl_hours=0.001)
        assert result is True
        
        # Aguarda expiração (alguns milissegundos)
        await asyncio.sleep(0.1)
        
        # Verifica se expirou
        retrieved = await memory_manager.get_working(task_id)
        assert retrieved is None
    
    @pytest.mark.asyncio
    async def test_search_episodic(self, memory_manager):
        """Testa busca em memória episódica."""
        # Armazena vários eventos
        events = [
            ("event1", {"type": "photo", "client": "João"}),
            ("event2", {"type": "photo", "client": "Maria"}),
            ("event3", {"type": "marketing", "client": "João"}),
        ]
        
        for event_id, event_data in events:
            await memory_manager.store_episodic(event_id, event_data)
        
        # Busca por tipo
        results = await memory_manager.search_episodic({"type": "photo"})
        assert len(results) == 2
        
        # Busca por cliente
        results = await memory_manager.search_episodic({"client": "João"})
        assert len(results) == 2
    
    @pytest.mark.asyncio
    async def test_memory_stats(self, memory_manager):
        """Testa estatísticas da memória."""
        # Armazena alguns itens
        await memory_manager.store_episodic("test1", {"data": "test"})
        await memory_manager.store_semantic("concept1", {"info": "test"})
        
        stats = await memory_manager.get_stats()
        
        assert stats['status'] == 'success'
        assert stats['stats']['episodic']['count'] >= 1
        assert stats['stats']['semantic']['count'] >= 1
        assert stats['total_files'] >= 2


class MockAgent(BaseAgent):
    """Agente mock para testes."""
    
    def __init__(self):
        super().__init__("test-agent")
        self.processed_messages = []
        self.executed_tasks = []
    
    async def process_message(self, message):
        self.processed_messages.append(message)
    
    async def execute_task(self, task):
        self.executed_tasks.append(task)
        return {"status": "success", "task_type": task.get("type", "unknown")}


class TestBaseAgent:
    """Testes para a classe base de agentes."""
    
    def test_agent_initialization(self):
        """Testa inicialização do agente."""
        agent = MockAgent()
        assert agent.agent_name == "test-agent"
        assert agent.rabbitmq_url is not None
    
    @pytest.mark.asyncio
    async def test_execute_task(self):
        """Testa execução de tarefa."""
        agent = MockAgent()
        
        task = {"type": "test_task", "data": "test"}
        result = await agent.execute_task(task)
        
        assert result["status"] == "success"
        assert result["task_type"] == "test_task"
        assert len(agent.executed_tasks) == 1


def test_jarvis_structure():
    """Testa se a estrutura do projeto está correta."""
    jarvis_path = Path(__file__).parent.parent
    
    # Verifica diretórios principais
    required_dirs = [
        "agents", "memory", "orchestrator", "cli", "examples"
    ]
    
    for dir_name in required_dirs:
        dir_path = jarvis_path / dir_name
        assert dir_path.exists(), f"Diretório {dir_name} não encontrado"
    
    # Verifica arquivos principais
    required_files = [
        "README.md", "requirements.txt", "docker-compose.yml", "Makefile"
    ]
    
    for file_name in required_files:
        file_path = jarvis_path / file_name
        assert file_path.exists(), f"Arquivo {file_name} não encontrado"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])