"""
Exemplo de Comunicação Entre Agentes

Este exemplo demonstra como os agentes do JARVIS se comunicam
entre si usando RabbitMQ para executar um workflow completo.

Cenário: Processamento de fotos de uma sessão seguido de
criação de conteúdo para redes sociais.

Autor: Daniel Ribau Fotografia
Data: 2024
"""

import asyncio
import sys
import os
from datetime import datetime

# Adiciona paths para importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.photo_agent.agent import PhotoAgent
from agents.marketing_agent.agent import MarketingAgent


async def demo_communication():
    """
    Demonstra comunicação entre PhotoAgent e MarketingAgent.
    
    Fluxo:
    1. PhotoAgent processa fotos de uma sessão
    2. MarketingAgent recebe notificação
    3. MarketingAgent cria sugestões de conteúdo
    4. Planeja posts para redes sociais
    """
    print("🤖 JARVIS - Demo de Comunicação Entre Agentes")
    print("=" * 50)
    
    # Inicializa agentes
    print("📸 Inicializando PhotoAgent...")
    photo_agent = PhotoAgent()
    
    print("📈 Inicializando MarketingAgent...")
    marketing_agent = MarketingAgent()
    
    try:
        # Conecta agentes
        print("\n🔗 Conectando agentes ao RabbitMQ...")
        await photo_agent.connect_to_rabbitmq()
        await marketing_agent.connect_to_rabbitmq()
        
        # Inicia consumo de mensagens (não bloqueia)
        print("👂 Iniciando escuta de mensagens...")
        await photo_agent.start_consuming()
        await marketing_agent.start_consuming()
        
        # Simula processamento de fotos
        print("\n📸 Processando fotos da sessão...")
        fotos_para_processar = [
            "/demo/fotos/IMG_001.jpg",
            "/demo/fotos/IMG_002.jpg", 
            "/demo/fotos/IMG_003.jpg",
            "/demo/fotos/IMG_004.jpg",
            "/demo/fotos/IMG_005.jpg"
        ]
        
        # PhotoAgent processa fotos
        resultado_fotos = await photo_agent.execute_task({
            'type': 'process_photos',
            'photos': fotos_para_processar
        })
        
        print(f"✅ Fotos processadas: {resultado_fotos}")
        
        # Publica evento para outros agentes
        await photo_agent.publish_message('photos.processed', {
            'session_id': 'demo_session_001',
            'processed_count': len(fotos_para_processar),
            'client': 'Cliente Demo',
            'session_type': 'ensaio_casal'
        })
        
        print("📢 Evento 'photos.processed' publicado")
        
        # Aguarda um pouco para MarketingAgent processar
        print("⏳ Aguardando MarketingAgent processar evento...")
        await asyncio.sleep(2)
        
        # MarketingAgent cria sugestões baseado nas fotos
        print("\n📈 Criando sugestões de marketing...")
        
        sugestoes_conteudo = await marketing_agent.execute_task({
            'type': 'suggest_content',
            'context': {
                'photos_processed': len(fotos_para_processar),
                'session_type': 'ensaio_casal',
                'client': 'Cliente Demo'
            }
        })
        
        print(f"💡 Sugestões criadas: {sugestoes_conteudo}")
        
        # Planeja posts para redes sociais
        print("\n📱 Planejando posts para redes sociais...")
        
        plano_posts = await marketing_agent.execute_task({
            'type': 'plan_social_posts',
            'photos': fotos_para_processar[:3]  # Usa apenas 3 fotos
        })
        
        print(f"📅 Plano de posts: {plano_posts}")
        
        # Demonstra comunicação direta entre agentes
        print("\n💬 Enviando mensagem direta...")
        
        await marketing_agent.send_direct_message('photo-agent', {
            'type': 'request_best_photos',
            'session_id': 'demo_session_001',
            'quantity': 10
        })
        
        print("✅ Mensagem direta enviada para PhotoAgent")
        
        # Aguarda um pouco para ver logs
        await asyncio.sleep(3)
        
        print("\n🎉 Demo de comunicação concluída com sucesso!")
        print("\n📊 Resumo da demonstração:")
        print(f"   - {len(fotos_para_processar)} fotos processadas")
        print(f"   - {len(sugestoes_conteudo.get('suggestions', []))} sugestões de conteúdo criadas")
        print(f"   - {plano_posts.get('posts_planned', 0)} posts planejados")
        print("   - Comunicação pub/sub funcionando")
        print("   - Mensagens diretas funcionando")
        
    except Exception as e:
        print(f"❌ Erro durante a demonstração: {e}")
        
    finally:
        # Para agentes
        print("\n⏹️ Finalizando agentes...")
        await photo_agent.stop()
        await marketing_agent.stop()


if __name__ == "__main__":
    print("Iniciando demo de comunicação...")
    print("Certifique-se de que o RabbitMQ está rodando!")
    print("Execute: docker-compose up -d rabbitmq\n")
    
    try:
        asyncio.run(demo_communication())
    except KeyboardInterrupt:
        print("\n👋 Demo interrompida pelo usuário")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")