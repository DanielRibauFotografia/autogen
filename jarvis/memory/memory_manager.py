"""
Memory Manager - Sistema de Memória Centralizada do JARVIS

Este módulo implementa o sistema de memória baseado em neurociência cognitiva:
- Memória Episódica: Eventos específicos com contexto temporal
- Memória Semântica: Conhecimento geral e fatos
- Memória Procedural: Como fazer coisas (procedimentos)
- Memória Emocional: Contexto emocional e preferências
- Memória de Trabalho: Informação temporária para tarefas ativas

Autor: Daniel Ribau Fotografia
Data: 2024
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import asyncio
import logging


class MemoryManager:
    """
    Gerenciador central do sistema de memória do JARVIS.
    
    O sistema de memória é inspirado na neurociência cognitiva e permite
    que os agentes compartilhem conhecimento e aprendam com experiências passadas.
    """

    def __init__(self, memory_path: str = "/app/memory"):
        """
        Inicializa o sistema de memória.
        
        Args:
            memory_path: Caminho base para armazenamento da memória
        """
        self.memory_path = Path(memory_path)
        self.logger = logging.getLogger("jarvis.memory")
        
        # Cria estrutura de diretórios para cada tipo de memória
        self.memory_types = {
            'episodic': self.memory_path / 'episodic',
            'semantic': self.memory_path / 'semantic', 
            'procedural': self.memory_path / 'procedural',
            'emocional': self.memory_path / 'emocional',
            'trabalho': self.memory_path / 'trabalho'
        }
        
        # Cria diretórios se não existirem
        for memory_type, path in self.memory_types.items():
            path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("Sistema de memória inicializado")

    async def store_episodic(self, event_id: str, event_data: Dict[str, Any]) -> bool:
        """
        Armazena memória episódica (eventos específicos).
        
        Args:
            event_id: Identificador único do evento
            event_data: Dados do evento
            
        Returns:
            True se armazenado com sucesso
        """
        try:
            # Adiciona timestamp se não existe
            if 'timestamp' not in event_data:
                event_data['timestamp'] = datetime.now().isoformat()
            
            # Adiciona metadados
            episodic_entry = {
                'event_id': event_id,
                'type': 'episodic',
                'stored_at': datetime.now().isoformat(),
                'data': event_data
            }
            
            # Salva arquivo JSON
            file_path = self.memory_types['episodic'] / f"{event_id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(episodic_entry, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Memória episódica armazenada: {event_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao armazenar memória episódica: {e}")
            return False

    async def store_semantic(self, concept_id: str, knowledge_data: Dict[str, Any]) -> bool:
        """
        Armazena memória semântica (conhecimento geral).
        
        Args:
            concept_id: Identificador do conceito
            knowledge_data: Dados do conhecimento
            
        Returns:
            True se armazenado com sucesso
        """
        try:
            semantic_entry = {
                'concept_id': concept_id,
                'type': 'semantic',
                'stored_at': datetime.now().isoformat(),
                'knowledge': knowledge_data
            }
            
            file_path = self.memory_types['semantic'] / f"{concept_id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(semantic_entry, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Memória semântica armazenada: {concept_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao armazenar memória semântica: {e}")
            return False

    async def store_procedural(self, procedure_id: str, procedure_data: Dict[str, Any]) -> bool:
        """
        Armazena memória procedural (como fazer algo).
        
        Args:
            procedure_id: Identificador do procedimento
            procedure_data: Dados do procedimento
            
        Returns:
            True se armazenado com sucesso
        """
        try:
            procedural_entry = {
                'procedure_id': procedure_id,
                'type': 'procedural',
                'stored_at': datetime.now().isoformat(),
                'procedure': procedure_data
            }
            
            file_path = self.memory_types['procedural'] / f"{procedure_id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(procedural_entry, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Memória procedural armazenada: {procedure_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao armazenar memória procedural: {e}")
            return False

    async def store_emotional(self, context_id: str, emotional_data: Dict[str, Any]) -> bool:
        """
        Armazena memória emocional (contexto emocional).
        
        Args:
            context_id: Identificador do contexto
            emotional_data: Dados emocionais
            
        Returns:
            True se armazenado com sucesso
        """
        try:
            emotional_entry = {
                'context_id': context_id,
                'type': 'emocional',
                'stored_at': datetime.now().isoformat(),
                'emotional_context': emotional_data
            }
            
            file_path = self.memory_types['emocional'] / f"{context_id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(emotional_entry, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Memória emocional armazenada: {context_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao armazenar memória emocional: {e}")
            return False

    async def store_working(self, task_id: str, working_data: Dict[str, Any], ttl_hours: int = 24) -> bool:
        """
        Armazena memória de trabalho (temporária).
        
        Args:
            task_id: Identificador da tarefa
            working_data: Dados de trabalho
            ttl_hours: Tempo de vida em horas
            
        Returns:
            True se armazenado com sucesso
        """
        try:
            expires_at = datetime.now() + timedelta(hours=ttl_hours)
            
            working_entry = {
                'task_id': task_id,
                'type': 'trabalho',
                'stored_at': datetime.now().isoformat(),
                'expires_at': expires_at.isoformat(),
                'ttl_hours': ttl_hours,
                'working_data': working_data
            }
            
            file_path = self.memory_types['trabalho'] / f"{task_id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(working_entry, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Memória de trabalho armazenada: {task_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao armazenar memória de trabalho: {e}")
            return False

    async def get_episodic(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Recupera memória episódica específica."""
        return await self._get_memory('episodic', event_id)

    async def get_semantic(self, concept_id: str) -> Optional[Dict[str, Any]]:
        """Recupera memória semântica específica."""
        return await self._get_memory('semantic', concept_id)

    async def get_procedural(self, procedure_id: str) -> Optional[Dict[str, Any]]:
        """Recupera memória procedural específica."""
        return await self._get_memory('procedural', procedure_id)

    async def get_emotional(self, context_id: str) -> Optional[Dict[str, Any]]:
        """Recupera memória emocional específica."""
        return await self._get_memory('emocional', context_id)

    async def get_working(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Recupera memória de trabalho específica (se ainda válida)."""
        memory = await self._get_memory('trabalho', task_id)
        
        if memory and 'expires_at' in memory:
            expires_at = datetime.fromisoformat(memory['expires_at'])
            if datetime.now() > expires_at:
                # Memória expirada, remove
                await self.delete_working(task_id)
                return None
        
        return memory

    async def search_episodic(self, query: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Busca memórias episódicas baseado em critérios.
        
        Args:
            query: Critérios de busca
            limit: Limite de resultados
            
        Returns:
            Lista de memórias encontradas
        """
        return await self._search_memories('episodic', query, limit)

    async def search_semantic(self, query: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """Busca memórias semânticas."""
        return await self._search_memories('semantic', query, limit)

    async def delete_working(self, task_id: str) -> bool:
        """Remove memória de trabalho."""
        try:
            file_path = self.memory_types['trabalho'] / f"{task_id}.json"
            if file_path.exists():
                file_path.unlink()
                self.logger.debug(f"Memória de trabalho removida: {task_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Erro ao remover memória de trabalho: {e}")
            return False

    async def cleanup_expired_working_memory(self) -> int:
        """
        Remove memórias de trabalho expiradas.
        
        Returns:
            Número de memórias removidas
        """
        try:
            removed_count = 0
            working_dir = self.memory_types['trabalho']
            
            for file_path in working_dir.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        memory = json.load(f)
                    
                    if 'expires_at' in memory:
                        expires_at = datetime.fromisoformat(memory['expires_at'])
                        if datetime.now() > expires_at:
                            file_path.unlink()
                            removed_count += 1
                            
                except Exception as e:
                    self.logger.warning(f"Erro ao verificar expiração de {file_path}: {e}")
            
            if removed_count > 0:
                self.logger.info(f"Removidas {removed_count} memórias de trabalho expiradas")
            
            return removed_count
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza de memórias expiradas: {e}")
            return 0

    async def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do sistema de memória.
        
        Returns:
            Estatísticas de uso da memória
        """
        try:
            stats = {}
            
            for memory_type, path in self.memory_types.items():
                if path.exists():
                    files = list(path.glob("*.json"))
                    stats[memory_type] = {
                        'count': len(files),
                        'size_mb': sum(f.stat().st_size for f in files) / (1024 * 1024)
                    }
                else:
                    stats[memory_type] = {'count': 0, 'size_mb': 0}
            
            return {
                'status': 'success',
                'stats': stats,
                'total_files': sum(s['count'] for s in stats.values()),
                'total_size_mb': sum(s['size_mb'] for s in stats.values()),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar estatísticas: {e}")
            return {'status': 'error', 'message': str(e)}

    # Métodos auxiliares privados

    async def _get_memory(self, memory_type: str, memory_id: str) -> Optional[Dict[str, Any]]:
        """Método interno para recuperar memória."""
        try:
            file_path = self.memory_types[memory_type] / f"{memory_id}.json"
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                memory = json.load(f)
            
            return memory
            
        except Exception as e:
            self.logger.error(f"Erro ao recuperar memória {memory_type}/{memory_id}: {e}")
            return None

    async def _search_memories(self, memory_type: str, query: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """Método interno para buscar memórias."""
        try:
            memories = []
            memory_dir = self.memory_types[memory_type]
            
            if not memory_dir.exists():
                return memories
            
            for file_path in memory_dir.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        memory = json.load(f)
                    
                    # Verifica se a memória corresponde aos critérios de busca
                    if self._matches_query(memory, query):
                        memories.append(memory)
                        
                        if len(memories) >= limit:
                            break
                            
                except Exception as e:
                    self.logger.warning(f"Erro ao ler memória {file_path}: {e}")
            
            # Ordena por data de criação (mais recente primeiro)
            memories.sort(key=lambda x: x.get('stored_at', ''), reverse=True)
            
            return memories[:limit]
            
        except Exception as e:
            self.logger.error(f"Erro na busca de memórias {memory_type}: {e}")
            return []

    def _matches_query(self, memory: Dict[str, Any], query: Dict[str, Any]) -> bool:
        """Verifica se uma memória corresponde aos critérios de busca."""
        for key, value in query.items():
            # Primeiro verifica no nível superior
            if key in memory:
                if isinstance(value, str):
                    if value.lower() not in str(memory[key]).lower():
                        return False
                elif memory[key] != value:
                    return False
            # Busca aninhada nos dados
            elif 'data' in memory and isinstance(memory['data'], dict):
                data = memory['data']
                if key in data:
                    if isinstance(value, str):
                        if value.lower() not in str(data[key]).lower():
                            return False
                    elif data[key] != value:
                        return False
                else:
                    return False
            else:
                return False
        
        return True


# Função de conveniência para criar instância global
_global_memory_manager = None

def get_memory_manager(memory_path: str = "/app/memory") -> MemoryManager:
    """
    Retorna instância global do MemoryManager.
    
    Args:
        memory_path: Caminho para armazenamento (apenas na primeira chamada)
        
    Returns:
        Instância do MemoryManager
    """
    global _global_memory_manager
    if _global_memory_manager is None:
        _global_memory_manager = MemoryManager(memory_path)
    return _global_memory_manager