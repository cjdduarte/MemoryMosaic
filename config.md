# Configuração do Addon Memory Mosaic

> **Note:** This document is available in both Portuguese and English. The Portuguese version is presented first, followed by the English version.
>
> **Nota:** Este documento está disponível em português e inglês. A versão em português é apresentada primeiro, seguida pela versão em inglês.

## Português

Este arquivo descreve as opções de configuração para o addon Memory Mosaic.
Você pode editar os valores no arquivo `config.json` correspondente ou através da tela de configuração do addon no Anki (Ferramentas -> Complementos -> Memory Mosaic -> Configuração), que abrirá um editor JSON.

## Opções de Cores dos Tiles

As cores são definidas usando códigos hexadecimais HTML (ex: "#RRGGBB").

*   `"color_new"`: Cor para cartões novos (não estudados).
    *   Padrão: `"#FFFFFF"` (Branco)
*   `"color_mature"`: Cor para cartões maduros (intervalo de revisão >= 21 dias).
    *   Padrão: `"#66B266"` (Verde Escuro)
*   `"color_young_learn"`: Cor para cartões jovens (intervalo < 21 dias) ou em aprendizado.
    *   Padrão: `"#A1E0A1"` (Verde Claro)
*   `"color_relearning_lapse"`: Cor para cartões em reaprendizado ou lapso.
    *   Padrão: `"#E53935"` (Vermelho Forte)
*   `"color_suspended_buried"`: Cor para cartões suspensos ou enterrados.
    *   Padrão: `"#222222"` (Cinza Bem Escuro)
*   `"color_default_bg"`: Cor de fallback usada se o status do cartão não puder ser determinado.
    *   Padrão: `"#E0E0E0"` (Cinza Claro)
*   `"tile_border_color"`: Cor da borda de cada tile individual.
    *   Padrão: `"#c0c0c0"` (Cinza)

## Indicador de Cartões "Due"

Um pequeno ponto que aparece no centro dos tiles para cartões que estão agendados para estudo hoje.

*   `"show_due_indicator"`: Define se o indicador de "due" deve ser exibido.
    *   Valores: `true` (mostrar) ou `false` (ocultar).
    *   Padrão: `true`
*   `"due_indicator_color"`: Cor do indicador de "due".
    *   Padrão: `"#FF0000"` (Vermelho)
*   `"due_indicator_size_ratio"`: Proporção do tamanho do indicador em relação ao tamanho do tile.
    *   Por exemplo, `0.33` significa que o indicador terá aproximadamente 1/3 do tamanho do tile.
    *   Valores: Um número entre `0.1` (pequeno) e `1.0` (tão grande quanto o tile).
    *   Padrão: `0.33`

## Filtro de Deck Padrão

*   `"memorymosaic_default_deck_filter"`: Permite especificar um nome de deck para filtrar a visualização do Memory Mosaic na tela principal ("Lista de Decks").
    *   Se uma string vazia (`""`) for fornecida, todos os cartões da coleção serão considerados.
    *   Se um nome de deck for especificado (ex: `"Meu Deck de Japonês"` ou `"Estudos::Vocabulário"`), apenas os cartões pertencentes a esse deck (e seus subdecks) serão mostrados.
    *   Este filtro **não** se aplica à visualização do Memory Mosaic dentro da tela de "Visão Geral" de um deck específico; lá, o Memory Mosaic sempre mostrará os cartões do deck atualmente visualizado.
    *   Padrão: `""` (sem filtro)

## Configurações de Dimensionamento e Layout da Grade

Estas opções controlam a aparência e o comportamento da grade de tiles.

*   `"tile_default_size_px"`: Tamanho padrão (largura e altura) do *conteúdo* de um tile em pixels. A grade tentará usar este tamanho se houver espaço.
    *   Padrão: `8`
*   `"tile_default_gap_px"`: Espaçamento padrão entre os tiles em pixels.
    *   Padrão: `0`
*   `"tile_min_size_px"`: Tamanho mínimo que o *conteúdo* de um tile pode ter. Se necessário, os tiles serão reduzidos até este tamanho para caberem mais na grade.
    *   Padrão: `6`
*   `"grid_max_width_px"`: Largura máxima total da área da grade em pixels.
    *   Padrão: `900`
*   `"grid_max_height_px"`: Altura máxima total da área da grade em pixels. Se o conteúdo exceder, barras de rolagem podem aparecer.
    *   Padrão: `800`
*   `"grid_padding_px"`: Padding (espaçamento interno) dentro do container da grade, em pixels.
    *   Padrão: `5`

**Nota sobre a Largura da Borda do Tile (`tile_border_width_px`):**
Atualmente, a largura da borda de cada tile é fixada em `1px` diretamente no código para corresponder ao estilo CSS. Tornar isso configurável exigiria que o estilo CSS do tile fosse ajustado dinamicamente, o que não está implementado no momento. Apenas a *cor* da borda (`tile_border_color`) é configurável.

Após modificar o `config.json` diretamente, pode ser necessário reiniciar o Anki para que as alterações tenham efeito, ou elas podem ser aplicadas na próxima vez que o Memory Mosaic for renderizado, dependendo da versão do Anki e do hook `config_did_change_hook`. Se você editar pela interface do Anki, as alterações geralmente são aplicadas após salvar e fechar a janela de configuração.

