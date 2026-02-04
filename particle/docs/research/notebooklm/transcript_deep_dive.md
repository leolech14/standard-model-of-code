# Transcript: Modelo Padrão e a Física do Código

**Type:** Deep Dive (Explanatory)
**Language:** Portuguese (Brazilian)
**Duration:** ~15 minutes
**Source:** NotebookLM AI-generated podcast

---

E se a gente pensasse em software, não como um artesanato, uma arte, mas como um universo físico.

Nossa!

Universo com suas próprias partículas, leis de comportamento e o mais maluco de tudo, até antimatéria.

É uma mudança de perspectiva assim brutal, a gente sairia de um mundo, onde o código é visto como uma série de decisões humanas, tipo muitas vezes idiosincráticas, pra um lugar onde ele é um sistema.

Um sistema com propriedades que emergem.

Exato, com leis que podem ser descobertas e o principal, medidas.

Ok, vamos mergulhar nisso então.

Porque a gente tem em mãos aqui um conjunto de documentos que propõem exatamente isso.

É um framework formal chamado o modelo padrão do código.

Uma física pro software é bem ambicioso.

É, e a nossa missão aqui é desvendar essa tentativa, sabe?

Entender como esse modelo classifica cada pecinha de um sistema, define as leis que governam tudo e até como ele mede a saúde e o propósito do código.

Exato.

O objetivo final pelo que eu entendi é pegar a estrutura que é invisível, a intenção que mora na cabeça de quem desenvolve e transformar em algo visível.

Mensurável.

E acima de tudo, rigoroso.

Chega de, eu acho que esse código tá ruim.

Exatamente.

A ideia é ter dados pra provar.

E o ponto de partida de tudo isso é uma ideia bem fundamental do modelo que eles até colocam numa equação, projeto igual a Codome mais Contextome.

Parece complicado, mas a ideia é super intuitiva, é a divisão fundamental de tudo que existe num projeto de software.

Certo.

Pensa assim, o Codome é a partícula, é todo o código que a máquina consegue executar, sabe?

E o ponto Pai, ponto JTS, ponto SQL é a matéria bruta do sistema.

Aquilo que tem uma sintaxe pode ser compilado ou interpretado.

Isso.

E o Contextome seria a onda.

É tudo aquilo que dá contexto significado pro código, mas que não é executável.

Ah, tipo documentação, especificações?

Documentação, especificações de produto, arquivos de configuração.

Até, sei lá, anotações de pesquisa num board é a intenção por trás da matéria.

Tá na analogia com a dualidade onda, a partícula da física, que é perfeita, né?

Sim.

O Codome, sozinho, sem o contexto, não tem um propósito claro.

E o Contextome sem o Codome é só uma ideia no ar, não tem aplicação.

Um não vive sem o outro pra descrever realidade completa.

Exato.

Tá, mas aí eu fico pensando, isso não é só um jeito, tipo bonito, de organizar as coisas, quer dizer, no fundo, não é só uma convenção, uma forma arbitrária de dar nome às coisas?

E aqui é que o negócio fica sério.

O que é fascinante nos documentos é que eles argumentam que essa divisão não é uma escolha de engenharia, não é uma convenção, é uma necessidade matemática.

A prova disso, segundo eles, vem do Teorema do ponto fixo de Löwer.

Uau, pera aí, você falou em Löwer e nos documentos eles também mencionam, o Teorema da incompletude de Gödel, isso soa bem intimidador, né?

Pra quem tá no dia a dia programando, o que isso quer dizer?

Que a minha documentação é matemáticamente obrigatória.

É quase isso, a essência, sabe, é que um sistema formal, no nosso caso, o Codome, ele não consegue se descrever completamente usando as próprias regras.

É como tentar se levantar puxando o próprio cadarço.

Exatamente, você precisa de uma linguagem externa, uma metalinguagem, pra falar sobre o sistema, sobre o propósito dele.

Essa metalinguagem é o Contextome.

Entendi.

Então sim, de uma perspectiva matemática, a documentação, a especificação não são extras ou nice-to-haves, são uma parte fundamental e necessária, o Código não pode ser sua própria especificação.

Entendi.

Então a separação não é opcional.

É tipo uma lei da natureza do software.

Eles não pararam por aí, né?

Criaram o que chamam de um verdadeiro zoológico do Código.

Sim, pra classificar absolutamente tudo, é uma taxonomia completa mesmo.

A estrutura começa com quatro grandes fases, ou reinos, temos os dados, que é a matéria, a lógica, que são as forças, a organização, que é a estrutura, e a execução, que é a dinâmica, o sistema em movimento.

E dentro disso vem os átomos, as unidades menores.

O modelo original tinha 167.

O que eu achei legal é que eles não trataram isso como verdade absoluta.

Não, ele evolui.

