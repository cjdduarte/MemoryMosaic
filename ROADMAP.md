# Roadmap: Addon Memory Mosaic

Este documento descreve os passos planejados para o desenvolvimento do addon "Memory Mosaic", que fornecerá uma visualização em grade do status dos cartões Anki.

## Fase 1: Estrutura Base e Desenho da Grade Estática

O objetivo desta fase é ter uma grade de quadrados representando os cartões exibida na tela principal do Anki.

*   **1.1. Configuração Inicial do Addon:**
    *   [X] Criar a estrutura de diretórios e arquivos básicos para um novo addon do Anki (`__init__.py`, `manifest.json`, etc.).
    *   [X] Integrar o addon à interface principal do Anki (por exemplo, na barra de status ou no corpo da tela de visão geral) para exibir um widget customizado. (Integrado ao Deck Browser e Overview)
*   **1.2. Cálculo e Exibição da Grade:**
    *   [X] Implementar a lógica para obter o número total de cartões na coleção (e seus IDs).
    *   [X] Desenvolver um algoritmo para calcular as dimensões da grade (CSS auto-fit).
    *   [X] Desenhar a grade utilizando HTML/CSS dentro do widget do addon.
    *   [X] Inicialmente, todos os quadrados terão uma cor padrão/placeholder. (Agora com cores finais)
    *   [X] Implementar a ordenação dos "espaços" na grade para corresponder à ordem de criação dos cartões (card.id ou card.cdate).

## Fase 2: Coloração Dinâmica e Atualização em Tempo Real

Nesta fase, os quadrados da grade ganharão cores baseadas nos estados dos cartões e serão atualizados dinamicamente.

*   **2.1. Mapeamento de Estados para Cores:**
    *   [X] Definir e implementar um esquema de cores para os diferentes estados dos cartões:
        *   **Verde Escuro:** Maduro (ex: intervalo > 21 dias).
        *   **Verde Claro:** Jovem ou em aprendizado.
        *   **Vermelho:** Errado/Lapso (reaprendizado).
        *   **Cinza Bem Escuro:** Suspenso ou "Ainda não visto/Buried".
        *   **Branco:** Novo (não estudado).
*   **2.2. Coleta de Dados dos Cartões:**
    *   [X] Implementar a lógica para buscar todos os IDs dos cartões a serem exibidos.
    *   [X] Para cada cartão, obter as informações necessárias para determinar seu status (tipo, intervalo, fila, etc.).
*   **2.3. Aplicação das Cores na Grade:**
    *   [X] Associar cada cartão (e seu status) a um quadrado específico na grade.
    *   [X] Atualizar a cor de cada quadrado para refletir o status do cartão correspondente (na renderização inicial).
*   **2.4. Atualização em Tempo Real:**
    *   [X] Atualização ao navegar para Deck Browser/Overview e após sincronização.

## Fase 3: Funcionalidades Adicionais e Refinamentos (Pós-MVP)

Melhorias e funcionalidades extras a serem consideradas após a implementação principal.

*   **3.1. Filtros:**
    *   [X] Implementar filtragem para mostrar apenas cartões do deck atual (e subdecks) na tela "Overview".
    *   [X] Implementar respeito ao filtro global `memorymosaic_default_deck_filter` para exibição no Deck Browser.
    *   [ ] Adicionar opções para filtrar os cartões exibidos na grade (ex: por tag).
*   **3.2. Tooltips/Informações Detalhadas e Interatividade:**
    *   [X] Ao passar o mouse sobre um quadrado, exibir um tooltip com informações básicas do cartão (CID, Due, Queue, Type, Ivl).
    *   [X] Ao clicar em um quadrado, abrir o cartão correspondente no Navegador do Anki.
*   **3.3. Persistência e Configurações:**
    *   [X] Configurações (cores, filtro padrão, indicador 'due', tamanho/gap dos tiles, cor da borda) são lidas do `config.json` (gerenciado pelo editor JSON do Anki).
    *   [X] Salvar as configurações do usuário (via `config.json`).
    *   [ ] Adicionar uma tela de configuração gráfica para o addon.
*   **3.4. Otimização de Performance:**
    *   [ ] Analisar o desempenho, especialmente com coleções muito grandes.
*   **3.5. Customização de Aparência:**
    *   [X] Tamanho dos tiles e espaçamento configuráveis via `config.json`.
    *   [ ] Permitir ao usuário customizar mais aspectos da aparência da grade (ex: largura da borda configurável via `config.json`).
*   **3.6. Modos de visualização e ordenação avançados:**
    *   [ ] Implementar uma visualização em modo "heatmap" com gradiente de cores baseado em facilidade (ease).
    *   [ ] Adicionar opção para visualização em grupos/clusters de cartões por deck ou tag.
    *   [ ] Implementar ordenação por frequência de erro (baseado nos dados de revisão).
    *   [ ] Permitir filtragem dinâmica combinando múltiplos critérios (tags, decks, estado).
*   **3.7. Suporte Multilíngue:**
    *   [X] Implementar infraestrutura para tradução da interface do addon (textos no sumário, tooltips, futura tela de configuração).

Este roadmap é um guia e pode ser ajustado conforme o desenvolvimento avança. 

Memory Mosaic 🟥🟨🟩🟦
anki mosaic visual grid cards color status tiles interactive tracking overview
https://github.com/cjdduarte/MemoryMosaic/issues

2.1.50
25.02.5