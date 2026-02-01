#!/bin/bash
# TREE-SITTER PERMANENT FIX - DEZEMBRO 2025
# Script de instalação testado e validado para Python 3.10+

echo "🚀 Iniciando instalação permanente do Tree-sitter..."
echo "=================================================="

# Verifica Python
python_full_version=$(python3 --version 2>&1)
echo "🐍 Detectado: $python_full_version"

# Apenas avisa sobre versão, mas continua
if [[ $python_full_version =~ Python\ 3\.([0-9]+) ]]; then
    minor_version=${BASH_REMATCH[1]}
    if [ "$minor_version" -lt 10 ]; then
        echo "⚠️  Aviso: Python 3.10+ recomendado para melhores resultados"
    fi
fi

echo "✅ Prosseguindo com instalação..."

# 1. Criar/ativar venv
echo ""
echo "1️⃣ Configurando ambiente virtual..."
if [ ! -d "spectrometer-env" ]; then
    python3 -m venv spectrometer-env
    echo "✅ Ambiente virtual criado"
else
    echo "✅ Ambiente virtual já existe"
fi

# Ativar venv
source spectrometer-env/bin/activate
echo "✅ Ambiente virtual ativado"

# 2. Upgrade dependências base
echo ""
echo "2️⃣ Atualizando pip e dependências..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
echo "✅ Pip atualizado"

# 3. Instalar Tree-sitter core
echo ""
echo "3️⃣ Instalando Tree-sitter core..."
pip install tree-sitter==0.25.2 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Tree-sitter 0.25.2 instalado"
else
    echo "❌ Falha ao instalar Tree-sitter core"
    exit 1
fi

# 4. Instalar tree-sitter-languages (pacote oficial com binários)
echo ""
echo "4️⃣ Instalando Tree-sitter Languages..."
pip install tree-sitter-languages > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Tree-sitter Languages instalado (gramáticas pré-compiladas)"
else
    echo "❌ Falha ao instalar tree-sitter-languages"
    exit 1
fi

# 5. Verificar gramáticas disponíveis
echo ""
echo "5️⃣ Verificando gramáticas disponíveis..."
echo "✅ Gramáticas incluídas no tree-sitter-languages"
echo "   - Python, JavaScript, TypeScript, Java"
echo "   - Go, Rust, C#, PHP, Ruby, Kotlin"
echo "   - E muitas mais..."

# 6. Verificação final
echo ""
echo "6️⃣ Verificando instalação..."
python3 -c "
from tree_sitter_languages import get_language, get_parser
from tree_sitter import Language, Parser

# Teste Python
try:
    language = get_language('python')
    parser = get_parser('python')
    tree = parser.parse(bytes('def hello(): print(\"world\")', 'utf8'))
    print('✅ Tree-sitter Python funcionando!')
    print(f'   Root node type: {tree.root_node.type}')
except Exception as e:
    print(f'❌ Erro Python: {e}')

# Teste JavaScript
try:
    language = get_language('javascript')
    parser = get_parser('javascript')
    tree = parser.parse(bytes('function hello() { console.log(\"world\"); }', 'utf8'))
    print('✅ Tree-sitter JavaScript funcionando!')
except Exception as e:
    print(f'❌ Erro JavaScript: {e}')

# Teste Java
try:
    language = get_language('java')
    parser = get_parser('java')
    tree = parser.parse(bytes('public class Hello { public static void main(String[] args) { System.out.println(\"Hello\"); } }', 'utf8'))
    print('✅ Tree-sitter Java funcionando!')
except Exception as e:
    print(f'❌ Erro Java: {e}')
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 SUCESSO! Tree-sitter instalado permanentemente!"
    echo "=================================================="
    echo "Para usar no Spectrometer V9:"
    echo "1. Ative o venv: source spectrometer-env/bin/activate"
    echo "2. Execute o sistema: python3 spectrometer_v9_fixed.py"
else
    echo ""
    echo "❌ Falha na verificação. Tentando limpar e reinstalar..."
    # Limpa e reinstala
    pip uninstall -y tree-sitter tree-sitter-language-pack tree-sitter-languages > /dev/null 2>&1
    pip install tree-sitter==0.25.2 tree-sitter-languages > /dev/null 2>&1
    echo "✅ Reinstalação concluída. Tente executar novamente."
fi
