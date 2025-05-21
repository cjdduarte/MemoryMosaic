# **Memory Mosaic 🟥🟨🟩🟦**

> **Note:** This document is available in both English and Portuguese. The English version is presented first, followed by the Portuguese version.
>
> **Nota:** Este documento está disponível em inglês e português. A versão em inglês é apresentada primeiro, seguida pela versão em português.

---

## **English**

### What is Memory Mosaic?

Memory Mosaic is an Anki addon that transforms your card collection into an interactive visual grid. Each card is represented by a small colored square ("tile"), with the color indicating the current learning status. It's similar to a disk defragmenter, but for your study cards!

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

### Main benefits

- **Panoramic View:** See your entire collection or specific deck at once
- **Visual Tracking:** Immediately see the distribution of different card states
- **Natural Integration:** Automatically appears in the deck browser and overview screen
- **Automatic Updates:** Updates when you navigate or sync with AnkiWeb

### Example Screenshot

*Add a screenshot of Memory Mosaic in action here.*

`![Memory Mosaic example](placeholder_example.png)`

### How to install

1. Open Anki and go to "Tools" > "Add-ons" > "Get Add-ons..."
2. Paste the addon code and click "OK"
3. Restart Anki

Or install manually using the `.ankiaddon` file.

### License and Contact

- **Copyright(C)** [Your Name Here]
- Licensed under [GNU AGPL, version 3](http://www.gnu.org/licenses/agpl.html)
- For bugs or suggestions, open an issue in the project repository [link]

---

## **Português**

### O que é o Memory Mosaic?

O Memory Mosaic é um addon para o Anki que transforma sua coleção de cartões em uma grade visual interativa. Cada cartão é representado por um pequeno quadrado colorido ("tile"), cuja cor indica o status de aprendizado atual. É semelhante a um desfragmentador de disco, mas para seus cartões de estudo!

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

### Principais benefícios

- **Visão Panorâmica:** Visualize toda sua coleção ou deck específico de uma só vez
- **Acompanhamento Visual:** Veja a distribuição dos diferentes estados dos cartões imediatamente
- **Integração Natural:** Aparece automaticamente no navegador de decks e na tela de visão geral
- **Atualização Automática:** Se atualiza quando você navega ou sincroniza com o AnkiWeb

### Screenshot de Exemplo

*Adicione aqui uma screenshot do Memory Mosaic em ação.*

`![Memory Mosaic exemplo](placeholder_example.png)`

### Como instalar

1. Abra o Anki e vá para "Ferramentas" > "Complementos" > "Obter Complementos..."
2. Cole o código do addon e clique em "OK"
3. Reinicie o Anki

Ou instale manualmente através do arquivo `.ankiaddon`.

### Licença e Contato

- **Copyright(C)** [Seu Nome Aqui]
- Licenciado sob [GNU AGPL, version 3](http://www.gnu.org/licenses/agpl.html)
- Para bugs ou sugestões, abra uma issue no repositório do projeto [link]

## **Changelog**

- **v1.0 - Initial Release**:
  - Interactive visual grid for card visualization
  - Two visualization modes: Card States and Gradient
  - Color system for card states (new, mature, young, relearning, suspended)
  - Gradient visualization by interval, ease factor, repetitions, lapses, or time until due
  - Multiple sorting options (creation date, interval, due date)
  - Integration with Deck Browser and Overview screen
  - Automatic updates when navigating or syncing
  - Tooltips with detailed information on mouse hover
  - Interactivity to open cards in Anki's browser
  - Current deck filtering
  - Customizable settings (size, spacing, colors, gradient properties)
  - Multilingual support