# memory/__init__.py
"""
Sistema de Memória Centralizada do JARVIS

Este módulo implementa o sistema de memória baseado em neurociência cognitiva
que permite aos agentes compartilhar conhecimento e aprender com experiências.
"""

from .memory_manager import MemoryManager, get_memory_manager

__all__ = ['MemoryManager', 'get_memory_manager']