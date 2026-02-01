# 🚀 Guia de Configuração de LLM para Apple M4 Pro (24GB RAM)

## 💻 Seu Hardware
- **Processador**: Apple M4 Pro (14 cores)
- **Memória**: 24 GB RAM
- **Capacidade**: Excelente para modelos de até 34B parâmetros!

---

## 🏆 Modelos Recomendados (do mais rápido ao mais capaz)

### 1. **Qwen2.5-Coder-14B-Instruct** ⭐ **RECOMENDADO**
- **Tamanho**: 14B parâmetros
- **RAM necessária**: ~10GB
- **Vantagens**: Especializado em código, muito rápido
- **Download**: `ollama pull qwen2.5-coder:14b-instruct`

### 2. **DeepSeek-Coder-V2-Instruct** ⚡ **MUITO RÁPIDO**
- **Tamanho**: 16B parâmetros
- **RAM necessária**: ~12GB
- **Vantagens**: Ótimo para análise de código
- **Download**: `ollama pull deepseek-coder-v2:16b-instruct`

### 3. **Qwen2.5-32B-Instruct** 💪 **MAIOR CAPACIDADE**
- **Tamanho**: 32B parâmetros
- **RAM necessária**: ~20GB
- **Vantagens**: Máximo desempenho no seu hardware
- **Download**: `ollama pull qwen2.5:32b-instruct`

### 4. **Llama-3.1-8B-Instruct** 🔥 **EQUILÍBRIO PERFEITO**
- **Tamanho**: 8B parâmetros
- **RAM necessária**: ~6GB
- **Vantagens**: Rápido e eficiente
- **Download**: `ollama pull llama3.1:8b-instruct`

---

## ⚡ Como Instalar e Usar

### Opção A: Via Ollama (Recomendado)

```bash
# 1. Instalar o Ollama (se não tiver)
brew install ollama

# 2. Iniciar o serviço
ollama serve

# 3. Baixar o modelo recomendado
ollama pull qwen2.5-coder:14b-instruct

# 4. Configurar variáveis de ambiente
export SPECTROMETER_LLM_URL="http://localhost:11434/v1"
export SPECTROMETER_LLM_MODEL="qwen2.5-coder:14b-instruct"

# 5. Executar o Spectrometer
python3 spectrometer.py "the-code-elementals (2)" elements.json --enable-llm
```

### Opção B: Via LM Studio (Interface Gráfica)

1. **Download**: https://lmstudio.ai/
2. **Instalar** e abrir o LM Studio
3. **Buscar modelo**: "Qwen2.5-Coder-14B-Instruct"
4. **Configurar**:
   - GPU Acceleration: Metal
   - Context Length: 4096
   - Server Port: 8080
5. **Start Server**
6. **Configurar Spectrometer**:
   ```bash
   export SPECTROMETER_LLM_URL="http://localhost:8080/v1"
   export SPECTROMETER_LLM_MODEL="qwen2.5-coder:14b-instruct"
   ```

---

## 📊 Performance Esperada

| Modelo | Tempo Resposta | Qualidade | Uso RAM |
|--------|----------------|-----------|----------|
| Qwen2.5-14B | 2-3s | ⭐⭐⭐⭐⭐ | 10GB |
| DeepSeek-16B | 2-4s | ⭐⭐⭐⭐ | 12GB |
| Qwen2.5-32B | 4-6s | ⭐⭐⭐⭐⭐ | 20GB |
| Llama3.1-8B | 1-2s | ⭐⭐⭐ | 6GB |

---

## 🎯 Configuração Otimizada

Para obter o melhor desempenho no M4 Pro:

```bash
# Configurar para usar otimizações do Apple Silicon
export OLLAMA_GPU=nvidia  # Mesmo sendo Apple, força otimização
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_NUM_PARALLEL=2
```

---

## 🔧 Verificação

Para confirmar que o modelo está rodando:

```bash
# Verificar modelos disponíveis
ollama list

# Testar o modelo
ollama run qwen2.5-coder:14b-instruct "Analise este código: function hello() { return 'world'; }"
```

---

## ⚠️ Solução de Problemas

### Se o LLM retornar erro 404:
1. Verifique se o Ollama está rodando: `ps aux | grep ollama`
2. Verifique a porta: `lsof -i :11434`
3. Teste direto: `curl http://localhost:11434/api/generate`

### Se ficar lento demais:
1. Use um modelo menor (Llama3.1-8B)
2. Reduza o contexto no LLM
3. Feche outros aplicativos

---

## 💡 Dica Pro

Para o **melhor equilíbrio** entre velocidade e qualidade no seu hardware, use **Qwen2.5-Coder-14B-Instruct**:
- Especializado em análise de código
- Respostas rápidas no M4 Pro
- Alta precisão arquitetural
- Usa apenas 40% da sua RAM
