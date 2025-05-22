# **Memory Mosaic 🟥🟨🟩🟦**

> **Note:** This document is available in both English and Portuguese. The English version is presented first, followed by the Portuguese version.
>
> **Nota:** Este documento está disponível em inglês e português. A versão em inglês é apresentada primeiro, seguida pela versão em português.

---

## **English**

### What is Memory Mosaic?

Memory Mosaic is an Anki addon that transforms your card collection into an interactive visual grid. Each card is represented by a small colored square ("tile"), with the color indicating the current learning status. It's similar to a disk defragmenter, but for your study cards!

![Memory Mosaic exemplo](https://i.ibb.co/8L2f5GjZ/image.png)

![Memory Mosaic exemplo](https://i.ibb.co/5XnVCRq0/image.png)

![Memory Mosaic exemplo](https://i.ibb.co/x8Jh5g4k/image.png)


### How does it work?

- **Grid Visualization:** Your cards are organized into a compact grid, allowing you to view hundreds or thousands of cards at once.
- **Two Visualization Modes:**
  - **Card States:** Shows cards colored by their learning state
  - **Gradient:** Shows cards in a color gradient based on properties like interval, ease factor, repetitions, lapses, or time until due
- **Intuitive Color System (Card States mode):**
  - **White:** New cards
  - **Dark Green:** Mature cards (interval ≥ 21 days)
  - **Light Green:** Young/learning cards
  - **Red:** Relearning cards
  - **Dark Gray:** Suspended/buried cards
- **Sorting Options:**
  - By creation date
  - By interval (ascending or descending)
  - By due date
- **Interactivity:**
  - Hover over a square to see card details
  - Click on a square to open the card in Anki's browser
  - A dot in the center indicates cards due today
- **Progressive Loading:** For very large collections, cards are loaded in batches (e.g., initial 4000), with "Show More" and "Show All" buttons to load the rest, ensuring better initial performance.

### Main benefits

- **Panoramic View:** See your entire collection or specific deck at once
- **Visual Tracking:** Immediately see the distribution of different card states
- **Natural Integration:** Automatically appears in the deck browser and overview screen
- **Automatic Updates:** Updates when you navigate or sync with AnkiWeb

### License and Contact

- **Copyright(C)** [Your Name Here]
- Licensed under [GNU AGPL, version 3](http://www.gnu.org/licenses/agpl.html)
- For bugs or suggestions, please open an issue at [https://github.com/cjdduarte/MemoryMosaic/issues](https://github.com/cjdduarte/MemoryMosaic/issues).

---

## **Português**

### O que é o Memory Mosaic?

O Memory Mosaic é um addon para o Anki que transforma sua coleção de cartões em uma grade visual interativa. Cada cartão é representado por um pequeno quadrado colorido ("tile"), cuja cor indica o status de aprendizado atual. É semelhante a um desfragmentador de disco, mas para seus cartões de estudo!

![Memory Mosaic exemplo](https://i.ibb.co/8L2f5GjZ/image.png)

![Memory Mosaic exemplo](https://i.ibb.co/5XnVCRq0/image.png)

![Memory Mosaic exemplo](https://i.ibb.co/x8Jh5g4k/image.png)

### Como funciona?

- **Visualização em Grade:** Seus cartões são organizados em uma grade compacta, permitindo visualizar centenas ou milhares de cartões de uma só vez.
- **Dois Modos de Visualização:**
  - **Estados dos Cartões:** Mostra cartões coloridos por seu estado de aprendizado
  - **Gradiente:** Mostra cartões em um gradiente de cores baseado em propriedades como intervalo, fator de facilidade, repetições, lapsos ou tempo até o vencimento
- **Sistema de Cores Intuitivo (modo Estados dos Cartões):**
  - **Branco:** Cartões novos
  - **Verde Escuro:** Cartões maduros (intervalo ≥ 21 dias)
  - **Verde Claro:** Cartões jovens/em aprendizado
  - **Vermelho:** Cartões em reaprendizado
  - **Cinza Escuro:** Cartões suspensos/enterrados
- **Opções de Ordenação:**
  - Por data de criação
  - Por intervalo (crescente ou decrescente)
  - Por data de vencimento
- **Interatividade:**
  - Passe o mouse sobre um quadrado para ver detalhes do cartão
  - Clique em um quadrado para abrir o cartão no navegador do Anki
  - Um ponto no centro indica cartões agendados para hoje
- **Carregamento Progressivo:** Para coleções muito grandes, os cartões são carregados em lotes (ex: 4000 iniciais), com botões "Mostrar Mais" e "Mostrar Todos" para carregar o restante, garantindo melhor performance inicial.

### Principais benefícios

- **Visão Panorâmica:** Visualize toda sua coleção ou deck específico de uma só vez
- **Acompanhamento Visual:** Veja a distribuição dos diferentes estados dos cartões imediatamente
- **Integração Natural:** Aparece automaticamente no navegador de decks e na tela de visão geral
- **Atualização Automática:** Se atualiza quando você navega ou sincroniza com o AnkiWeb

### Licença e Contato

- **Copyright(C)** [Carlos Duarte]
- Licenciado sob [GNU AGPL, version 3](http://www.gnu.org/licenses/agpl.html)
- Para bugs ou sugestões, por favor, abra uma issue em [https://github.com/cjdduarte/MemoryMosaic/issues](https://github.com/cjdduarte/MemoryMosaic/issues).

## **Changelog**

- **v1.5 - 2025-05-22 - Classification Fix**:
  - Fixed bug that incorrectly classified relearning cards with `type=3` and `queue=1` as "Default/Error" instead of "Relearning/Lapse".
  - Memory Mosaic now correctly identifies all relearning cards, regardless of the type/queue combination.

- **v1.4 - 2025-05-22 - Visual Enhancement**:
  - Added visual indicator for due cards in the summary, showing a rectangle with a centered red dot, simulating how the indicator appears on cards in the grid.
  - Improved summary legend for better understanding of visual elements.

- **v1.3 - 2025-05-22 - Configuration Improvements & UI Enhancement**:
  - Removed default values from configuration retrieval functions, making the addon more resilient to missing configuration keys.
  - Added "Factor" field to card tooltips, showing the card's ease factor value for better visualization of Anki's scheduling algorithm parameters.
  - Fixed translation-related issues for consistency between UI elements.

- **v1.2 - 2025-05-21 - Performance Optimizations & Progressive Loading**: 
  - Optimized fetching of last review dates for tooltips (batch query instead of per-card query), significantly improving performance on large collections.
  - Optimized calculation of "today's date" for due checks and gradient calculations (calculated once per grid render).
  - Optimized configuration reading for IVL gradient tooltips (read once per grid render).
  - Added progressive loading (pagination) for cards, with "Show More" and "Show All" buttons, improving initial load time for very large collections.

- **v1.1 - 2025-05-21 - Bug fix & Improvements**:
  - Corrected the sort order dropdown label to avoid redundancy and improve clarity.
  - Added a specific configuration key (`label_sort_order_group`) for the sort order group label.
  - Multilingual support for UI elements and messages.

- **v1.0 - 2025-05-20 - Initial Release**:
