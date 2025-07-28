"""
PhotoAgent - Agente especializado em gerenciamento de fotos

Este agente é responsável por:
- Organização de bibliotecas de fotos
- Análise de metadados (EXIF)
- Processamento básico de imagens
- Backup e sincronização
- Comunicação com outros agentes sobre eventos relacionados a fotos

Autor: Daniel Ribau Fotografia
Data: 2024
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Adiciona o diretório pai ao path para importar BaseAgent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base.base_agent import BaseAgent

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


class PhotoAgent(BaseAgent):
    """
    Agente especializado em gerenciamento e processamento de fotografias.
    
    Funcionalidades principais:
    - Organização automática de fotos por data/evento
    - Extração de metadados EXIF
    - Detecção de duplicatas
    - Processamento básico (redimensionamento, compressão)
    - Integração com workflow de marketing e redes sociais
    """

    def __init__(self):
        """Inicializa o PhotoAgent."""
        super().__init__("photo-agent")
        
        # Diretórios de trabalho
        self.photo_dir = Path("/app/photos")
        self.processed_dir = Path("/app/photos/processed")
        self.backup_dir = Path("/app/photos/backup")
        
        # Cria diretórios se não existirem
        self.photo_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Formatos de imagem suportados
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.webp'}
        
        # Estatísticas do agente
        self.stats = {
            'photos_processed': 0,
            'photos_organized': 0,
            'duplicates_found': 0,
            'errors': 0
        }
        
        if not PILLOW_AVAILABLE:
            self.logger.warning("Pillow não disponível. Funcionalidades de processamento limitadas.")

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
        if event_type == 'task.photo_organization':
            await self._handle_photo_organization_task(data)
        
        elif event_type == 'task.photo_processing':
            await self._handle_photo_processing_task(data)
        
        elif event_type == 'crm.new_client':
            await self._handle_new_client_event(data)
        
        elif event_type == 'calendar.session_scheduled':
            await self._handle_session_scheduled(data)
        
        else:
            self.logger.debug(f"Evento não processado pelo PhotoAgent: {event_type}")

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa tarefas específicas do PhotoAgent.
        
        Args:
            task: Dados da tarefa incluindo tipo e parâmetros
            
        Returns:
            Resultado da execução da tarefa
        """
        task_type = task.get('type', '')
        
        if task_type == 'organize_photos':
            return await self.organize_photos(task.get('path', str(self.photo_dir)))
        
        elif task_type == 'process_photos':
            return await self.process_photos(task.get('photos', []))
        
        elif task_type == 'analyze_photo':
            return await self.analyze_photo(task.get('photo_path', ''))
        
        elif task_type == 'create_backup':
            return await self.create_backup(task.get('source_path', ''))
        
        elif task_type == 'get_stats':
            return {'status': 'success', 'stats': self.stats}
        
        else:
            return {
                'status': 'error',
                'message': f'Tipo de tarefa não reconhecido: {task_type}'
            }

    async def organize_photos(self, source_path: str) -> Dict[str, Any]:
        """
        Organiza fotos por data em estrutura de pastas.
        
        Args:
            source_path: Caminho da pasta com fotos para organizar
            
        Returns:
            Resultado da organização
        """
        try:
            source = Path(source_path)
            if not source.exists():
                return {'status': 'error', 'message': f'Caminho não encontrado: {source_path}'}
            
            organized_count = 0
            error_count = 0
            
            # Lista todas as imagens na pasta
            image_files = []
            for ext in self.supported_formats:
                image_files.extend(source.glob(f"*{ext}"))
                image_files.extend(source.glob(f"*{ext.upper()}"))
            
            self.logger.info(f"Encontradas {len(image_files)} imagens para organizar")
            
            for image_path in image_files:
                try:
                    # Obtém data da foto (EXIF ou arquivo)
                    photo_date = await self._get_photo_date(image_path)
                    
                    # Cria estrutura de pastas por data
                    year_month = photo_date.strftime("%Y-%m")
                    target_dir = self.processed_dir / year_month
                    target_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Move arquivo para pasta organizada
                    target_path = target_dir / image_path.name
                    if not target_path.exists():
                        image_path.rename(target_path)
                        organized_count += 1
                        self.logger.debug(f"Organizada: {image_path.name} -> {year_month}/")
                    
                except Exception as e:
                    error_count += 1
                    self.logger.error(f"Erro ao organizar {image_path.name}: {e}")
            
            # Atualiza estatísticas
            self.stats['photos_organized'] += organized_count
            self.stats['errors'] += error_count
            
            # Publica evento de organização concluída
            await self.publish_message('photos.organized', {
                'organized_count': organized_count,
                'error_count': error_count,
                'source_path': source_path
            })
            
            return {
                'status': 'success',
                'organized_count': organized_count,
                'error_count': error_count,
                'message': f'Organizadas {organized_count} fotos com {error_count} erros'
            }
            
        except Exception as e:
            self.logger.error(f"Erro na organização de fotos: {e}")
            return {'status': 'error', 'message': str(e)}

    async def process_photos(self, photo_list: List[str]) -> Dict[str, Any]:
        """
        Processa uma lista de fotos (redimensionamento, otimização).
        
        Args:
            photo_list: Lista de caminhos de fotos para processar
            
        Returns:
            Resultado do processamento
        """
        if not PILLOW_AVAILABLE:
            return {'status': 'error', 'message': 'Pillow não disponível para processamento'}
        
        try:
            processed_count = 0
            results = []
            
            for photo_path in photo_list:
                try:
                    result = await self._process_single_photo(photo_path)
                    results.append(result)
                    if result['status'] == 'success':
                        processed_count += 1
                        
                except Exception as e:
                    self.logger.error(f"Erro ao processar {photo_path}: {e}")
                    results.append({
                        'photo_path': photo_path,
                        'status': 'error',
                        'message': str(e)
                    })
            
            self.stats['photos_processed'] += processed_count
            
            # Publica evento de processamento concluído
            await self.publish_message('photos.processed', {
                'processed_count': processed_count,
                'total_photos': len(photo_list),
                'results': results
            })
            
            return {
                'status': 'success',
                'processed_count': processed_count,
                'total_photos': len(photo_list),
                'results': results
            }
            
        except Exception as e:
            self.logger.error(f"Erro no processamento de fotos: {e}")
            return {'status': 'error', 'message': str(e)}

    async def analyze_photo(self, photo_path: str) -> Dict[str, Any]:
        """
        Analisa uma foto e extrai metadados.
        
        Args:
            photo_path: Caminho da foto a ser analisada
            
        Returns:
            Metadados da foto
        """
        try:
            path = Path(photo_path)
            if not path.exists():
                return {'status': 'error', 'message': 'Arquivo não encontrado'}
            
            analysis = {
                'file_name': path.name,
                'file_size': path.stat().st_size,
                'file_date': datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
                'format': path.suffix.lower()
            }
            
            # Extrai metadados EXIF se disponível
            if PILLOW_AVAILABLE and path.suffix.lower() in {'.jpg', '.jpeg'}:
                exif_data = await self._extract_exif_data(path)
                analysis['exif'] = exif_data
            
            return {'status': 'success', 'analysis': analysis}
            
        except Exception as e:
            self.logger.error(f"Erro na análise da foto: {e}")
            return {'status': 'error', 'message': str(e)}

    async def create_backup(self, source_path: str) -> Dict[str, Any]:
        """
        Cria backup de fotos.
        
        Args:
            source_path: Caminho da pasta a fazer backup
            
        Returns:
            Resultado do backup
        """
        try:
            import shutil
            from datetime import datetime
            
            source = Path(source_path)
            if not source.exists():
                return {'status': 'error', 'message': 'Caminho não encontrado'}
            
            # Cria nome do backup com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{source.name}_{timestamp}"
            backup_path = self.backup_dir / backup_name
            
            # Copia arquivos
            shutil.copytree(source, backup_path)
            
            # Conta arquivos copiados
            file_count = len(list(backup_path.rglob("*")))
            
            # Publica evento de backup concluído
            await self.publish_message('photos.backup_created', {
                'backup_path': str(backup_path),
                'source_path': source_path,
                'file_count': file_count
            })
            
            return {
                'status': 'success',
                'backup_path': str(backup_path),
                'file_count': file_count
            }
            
        except Exception as e:
            self.logger.error(f"Erro no backup: {e}")
            return {'status': 'error', 'message': str(e)}

    async def _handle_photo_organization_task(self, data: Dict[str, Any]) -> None:
        """Processa tarefa de organização de fotos."""
        path = data.get('path', str(self.photo_dir))
        result = await self.organize_photos(path)
        self.logger.info(f"Organização concluída: {result}")

    async def _handle_photo_processing_task(self, data: Dict[str, Any]) -> None:
        """Processa tarefa de processamento de fotos."""
        photos = data.get('photos', [])
        result = await self.process_photos(photos)
        self.logger.info(f"Processamento concluído: {result}")

    async def _handle_new_client_event(self, data: Dict[str, Any]) -> None:
        """Processa evento de novo cliente criando pasta."""
        client_name = data.get('client_name', 'unknown')
        client_folder = self.photo_dir / "clients" / client_name
        client_folder.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Pasta criada para cliente: {client_name}")

    async def _handle_session_scheduled(self, data: Dict[str, Any]) -> None:
        """Processa evento de sessão agendada."""
        session_type = data.get('session_type', 'session')
        client_name = data.get('client_name', 'unknown')
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # Cria pasta para a sessão
        session_folder = self.photo_dir / "sessions" / f"{date}_{client_name}_{session_type}"
        session_folder.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Pasta criada para sessão: {session_folder.name}")

    async def _get_photo_date(self, image_path: Path) -> datetime:
        """Obtém data da foto (EXIF ou arquivo)."""
        try:
            if PILLOW_AVAILABLE and image_path.suffix.lower() in {'.jpg', '.jpeg'}:
                with Image.open(image_path) as img:
                    exifdata = img.getexif()
                    if exifdata:
                        # Procura por data/hora na EXIF
                        for tag_id in exifdata:
                            tag = TAGS.get(tag_id, tag_id)
                            if tag == "DateTime":
                                date_str = exifdata.get(tag_id)
                                if date_str:
                                    return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
        except Exception:
            pass
        
        # Usa data de modificação do arquivo como fallback
        return datetime.fromtimestamp(image_path.stat().st_mtime)

    async def _extract_exif_data(self, image_path: Path) -> Dict[str, Any]:
        """Extrai dados EXIF da imagem."""
        exif_data = {}
        try:
            with Image.open(image_path) as img:
                exifdata = img.getexif()
                for tag_id in exifdata:
                    tag = TAGS.get(tag_id, tag_id)
                    data = exifdata.get(tag_id)
                    if isinstance(data, bytes):
                        data = data.decode('utf-8', errors='ignore')
                    exif_data[tag] = data
        except Exception as e:
            self.logger.warning(f"Erro ao extrair EXIF de {image_path}: {e}")
        
        return exif_data

    async def _process_single_photo(self, photo_path: str) -> Dict[str, Any]:
        """Processa uma única foto."""
        try:
            path = Path(photo_path)
            if not path.exists():
                return {'status': 'error', 'message': 'Arquivo não encontrado'}
            
            with Image.open(path) as img:
                # Redimensiona se muito grande (mantém proporção)
                max_size = (2048, 2048)
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    # Salva versão redimensionada
                    output_path = self.processed_dir / f"resized_{path.name}"
                    img.save(output_path, optimize=True, quality=85)
                    
                    return {
                        'photo_path': photo_path,
                        'status': 'success',
                        'output_path': str(output_path),
                        'original_size': f"{img.size[0]}x{img.size[1]}",
                        'action': 'resized'
                    }
                else:
                    return {
                        'photo_path': photo_path,
                        'status': 'success',
                        'action': 'no_changes_needed'
                    }
                    
        except Exception as e:
            return {
                'photo_path': photo_path,
                'status': 'error',
                'message': str(e)
            }


async def main():
    """Função principal para executar o PhotoAgent."""
    agent = PhotoAgent()
    
    try:
        await agent.start()
        
        # Mantém o agente rodando
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\nParando PhotoAgent...")
    except Exception as e:
        agent.logger.error(f"Erro no PhotoAgent: {e}")
    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())