## Nova Opção de Configuração

*   `"memorymosaic_default_sort_order"`: Define a ordenação padrão dos tiles ao carregar.
    *   Opções válidas:
        *   `"id_asc"` (Padrão): Ordena por data de criação (mais antigos primeiro).
        *   `"ivl_asc"`: Ordena por intervalo crescente (intervalos menores primeiro).
        *   `"ivl_desc"`: Ordena por intervalo decrescente (intervalos maiores primeiro).
        *   `"due_asc"`: Ordena por data de vencimento (mais próximos primeiro).
    *   Padrão se não especificado: `"id_asc"`. 

---

## English

# Memory Mosaic Addon Configuration

This file describes the configuration options for the Memory Mosaic addon.
You can edit the values in the corresponding `config.json` file or through the addon configuration screen in Anki (Tools -> Add-ons -> Memory Mosaic -> Config), which will open a JSON editor.

## Tile Color Options

Colors are defined using HTML hexadecimal codes (e.g., "#RRGGBB").

*   `"color_new"`: Color for new cards (not studied yet).
    *   Default: `"#FFFFFF"` (White)
*   `"color_mature"`: Color for mature cards (review interval >= 21 days).
    *   Default: `"#66B266"` (Dark Green)
*   `"color_young_learn"`: Color for young cards (interval < 21 days) or cards in learning.
    *   Default: `"#A1E0A1"` (Light Green)
*   `"color_relearning_lapse"`: Color for cards in relearning or lapsed.
    *   Default: `"#E53935"` (Strong Red)
*   `"color_suspended_buried"`: Color for suspended or buried cards.
    *   Default: `"#222222"` (Very Dark Gray)
*   `"color_default_bg"`: Fallback color used if the card status cannot be determined.
    *   Default: `"#E0E0E0"` (Light Gray)
*   `"tile_border_color"`: Border color for each individual tile.
    *   Default: `"#c0c0c0"` (Gray)

## Due Cards Indicator

A small dot that appears in the center of tiles for cards that are scheduled for study today.

*   `"show_due_indicator"`: Determines if the "due" indicator should be displayed.
    *   Values: `true` (show) or `false` (hide).
    *   Default: `true`
*   `"due_indicator_color"`: Color of the "due" indicator.
    *   Default: `"#FF0000"` (Red)
*   `"due_indicator_size_ratio"`: Size proportion of the indicator relative to the tile size.
    *   For example, `0.33` means the indicator will be approximately 1/3 the size of the tile.
    *   Values: A number between `0.1` (small) and `1.0` (as large as the tile).
    *   Default: `0.33`

## Default Deck Filter

*   `"memorymosaic_default_deck_filter"`: Allows you to specify a deck name to filter the Memory Mosaic view on the main screen ("Deck List").
    *   If an empty string (`""`) is provided, all cards in the collection will be considered.
    *   If a deck name is specified (e.g., `"My Japanese Deck"` or `"Studies::Vocabulary"`), only cards belonging to that deck (and its subdecks) will be shown.
    *   This filter **does not** apply to the Memory Mosaic view within the "Overview" screen of a specific deck; there, Memory Mosaic will always show the cards of the currently viewed deck.
    *   Default: `""` (no filter)

## Grid Sizing and Layout Settings

These options control the appearance and behavior of the tile grid.

*   `"tile_default_size_px"`: Default size (width and height) of a tile's *content* in pixels. The grid will try to use this size if there is enough space.
    *   Default: `8`
*   `"tile_default_gap_px"`: Default spacing between tiles in pixels.
    *   Default: `0`
*   `"tile_min_size_px"`: Minimum size that a tile's *content* can have. If necessary, tiles will be reduced to this size to fit more in the grid.
    *   Default: `6`
*   `"grid_max_width_px"`: Maximum total width of the grid area in pixels.
    *   Default: `900`
*   `"grid_max_height_px"`: Maximum total height of the grid area in pixels. If the content exceeds, scrollbars may appear.
    *   Default: `800`
*   `"grid_padding_px"`: Padding (internal spacing) within the grid container, in pixels.
    *   Default: `5`

**Note about Tile Border Width (`tile_border_width_px`):**
Currently, the border width of each tile is fixed at `1px` directly in the code to match the CSS style. Making this configurable would require dynamically adjusting the tile's CSS style, which is not implemented at the moment. Only the border *color* (`tile_border_color`) is configurable.

After modifying the `config.json` directly, you may need to restart Anki for the changes to take effect, or they may be applied the next time Memory Mosaic is rendered, depending on the Anki version and the `config_did_change_hook`. If you edit through the Anki interface, changes are usually applied after saving and closing the configuration window.

## New Configuration Option

*   `"memorymosaic_default_sort_order"`: Defines the default tile ordering when loading.
    *   Valid options:
        *   `"id_asc"` (Default): Sorts by creation date (oldest first).
        *   `"ivl_asc"`: Sorts by ascending interval (smaller intervals first).
        *   `"ivl_desc"`: Sorts by descending interval (larger intervals first).
        *   `"due_asc"`: Sorts by due date (closest first).
    *   Default if not specified: `"id_asc"`. 