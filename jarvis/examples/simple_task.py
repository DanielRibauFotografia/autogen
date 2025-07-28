"""
Exemplo Simples de Tarefa no JARVIS

Este exemplo mostra como executar uma tarefa simples
usando o sistema JARVIS.

Autor: Daniel Ribau Fotografia
Data: 2024
"""

import asyncio
import sys
import os

# Adiciona paths para importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.photo_agent.agent import PhotoAgent
from memory.memory_manager import MemoryManager


async def simple_task_example():
    """
    Exemplo simples: organizar fotos e armazenar na memória.
    """
    print("🤖 JARVIS - Exemplo de Tarefa Simples")
    print("=" * 40)
    
    # Inicializa componentes
    print("📸 Inicializando PhotoAgent...")
    photo_agent = PhotoAgent()
    
    print("🧠 Inicializando sistema de memória...")
    memory_manager = MemoryManager()
    
    try:
        # Conecta PhotoAgent (sem RabbitMQ para este exemplo simples)
        print("🔗 Configurando PhotoAgent...")
        
        # Executa tarefa de análise de foto
        print("\n📋 Executando tarefa: Analisar foto...")
        
        # Simula análise de uma foto
        resultado_analise = await photo_agent.execute_task({
            'type': 'analyze_photo',
            'photo_path': '/demo/sample_photo.jpg'  # Arquivo simulado
        })
        
        print(f"📊 Resultado da análise: {resultado_analise}")
        
        # Armazena resultado na memória episódica
        print("\n🧠 Armazenando na memória episódica...")
        
        evento_id = f"photo_analysis_{int(asyncio.get_event_loop().time())}"
        sucesso = await memory_manager.store_episodic(evento_id, {
            'event_type': 'photo_analysis',
            'photo_path': '/demo/sample_photo.jpg',
            'analysis_result': resultado_analise,
            'agent': 'photo-agent'
        })
        
        if sucesso:
            print(f"✅ Evento armazenado na memória: {evento_id}")
        else:
            print("❌ Erro ao armazenar na memória")
        
        # Armazena conhecimento na memória semântica
        print("\n🧠 Armazenando conhecimento semântico...")
        
        conhecimento_sucesso = await memory_manager.store_semantic('photo_analysis_procedures', {
            'description': 'Como analisar fotos no sistema JARVIS',
            'steps': [
                'Verificar se arquivo existe',
                'Extrair metadados EXIF se disponível',
                'Analisar tamanho e formato',
                'Retornar dados estruturados'
            ],
            'best_practices': [
                'Sempre verificar integridade do arquivo',
                'Fazer backup antes de processar',
                'Logar resultados para auditoria'
            ]
        })
        
        if conhecimento_sucesso:
            print("✅ Conhecimento armazenado na memória semântica")
        
        # Demonstra busca na memória
        print("\n🔍 Buscando eventos na memória...")
        
        eventos_encontrados = await memory_manager.search_episodic({
            'event_type': 'photo_analysis'
        }, limit=5)
        
        print(f"📋 Encontrados {len(eventos_encontrados)} eventos de análise de fotos")
        
        # Mostra estatísticas da memória
        print("\n📊 Estatísticas da memória:")
        stats = await memory_manager.get_stats()
        
        if stats['status'] == 'success':
            for memory_type, info in stats['stats'].items():
                print(f"   {memory_type}: {info['count']} itens ({info['size_mb']:.2f} MB)")
        
        print("\n🎉 Tarefa simples concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Executando exemplo de tarefa simples...")
    print("Este exemplo não requer RabbitMQ rodando.\n")
    
    try:
        asyncio.run(simple_task_example())
    except KeyboardInterrupt:
        print("\n👋 Exemplo interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")