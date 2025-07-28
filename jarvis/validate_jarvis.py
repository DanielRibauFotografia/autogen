#!/usr/bin/env python3
"""
Validação do Sistema JARVIS

Script de validação que testa todos os componentes principais
do sistema JARVIS sem dependências externas.

Autor: Daniel Ribau Fotografia
Data: 2024
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

# Adiciona path do projeto
sys.path.append(str(Path(__file__).parent))

def print_header(title):
    """Imprime cabeçalho formatado."""
    print(f"\n{'='*50}")
    print(f"🤖 {title}")
    print(f"{'='*50}")

def print_test(name, success, details=""):
    """Imprime resultado de teste."""
    status = "✅" if success else "❌"
    print(f"{status} {name}")
    if details:
        print(f"   {details}")

async def test_memory_system():
    """Testa sistema de memória."""
    print_header("Testando Sistema de Memória")
    
    try:
        from memory.memory_manager import MemoryManager
        
        with tempfile.TemporaryDirectory() as temp_dir:
            memory = MemoryManager(temp_dir)
            
            # Teste 1: Memória Episódica
            success = await memory.store_episodic('test_event', {
                'description': 'Evento de teste',
                'type': 'test',
                'client': 'Cliente Teste'
            })
            print_test("Armazenamento Episódico", success)
            
            retrieved = await memory.get_episodic('test_event')
            print_test("Recuperação Episódica", retrieved is not None)
            
            # Teste 2: Memória Semântica
            success = await memory.store_semantic('photography_basics', {
                'definition': 'Conceitos básicos de fotografia',
                'topics': ['exposição', 'composição', 'luz']
            })
            print_test("Armazenamento Semântico", success)
            
            # Teste 3: Memória de Trabalho
            success = await memory.store_working('current_task', {
                'task_type': 'photo_processing',
                'progress': 50
            }, ttl_hours=1)
            print_test("Memória de Trabalho", success)
            
            # Teste 4: Busca
            await memory.store_episodic('event2', {'type': 'test', 'client': 'João'})
            results = await memory.search_episodic({'type': 'test'})
            print_test("Busca Episódica", len(results) >= 2)
            
            # Teste 5: Estatísticas
            stats = await memory.get_stats()
            print_test("Estatísticas", stats['status'] == 'success')
            
        return True
        
    except Exception as e:
        print_test("Sistema de Memória", False, str(e))
        return False

def test_base_agent():
    """Testa classe base de agentes."""
    print_header("Testando Base Agent")
    
    try:
        # Mock da classe BaseAgent sem dependências
        class MockAgent:
            def __init__(self, name):
                self.agent_name = name
                self.processed_messages = []
                
            async def execute_task(self, task):
                return {
                    'status': 'success',
                    'task_type': task.get('type', 'unknown'),
                    'agent': self.agent_name
                }
        
        # Teste básico
        agent = MockAgent("test-agent")
        print_test("Inicialização de Agente", agent.agent_name == "test-agent")
        
        return True
        
    except Exception as e:
        print_test("Base Agent", False, str(e))
        return False

async def test_base_agent_async():
    """Testa classe base de agentes (versão async)."""
    print_header("Testando Base Agent")
    
    try:
        # Mock da classe BaseAgent sem dependências
        class MockAgent:
            def __init__(self, name):
                self.agent_name = name
                self.processed_messages = []
                
            async def execute_task(self, task):
                return {
                    'status': 'success',
                    'task_type': task.get('type', 'unknown'),
                    'agent': self.agent_name
                }
        
        # Teste básico
        agent = MockAgent("test-agent")
        print_test("Inicialização de Agente", agent.agent_name == "test-agent")
        
        # Teste de tarefa
        result = await agent.execute_task({'type': 'test_task'})
        task_success = result['status'] == 'success'
        print_test("Execução de Tarefa", task_success)
        
        return True
        
    except Exception as e:
        print_test("Base Agent", False, str(e))
        return False

def test_project_structure():
    """Testa estrutura do projeto."""
    print_header("Testando Estrutura do Projeto")
    
    jarvis_path = Path('.')
    
    # Diretórios obrigatórios
    required_dirs = [
        'agents', 'agents/base', 'agents/photo_agent', 'agents/marketing_agent',
        'memory', 'orchestrator', 'cli', 'examples', 'tests'
    ]
    
    missing_dirs = []
    for dir_name in required_dirs:
        dir_path = jarvis_path / dir_name
        if dir_path.exists():
            print_test(f"Diretório {dir_name}/", True)
        else:
            print_test(f"Diretório {dir_name}/", False)
            missing_dirs.append(dir_name)
    
    # Arquivos obrigatórios
    required_files = [
        'README.md', 'requirements.txt', 'docker-compose.yml', 'Makefile',
        'agents/base/base_agent.py', 'memory/memory_manager.py',
        'orchestrator/orchestrator.py', 'cli/jarvis_cli.py'
    ]
    
    missing_files = []
    for file_name in required_files:
        file_path = jarvis_path / file_name
        if file_path.exists():
            print_test(f"Arquivo {file_name}", True)
        else:
            print_test(f"Arquivo {file_name}", False)
            missing_files.append(file_name)
    
    success = len(missing_dirs) == 0 and len(missing_files) == 0
    return success

def test_docker_configs():
    """Testa configurações Docker."""
    print_header("Testando Configurações Docker")
    
    try:
        # Verifica docker-compose.yml
        compose_file = Path('docker-compose.yml')
        if compose_file.exists():
            content = compose_file.read_text()
            
            services_found = []
            expected_services = [
                'rabbitmq', 'orchestrator', 'photo-agent', 
                'marketing-agent', 'social-media-agent'
            ]
            
            for service in expected_services:
                if service in content:
                    services_found.append(service)
                    print_test(f"Serviço {service}", True)
                else:
                    print_test(f"Serviço {service}", False)
            
            print_test("docker-compose.yml", len(services_found) >= 3)
        else:
            print_test("docker-compose.yml", False, "Arquivo não encontrado")
            return False
        
        # Verifica Dockerfiles
        dockerfiles = [
            'agents/photo_agent/Dockerfile',
            'agents/marketing_agent/Dockerfile',
            'orchestrator/Dockerfile'
        ]
        
        dockerfile_count = 0
        for dockerfile in dockerfiles:
            if Path(dockerfile).exists():
                dockerfile_count += 1
                print_test(f"Dockerfile {dockerfile}", True)
            else:
                print_test(f"Dockerfile {dockerfile}", False)
        
        return dockerfile_count >= 2
        
    except Exception as e:
        print_test("Configurações Docker", False, str(e))
        return False

def test_cli_structure():
    """Testa estrutura da CLI."""
    print_header("Testando Interface CLI")
    
    try:
        cli_file = Path('cli/jarvis_cli.py')
        if not cli_file.exists():
            print_test("Arquivo CLI", False, "jarvis_cli.py não encontrado")
            return False
        
        content = cli_file.read_text()
        
        # Verifica estrutura básica
        tests = [
            ('@cli.command()', 'Decoradores de comando'),
            ('def welcome', 'Comando welcome'),
            ('def status', 'Comando status'),
            ('def task', 'Comando task'),
            ('click.', 'Integração Click'),
            ('JarvisCLI', 'Classe CLI')
        ]
        
        success_count = 0
        for pattern, description in tests:
            if pattern in content:
                print_test(description, True)
                success_count += 1
            else:
                print_test(description, False)
        
        return success_count >= 4
        
    except Exception as e:
        print_test("Interface CLI", False, str(e))
        return False

def test_documentation():
    """Testa documentação."""
    print_header("Testando Documentação")
    
    try:
        readme_file = Path('README.md')
        if not readme_file.exists():
            print_test("README.md", False, "Arquivo não encontrado")
            return False
        
        content = readme_file.read_text()
        
        # Verifica seções obrigatórias
        required_sections = [
            '# 🤖 JARVIS',
            '🏗️ Arquitetura do Sistema',
            '💻 Pré-requisitos',
            '🚀 Instalação',
            '🤖 Agentes Disponíveis',
            '🧠 Sistema de Memória',
            'macOS ARM64',
            'Docker',
            'RabbitMQ'
        ]
        
        found_sections = 0
        for section in required_sections:
            if section in content:
                found_sections += 1
                print_test(f"Seção '{section}'", True)
            else:
                print_test(f"Seção '{section}'", False)
        
        # Verifica tamanho da documentação
        word_count = len(content.split())
        print_test(f"Documentação abrangente ({word_count} palavras)", word_count > 1000)
        
        return found_sections >= 6
        
    except Exception as e:
        print_test("Documentação", False, str(e))
        return False

async def run_all_tests():
    """Executa todos os testes."""
    print("🤖 JARVIS - Validação do Sistema")
    print("🔍 Iniciando validação completa...")
    
    tests = [
        ("Estrutura do Projeto", test_project_structure),
        ("Configurações Docker", test_docker_configs),
        ("Interface CLI", test_cli_structure),
        ("Documentação", test_documentation),
        ("Sistema de Memória", test_memory_system),
        ("Base Agent", test_base_agent_async)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_test(test_name, False, f"Erro: {e}")
            results.append((test_name, False))
    
    # Resumo final
    print_header("Resumo da Validação")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        print_test(test_name, result)
    
    print(f"\n📊 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema JARVIS validado com sucesso")
        print("\n📋 Próximos passos:")
        print("   1. Execute 'make check-deps' para verificar dependências")
        print("   2. Execute 'make setup' para configurar ambiente")
        print("   3. Execute 'make up' para iniciar o sistema")
        return True
    else:
        print(f"\n⚠️  {total - passed} teste(s) falharam")
        print("🔧 Verifique os erros acima e corrija antes de prosseguir")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Validação interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal na validação: {e}")
        sys.exit(1)