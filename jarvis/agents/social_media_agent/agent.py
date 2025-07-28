"""
Social_media_agentAgent - Agente especializado em estratégias de marketing

Este agente é responsável por:
- Análise de campanhas de marketing
- Sugestões de conteúdo baseado em fotos processadas
- Métricas de performance
- Planejamento de estratégias promocionais
- Integração com redes sociais e CRM

Autor: Daniel Ribau Fotografia
Data: 2024
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List

# Adiciona o diretório pai ao path para importar BaseAgent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base.base_agent import BaseAgent


class Social_media_agentAgent(BaseAgent):
    """
    Agente especializado em marketing e estratégias promocionais.
    
    Funcionalidades principais:
    - Análise de campanhas
    - Geração de ideias de conteúdo
    - Planejamento de posts para redes sociais
    - Métricas e relatórios de performance
    - Sugestões de preços e promoções
    """

    def __init__(self):
        """Inicializa o Social_media_agentAgent."""
        super().__init__("social_media_agent")
        
        # Base de conhecimento para sugestões
        self.campaign_templates = {
            'ensaio_casal': {
                'title': 'Ensaio Romântico',
                'description': 'Capture momentos únicos do seu amor',
                'target_audience': 'casais',
                'best_seasons': ['primavera', 'outono'],
                'suggested_locations': ['parque', 'praia', 'campo']
            },
            'ensaio_familia': {
                'title': 'Memórias em Família',
                'description': 'Eternize os momentos especiais da família',
                'target_audience': 'famílias',
                'best_seasons': ['todas'],
                'suggested_locations': ['casa', 'parque', 'estúdio']
            },
            'ensaio_gestante': {
                'title': 'Esperando com Amor',
                'description': 'Celebre essa fase única da vida',
                'target_audience': 'gestantes',
                'best_seasons': ['todas'],
                'suggested_locations': ['estúdio', 'casa', 'jardim']
            }
        }
        
        # Estatísticas do agente
        self.stats = {
            'campaigns_created': 0,
            'content_suggestions': 0,
            'social_posts_planned': 0,
            'analytics_reports': 0
        }

    async def process_message(self, message: Dict[str, Any]) -> None:
        """
        Processa mensagens recebidas de outros agentes.
        
        Args:
            message: Mensagem com tipo de evento e dados
        """
        event_type = message.get('event_type', '')
        data = message.get('data', {})
        
        self.logger.debug(f"Processando evento: {event_type}")
        
        # Processa diferentes tipos de eventos
        if event_type == 'photos.processed':
            await self._handle_photos_processed(data)
        
        elif event_type == 'crm.new_client':
            await self._handle_new_client(data)
        
        elif event_type == 'social_media.post_published':
            await self._handle_post_published(data)
        
        elif event_type == 'calendar.session_completed':
            await self._handle_session_completed(data)
        
        elif event_type == 'task.marketing_campaign':
            await self._handle_campaign_task(data)
        
        else:
            self.logger.debug(f"Evento não processado pelo Social_media_agentAgent: {event_type}")

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa tarefas específicas do Social_media_agentAgent.
        
        Args:
            task: Dados da tarefa incluindo tipo e parâmetros
            
        Returns:
            Resultado da execução da tarefa
        """
        task_type = task.get('type', '')
        
        if task_type == 'create_campaign':
            return await self.create_campaign(task.get('campaign_data', {}))
        
        elif task_type == 'suggest_content':
            return await self.suggest_content(task.get('context', {}))
        
        elif task_type == 'analyze_performance':
            return await self.analyze_performance(task.get('period_days', 30))
        
        elif task_type == 'plan_social_posts':
            return await self.plan_social_posts(task.get('photos', []))
        
        elif task_type == 'generate_pricing':
            return await self.generate_pricing_suggestions(task.get('service_type', ''))
        
        elif task_type == 'get_stats':
            return {'status': 'success', 'stats': self.stats}
        
        else:
            return {
                'status': 'error',
                'message': f'Tipo de tarefa não reconhecido: {task_type}'
            }

    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria uma nova campanha de marketing.
        
        Args:
            campaign_data: Dados da campanha (tipo, público-alvo, etc.)
            
        Returns:
            Campanha criada com sugestões
        """
        try:
            service_type = campaign_data.get('service_type', 'ensaio_casal')
            template = self.campaign_templates.get(service_type, self.campaign_templates['ensaio_casal'])
            
            # Gera campanha baseada no template
            campaign = {
                'id': f"camp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'service_type': service_type,
                'title': template['title'],
                'description': template['description'],
                'target_audience': template['target_audience'],
                'created_at': datetime.now().isoformat(),
                'status': 'draft',
                'suggested_content': await self._generate_content_ideas(template),
                'budget_suggestions': await self._generate_budget_suggestions(service_type),
                'timeline': await self._generate_campaign_timeline()
            }
            
            self.stats['campaigns_created'] += 1
            
            # Publica evento de campanha criada
            await self.publish_message('marketing.campaign_created', {
                'campaign_id': campaign['id'],
                'service_type': service_type,
                'campaign': campaign
            })
            
            return {'status': 'success', 'campaign': campaign}
            
        except Exception as e:
            self.logger.error(f"Erro ao criar campanha: {e}")
            return {'status': 'error', 'message': str(e)}

    async def suggest_content(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sugere conteúdo baseado no contexto fornecido.
        
        Args:
            context: Contexto para sugestões (fotos processadas, cliente, etc.)
            
        Returns:
            Sugestões de conteúdo
        """
        try:
            suggestions = []
            
            # Sugestões baseadas em fotos processadas
            if 'photos_processed' in context:
                photo_count = context['photos_processed']
                suggestions.extend([
                    f"Compartilhe bastidores: '{photo_count} momentos únicos capturados hoje!'",
                    f"Mostre o antes/depois: 'O processo criativo por trás de {photo_count} fotos especiais'",
                    "Destaque técnicas utilizadas na sessão",
                    "Compartilhe depoimento do cliente (com autorização)"
                ])
            
            # Sugestões baseadas na temporada
            current_season = self._get_current_season()
            seasonal_suggestions = {
                'primavera': [
                    "Aproveite a luz natural da primavera",
                    "Flores e cores vibrantes como cenário",
                    "Ensaios ao ar livre em jardins"
                ],
                'verão': [
                    "Golden hour para fotos românticas",
                    "Ensaios na praia ao pôr do sol",
                    "Cores quentes e texturas naturais"
                ],
                'outono': [
                    "Folhas douradas como backdrop natural",
                    "Luz suave e atmosfera acolhedora",
                    "Tons terrosos e aconchegantes"
                ],
                'inverno': [
                    "Aconchego em ensaios internos",
                    "Luzes de natal como elemento",
                    "Roupas elegantes e texturas"
                ]
            }
            suggestions.extend(seasonal_suggestions.get(current_season, []))
            
            self.stats['content_suggestions'] += len(suggestions)
            
            return {
                'status': 'success',
                'suggestions': suggestions,
                'context': context,
                'season': current_season
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao sugerir conteúdo: {e}")
            return {'status': 'error', 'message': str(e)}

    async def plan_social_posts(self, photos: List[str]) -> Dict[str, Any]:
        """
        Planeja posts para redes sociais baseado em fotos.
        
        Args:
            photos: Lista de fotos processadas
            
        Returns:
            Plano de posts para redes sociais
        """
        try:
            posts_plan = []
            
            for i, photo in enumerate(photos[:5]):  # Limita a 5 posts
                post_date = datetime.now() + timedelta(days=i)
                
                post = {
                    'id': f"post_{datetime.now().strftime('%Y%m%d')}_{i+1}",
                    'photo': photo,
                    'scheduled_date': post_date.isoformat(),
                    'platforms': ['instagram', 'facebook'],
                    'caption': await self._generate_post_caption(photo, i),
                    'hashtags': await self._generate_hashtags(),
                    'best_time': await self._get_best_posting_time(post_date.weekday())
                }
                posts_plan.append(post)
            
            self.stats['social_posts_planned'] += len(posts_plan)
            
            # Envia plano para SocialMediaAgent
            await self.send_direct_message('social-media-agent', {
                'type': 'posts_plan',
                'posts': posts_plan
            })
            
            return {
                'status': 'success',
                'posts_planned': len(posts_plan),
                'posts': posts_plan
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao planejar posts: {e}")
            return {'status': 'error', 'message': str(e)}

    async def analyze_performance(self, period_days: int = 30) -> Dict[str, Any]:
        """
        Analisa performance de campanhas e conteúdo.
        
        Args:
            period_days: Período em dias para análise
            
        Returns:
            Relatório de performance
        """
        try:
            # Simula análise de performance (em implementação real, conectaria com APIs)
            analysis = {
                'period_days': period_days,
                'campaigns_analyzed': self.stats['campaigns_created'],
                'content_performance': {
                    'total_posts': self.stats['social_posts_planned'],
                    'engagement_rate': 4.2,  # Simulado
                    'reach': 1250,  # Simulado
                    'best_performing_content': 'ensaio_casal'
                },
                'recommendations': [
                    "Aumentar frequência de posts de bastidores",
                    "Focar em conteúdo de ensaios de casal (maior engajamento)",
                    "Postar preferencialmente entre 19h-21h",
                    "Usar mais stories interativos"
                ],
                'generated_at': datetime.now().isoformat()
            }
            
            self.stats['analytics_reports'] += 1
            
            return {'status': 'success', 'analysis': analysis}
            
        except Exception as e:
            self.logger.error(f"Erro na análise de performance: {e}")
            return {'status': 'error', 'message': str(e)}

    async def generate_pricing_suggestions(self, service_type: str) -> Dict[str, Any]:
        """
        Gera sugestões de preços baseado no tipo de serviço.
        
        Args:
            service_type: Tipo de serviço fotográfico
            
        Returns:
            Sugestões de preço
        """
        try:
            # Base de preços (valores em R$)
            base_prices = {
                'ensaio_casal': {'min': 300, 'max': 800, 'recommended': 500},
                'ensaio_familia': {'min': 400, 'max': 1000, 'recommended': 650},
                'ensaio_gestante': {'min': 250, 'max': 600, 'recommended': 400},
                'casamento': {'min': 1500, 'max': 5000, 'recommended': 2500},
                'evento_corporativo': {'min': 800, 'max': 2000, 'recommended': 1200}
            }
            
            pricing = base_prices.get(service_type, base_prices['ensaio_casal'])
            
            suggestions = {
                'service_type': service_type,
                'pricing': pricing,
                'packages': [
                    {
                        'name': 'Básico',
                        'price': pricing['min'],
                        'includes': ['30 fotos editadas', '1 hora de sessão', 'Galeria online']
                    },
                    {
                        'name': 'Completo',
                        'price': pricing['recommended'],
                        'includes': ['50 fotos editadas', '2 horas de sessão', 'Galeria online', 'Prints 10x15']
                    },
                    {
                        'name': 'Premium',
                        'price': pricing['max'],
                        'includes': ['100 fotos editadas', '3 horas de sessão', 'Galeria online', 'Álbum digital', 'Prints grandes']
                    }
                ],
                'market_factors': await self._get_market_factors(),
                'generated_at': datetime.now().isoformat()
            }
            
            return {'status': 'success', 'pricing_suggestions': suggestions}
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar sugestões de preço: {e}")
            return {'status': 'error', 'message': str(e)}

    # Métodos auxiliares

    async def _handle_photos_processed(self, data: Dict[str, Any]) -> None:
        """Processa evento de fotos processadas criando sugestões de conteúdo."""
        processed_count = data.get('processed_count', 0)
        suggestions = await self.suggest_content({'photos_processed': processed_count})
        self.logger.info(f"Sugestões criadas para {processed_count} fotos processadas")

    async def _handle_new_client(self, data: Dict[str, Any]) -> None:
        """Processa evento de novo cliente criando campanha personalizada."""
        client_data = {
            'service_type': data.get('service_type', 'ensaio_casal'),
            'client_name': data.get('client_name', '')
        }
        campaign = await self.create_campaign(client_data)
        self.logger.info(f"Campanha criada para novo cliente: {client_data['client_name']}")

    async def _handle_post_published(self, data: Dict[str, Any]) -> None:
        """Processa evento de post publicado atualizando métricas."""
        post_id = data.get('post_id', '')
        platform = data.get('platform', '')
        self.logger.info(f"Post {post_id} publicado em {platform}")

    async def _handle_session_completed(self, data: Dict[str, Any]) -> None:
        """Processa evento de sessão concluída planejando follow-up."""
        client_name = data.get('client_name', '')
        session_type = data.get('session_type', '')
        
        # Programa follow-up automático
        follow_up_plan = {
            'client_name': client_name,
            'session_type': session_type,
            'follow_up_date': (datetime.now() + timedelta(days=7)).isoformat(),
            'actions': ['Enviar galeria', 'Solicitar feedback', 'Oferecer próximo ensaio']
        }
        
        await self.send_direct_message('crm-agent', {
            'type': 'schedule_follow_up',
            'plan': follow_up_plan
        })

    async def _handle_campaign_task(self, data: Dict[str, Any]) -> None:
        """Processa tarefa de campanha específica."""
        campaign_data = data.get('campaign_data', {})
        result = await self.create_campaign(campaign_data)
        self.logger.info(f"Campanha executada: {result}")

    async def _generate_content_ideas(self, template: Dict[str, Any]) -> List[str]:
        """Gera ideias de conteúdo baseado no template."""
        return [
            f"Dicas para {template['target_audience']}",
            f"Bastidores de {template['title'].lower()}",
            f"Locações ideais: {', '.join(template['suggested_locations'])}",
            "Preparação para o ensaio",
            "Como escolher roupas para fotos"
        ]

    async def _generate_budget_suggestions(self, service_type: str) -> Dict[str, Any]:
        """Gera sugestões de orçamento para campanhas."""
        return {
            'ads_budget': 200,  # R$
            'content_creation': 150,
            'photography': 100,
            'total_monthly': 450
        }

    async def _generate_campaign_timeline(self) -> List[Dict[str, Any]]:
        """Gera cronograma para a campanha."""
        return [
            {'week': 1, 'activity': 'Criação de conteúdo visual'},
            {'week': 2, 'activity': 'Lançamento da campanha'},
            {'week': 3, 'activity': 'Intensificação de posts'},
            {'week': 4, 'activity': 'Análise de resultados'}
        ]

    async def _generate_post_caption(self, photo: str, index: int) -> str:
        """Gera legenda para post baseado na foto."""
        captions = [
            "Cada momento tem sua magia ✨",
            "Eternizando sorrisos únicos 📸",
            "A arte de capturar emoções 💝",
            "Momentos que ficam para sempre 🤍",
            "Sua história merece ser contada 📖"
        ]
        return captions[index % len(captions)]

    async def _generate_hashtags(self) -> List[str]:
        """Gera hashtags relevantes."""
        return [
            "#fotografia", "#ensaio", "#momentos", "#memories", 
            "#photography", "#love", "#couple", "#family",
            "#ribaufotografia", "#fotografo", "#brasília"
        ]

    async def _get_best_posting_time(self, weekday: int) -> str:
        """Retorna melhor horário para postar baseado no dia da semana."""
        best_times = {
            0: "19:00",  # Segunda
            1: "20:00",  # Terça
            2: "19:30",  # Quarta
            3: "20:30",  # Quinta
            4: "18:00",  # Sexta
            5: "17:00",  # Sábado
            6: "16:00"   # Domingo
        }
        return best_times.get(weekday, "19:00")

    def _get_current_season(self) -> str:
        """Retorna a estação atual baseada no mês."""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return 'verão'
        elif month in [3, 4, 5]:
            return 'outono'
        elif month in [6, 7, 8]:
            return 'inverno'
        else:
            return 'primavera'

    async def _get_market_factors(self) -> Dict[str, Any]:
        """Retorna fatores de mercado que influenciam preços."""
        return {
            'demand_level': 'alto',
            'season_factor': 1.1,  # 10% a mais na alta temporada
            'competition': 'média',
            'economic_factor': 'estável'
        }


async def main():
    """Função principal para executar o Social_media_agentAgent."""
    agent = Social_media_agentAgent()
    
    try:
        await agent.start()
        
        # Mantém o agente rodando
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\nParando Social_media_agentAgent...")
    except Exception as e:
        agent.logger.error(f"Erro no Social_media_agentAgent: {e}")
    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())