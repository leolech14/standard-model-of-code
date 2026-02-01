#!/bin/bash
# SCRIPT PARA CONFIGURAR PYTHON COMPATÍVEL COM TREE-SITTER

echo "🐍 CONFIGURAÇÃO PYTHON PARA TREE-SITTER"
echo "======================================="

# Verifica Python atual
echo "Python atual:"
python3 --version

# Verifica se pyenv está instalado
if ! command -v pyenv &> /dev/null; then
    echo ""
    echo "📥 Instalando pyenv (gerenciador de versões Python)..."

    # macOS com Homebrew
    if command -v brew &> /dev/null; then
        brew install pyenv
    else
        # Linux/Unix
        curl https://pyenv.run | bash
    fi

    # Adiciona ao shell
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
    echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
    echo 'eval "$(pyenv init -)"' >> ~/.zshrc

    # Recarrega
    export PYENV_ROOT="$HOME/.pyenv"
    command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"

    echo "✅ Pyenv instalado. Por favor, recarregue seu terminal: source ~/.zshrc"
fi

# Instala Python 3.11 (mais estável para tree-sitter)
echo ""
echo "📦 Instalando Python 3.11 (compatível com tree-sitter-languages)..."
pyenv install 3.11.10

# Define Python 3.11 como padrão do projeto
echo ""
echo "🎯 Configurando Python 3.11 para este projeto..."
pyenv local 3.11.10

# Verifica
python --version
echo "✅ Python 3.11 configurado!"

# Cria novo venv
echo ""
echo "🌱 Criando ambiente virtual com Python 3.11..."
rm -rf spectrometer-env 2>/dev/null
python -m venv spectrometer-env
source spectrometer-env/bin/activate

# Instala dependências
echo ""
echo "📦 Instalando dependências do Spectrometer V9..."
pip install --upgrade pip setuptools wheel

# Tree-sitter stack
echo ""
echo "🌳 Instalando Tree-sitter..."
pip install tree-sitter==0.25.2
pip install tree-sitter-languages

# LibCST
pip install libcst

# Outras dependências
pip install numpy pandas matplotlib

echo ""
echo "✅ Setup completo! Python 3.11 + Tree-sitter funcionando."
echo ""
echo "Para usar:"
echo "1. source spectrometer-env/bin/activate"
echo "2. python3 spectrometer_v9_fixed.py"