Depois de alinhar com o SWEBOK, o Corpo de Conhecimento de Engenharia de Software, esse número foi para 187.

Mostra que o modelo está vivo.

Sim, e além dos átomos, o modelo define 41 papéis canônicos, coisas que a gente já conhece como repositorio, validador, comando, serviço.

Isso, e é aqui que o modelo faz uma distinção que eu achei crucial, que resolve muita confusão na nossa área.

A diferença entre o que uma coisa é e para que ela serve.

Exatamente.

Um átomo responde à pergunta, o que é isso?

É uma definição baseada na sintaxe.

Por exemplo, isto é uma função ou isto é uma classe?

É uma verdade estrutural.

Imutável.

Isso.

Já um papel responde à pergunta, para que isso serve?

E essa resposta depende do contexto das relações daquela peça com o resto do sistema.

Ah, então a mesma classe, que é o átomo, pode ter papéis diferentes?

Exatamente.

Ela pode ser um controlador num contexto, recebendo requisições Web e um simples serviço em outro.

O propósito é relacional, não é absoluto.

Ok.

Essa ideia de classificar tudo num zoológico do código faz sentido, mas a biologia também tem regras de interação, ecossistemas, simbiose.

Esse modelo também tem leis que governam como essas partes todas interagem?

Tem.

E é aqui que o modelo deixa de ser só uma taxonomia e vira uma dinâmica.

Ele introduz leis e a mais interessante é que descreve a emergência do propósito.

Emergência do propósito.

O que você quer dizer com isso?

Quer dizer que o propósito de um trecho de código não é algo que alguém escreve num comentário, sabe?

O propósito emerge das relações que aquele código tem com o resto do sistema.

O modelo propõe umas equações de P1 a P4, que mostram como esse propósito é calculado de forma hierárquica.

Hierárquica.

Isso ainda está um pouco abstrato pra mim.

Me dá um exemplo prático.

Claro.

Imagina uma função simples, salvar o usuário.

A P1 olha o código e diz ok.

Isso aqui interage com um banco de dados.

O papel atômico disso é persistência.

Simples.

Ok, nível 1.

Aí a P2 olha pra um grupo de funções, tipo salvar o usuário, validar o usuário.

E conclui.

O propósito molecular desse grupo é gerenciamento de usuário.

P3 sobe um nível pra classe e define o propósito dela como um repositório de usuário.

E vai subindo.

Vai subindo.

Até a P4, que olha pro arquivo inteiro e determina o propósito do sistema maior, como módulo de acesso a dados.

O significado é construído camada por camada.

Então, o que você está dizendo é que o propósito não é algo que a gente escreve.

O código ganha um propósito, querendo ou não, só por existir ali, e esse modelo consegue medir isso.

Exatamente essa é a virada de chave.

Isso é revolucionário.

Tira a intenção do campo da opinião e transforma num dado.

E não é só sobre o que é bom.

O modelo também define o que é ruim.

Ele define o que chama de antimatéria.

Adorei esse nome.

O que seria a antimatéria do software?

São violações arquitetônicas, padrões de código que violam as boas práticas.

E o modelo não só dá nome a elas, como as detecta automaticamente.

As descrições são fantásticas.

A minha favorita que eu vi foi a AM-003, a God class, a classe divina.

Aquela classe que faz de tudo um pouco, né?

Valida, salva no banco, manda e-mail.

Um monstro.

E a forma como o modelo descreve isso é genial.

Peraí, você está me dizendo que eles usaram a teoria de um filósofo húngaro Arthur Koestler para descrever um problema de software?

Isso é fantástico!

Descreve isso melhor.

É incrível, né?

Eles usam a teoria dos Holons de Koestler.

Um Holon é algo que é ao mesmo tempo um todo e uma parte de um todo maior.

Certo.

O modelo descreve a God class como um Holon com tendência autoafirmativa excessiva, tornando-se cancerígeno para o sistema.

Essa linguagem não é só poética.

Ela é precisa.

É.

Descreve uma parte que se recusa a cooperar e tenta absorver tudo destruindo a arquitetura.

E tem o oposto, né?

A antimatéria AM-004, o anemic model.

Modelo anêmico.

Basicamente uma classe que só tem dados e um monte de get e set.

Um saco de dados sem comportamento.

Deixa eu adivinhar, também usam Koestler para esse?

Usam.

É um Holon com tendência integrativa excessiva, que perde sua identidade.

Ou seja, é uma classe tão passiva que vira um mero office boy de dados.

Ela só obedece.

Não pensa.

Nossa, eu já vi tantos projetos sofrerem com isso.

Você tem essas classes que são planilhas glorificadas e toda a lógica fica espalhada em dezenas de serviços.

É um pesadelo.

Exato.

Esse modelo dá um nome e uma causa para essa dor que todo dev experiente já sentiu.

Mas essa detecção de antimatéria não corre o risco de ser, sei lá, dogmática?

