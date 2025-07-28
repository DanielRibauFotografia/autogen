#!/usr/bin/env bash
# Quick start script for JARVIS system demonstration

echo "🤖 JARVIS - Demo do Sistema Multi-Agente"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Execute este script do diretório jarvis/"
    exit 1
fi

echo "📋 Este demo irá:"
echo "   1. Validar a estrutura do projeto"
echo "   2. Testar o sistema de memória"
echo "   3. Mostrar a interface CLI"
echo "   4. Executar exemplo simples"
echo ""

read -p "▶️  Pressione Enter para continuar..."

# 1. Validate structure
echo ""
echo "🔍 1. Validando estrutura do projeto..."
python3 validate_jarvis.py
if [ $? -ne 0 ]; then
    echo "❌ Validação falhou. Verifique a estrutura."
    exit 1
fi

echo ""
echo "✅ Estrutura validada com sucesso!"
read -p "▶️  Pressione Enter para continuar..."

# 2. Test memory system
echo ""
echo "🧠 2. Testando sistema de memória..."
python3 -c "
import asyncio
import sys
sys.path.append('.')
from memory.memory_manager import MemoryManager

async def demo_memory():
    print('   📝 Criando memórias de exemplo...')
    memory = MemoryManager('./demo_memory')
    
    # Episódica
    await memory.store_episodic('sessao_casal_joao', {
        'cliente': 'João Silva',
        'tipo': 'ensaio_casal',
        'local': 'Parque da Cidade',
        'fotos': 45
    })
    
    # Semântica
    await memory.store_semantic('ensaio_casal_procedimento', {
        'descricao': 'Como conduzir ensaio de casal',
        'passos': ['Planejamento', 'Preparação', 'Execução', 'Pós-produção'],
        'dicas': ['Luz natural', 'Poses naturais', 'Interação genuína']
    })
    
    print('   📊 Verificando estatísticas...')
    stats = await memory.get_stats()
    
    for tipo, info in stats['stats'].items():
        if info['count'] > 0:
            print(f'      {tipo}: {info[\"count\"]} itens')
    
    print('   ✅ Sistema de memória funcionando!')

asyncio.run(demo_memory())
"

if [ $? -eq 0 ]; then
    echo "✅ Sistema de memória testado com sucesso!"
else
    echo "❌ Erro no teste de memória"
fi

read -p "▶️  Pressione Enter para continuar..."

# 3. Show CLI help
echo ""
echo "💻 3. Interface CLI do JARVIS..."
echo "   📋 Comandos disponíveis via Makefile:"
make help | head -15

echo ""
echo "   💡 Exemplos de uso:"
echo "      make status          # Status do sistema"
echo "      make up              # Iniciar sistema"
echo "      make logs            # Ver logs"
echo "      make example-simple  # Executar exemplo"

read -p "▶️  Pressione Enter para continuar..."

# 4. Run simple example
echo ""
echo "🚀 4. Executando exemplo simples..."
python3 examples/simple_task.py

if [ $? -eq 0 ]; then
    echo "✅ Exemplo executado com sucesso!"
else
    echo "❌ Erro no exemplo simples"
fi

echo ""
echo "🎉 DEMO CONCLUÍDO!"
echo "=================="
echo ""
echo "📋 Próximos passos para usar o JARVIS:"
echo ""
echo "   1. Instalar dependências:"
echo "      make install"
echo ""
echo "   2. Verificar Docker:"
echo "      make check-deps"
echo ""
echo "   3. Iniciar sistema completo (requer Docker):"
echo "      make up"
echo ""
echo "   4. Ver logs em tempo real:"
echo "      make logs-follow"
echo ""
echo "   5. Usar CLI interativa:"
echo "      make cli"
echo ""
echo "   6. Executar exemplos avançados:"
echo "      make example-communication"
echo ""
echo "📖 Leia o README.md para documentação completa!"
echo "🐛 Reporte issues em: https://github.com/DanielRibauFotografia/autogen/issues"
echo ""
echo "👋 Obrigado por testar o JARVIS!"

# Cleanup demo memory
rm -rf ./demo_memory 2>/dev/null || true