Uma God class é quase sempre ruim.

Mas e se, num contexto muito específico, ela for uma solução pragmática?

Ótima pergunta.

Não, o modelo não é binário.

Ele não diz, isso é uma God class, delete.

Ele calcula uma pontuação.

A violação AM-003, por exemplo, é medida pela combinação de baixa coesão e alta complexidade.

Ah, entendi.

Então, uma classe pode ter uma tendência a ser uma God class.

Com uma pontuação baixa de violação, o que pode ser aceitável.

O sistema te dá um termômetro, não um juiz.

Ok, faz sentido.

Se eles medem problemas como a antimatéria, imagino que também consigam medir a qualidade de forma positiva, né?

Sim.

É aí que entra a inteligência de propósito, ou as pontuações Q.

É uma nota de zero a um que mede o quão bem uma parte do código cumpre seu propósito.

A pergunta não é só, ele funciona.

Mas sim, ele cumpre sua intenção de forma elegante, eficiente e correta.

Exato.

E essa nota é uma média ponderada de cinco métricas.

E quais são os ingredientes?

Primeiro, alinhamento.

O código segue as regras no papel que ele está desempenhando.

Segundo, coerência.

Ele é focado em fazer uma única coisa.

Terceiro, densidade.

Qual a proporção de sinal versus ruído?

Ou seja, código útil versus código repetitivo.

O famoso boilerplate.

E isso, quarto, completude.

Ele tem tudo o que precisa para cumprir seu papel.

E por último, simplicidade.

Ele resolve o problema com o mínimo de complexidade.

É uma avaliação multidimensional da qualidade.

Isso muda completamente o nível da conversa num code review, né?

Em vez de, eu não gosto desse jeito, você pode dizer, a pontuação de coerência deste módulo caiu 20% e a causa é essa violação da lei AM-003.

Totalmente.

E falando em abstração, o modelo se apoia muito em analogias, né, como a dos Holons.

E o mais legal é que eles criaram um sistema para validar isso, para garantir que as analogias não são só bonitas, mas rigorosas.

Certo, a metodologia de pontuação de Analogias 4D.

Isso ainda parece meio etéreo.

Vamos pegar o exemplo principal deles.

A analogia Cloud Refinery igualmente subconsciente.

Como eles pontuam isso na prática?

Ótimo, vamos detalhar.

A metodologia quebra a analogia em mapeamentos específicos.

A dimensão semântica, com 40% de peso, é mais importante.

No nosso exemplo, ela pergunta.

Processamento contínuo na nuvem tem o mesmo significado de ruminação de fundo do subconsciente?

Sim.

Ambos são processos de baixo nível, sem prioridade, que organizam informações sem nossa atenção direta.

Exato.

Nota alta aqui.

A segunda é a estrutural, com 30%.

O subconsciente faz parte de uma mente maior, como uma parte consciente.

A refinaria faz parte de um sistema maior com interfaces de usuário, que são as partes conscientes.

A estrutura bate.

Faz sentido.

A terceira é a funcional, com 20%.

O propósito de ambos é processar e preparar informações para uma parte mais consciente.

E, por fim, a temporal, com 10%.

Ambos operam 24x7.

Somando tudo, a analogia alcançou 85.3 pontos.

Validada.

Então, a analogia não é só um enfeite, ela é uma ferramenta estrutural para pensar sobre o sistema.

Exatamente.

Ufa.

Tá.

Então, no fim das contas, o que tudo isso significa?

A gente saiu do código como texto para um universo, com partículas, o Codome, ondas de intenção, o Contextome, um zoológico de classificações, leis, antimatéria e até uma inteligência de propósito, que pode ser medida.

É isso.

O esforço central é tornar a estrutura invisível e a intenção do software em algo visível, mensurável, rigoroso.

É sair do campo da opinião e do feeling para um campo onde a gente pode ter uma discussão objetiva, baseada em métricas, sobre a saúde da nossa arquitetura.

É uma mudança de paradigma, uma nova forma de dialogar sobre a qualidade daquilo que a gente constrói.

E isso nos leva a uma questão para o futuro, que os próprios axiomas do modelo sugerem.

O modelo postula que a ascensão da IA está mudando o nosso trabalho.

O desenvolvimento de software está deixando de ser sobre escrever código e passando a ser sobre especificar a intenção.

Contextome, a documentação, os diagramas, as especificações.

Se torna o principal espaço de trabalho humano.

Enquanto isso, as IAs ficam cada vez melhores em traduzir essa intenção para o código executável.

Uma ideia bem provocadora para a gente fechar.

Sim, isso levanta uma questão fundamental.

Como será o desenvolvimento de software quando o nosso trabalho principal for curar o porquê e não mais o como?

Quando a engenharia de software se tornar fundamentalmente, a engenharia do contexto.
