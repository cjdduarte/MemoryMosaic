# Placeholder for CardGrid addon 

from __future__ import annotations
import math # Importar o módulo math
from datetime import datetime # Para formatar timestamp
from typing import Any
# import os # Não é mais necessário para web exports

from aqt import mw
# from aqt.qt import QColor # Não estritamente necessário para hex strings
from aqt.gui_hooks import (
    overview_will_render_content, 
    deck_browser_will_render_content,
    sync_did_finish # Adicionado hook de sincronização
)
from aqt.overview import Overview, OverviewContent # Garante que ambos estão importados
from aqt.deckbrowser import DeckBrowser, DeckBrowserContent # Adicionadas importações do deckbrowser
from anki.cards import Card # Para type hinting
# from aqt.utils import showInfo # Para debug, se necessário
from aqt import dialogs # Para abrir o Browser
# from aqt.addons import AddonManager, ConfigEditor # ConfigEditor não é mais usado

# Importação do módulo de traduções
from .translations import tr

# Filtro de Deck Global Padrão para Memory Mosaic
# Se preenchido (ex: "Meu Deck Principal" ou "Deck::Subdeck"), o Memory Mosaic mostrará apenas cartões deste deck e seus subdecks.
# Se deixado como "" (string vazia), mostrará todos os cartões no Deck Browser, ou os cartões do deck atual no Overview.
# Esta constante será usada como parte da configuração padrão.
# MEMORYMOSAIC_DEFAULT_DECK_FILTER = "" # Movido para DEFAULT_CONFIG

# Não precisamos mais do MEMORYMOSAIC_WIDGET_ID para a status bar

# Configurações de Aparência e Comportamento do Memory Mosaic (Constantes Globais para dimensionamento)
# Estas não são configuráveis via config.json, mas são usadas pela lógica de renderização.
# MEMORYMOSAIC_DEFAULT_TILE_SIZE_PX = 8   
# MEMORYMOSAIC_DEFAULT_TILE_GAP_PX = 0    
# MEMORYMOSAIC_MIN_TILE_SIZE_PX = 6       
# MEMORYMOSAIC_MAX_GRID_WIDTH_PX = 900    
# MEMORYMOSAIC_MAX_GRID_HEIGHT_PX = 800   
# TILE_BORDER_WIDTH_PX = 1           
# GRID_PADDING_PX = 5                

# --- Início das Definições de Configuração ---

_memorymosaic_cached_config: dict | None = None
_session_sort_order_override: str | None = None # Armazena a ordenação da sessão atual

# DEFAULT_CONFIG removido

# ADDON_WINDOW_CONFIG_KEY = "memorymosaic_config_dialog" # Não é mais necessário

def _get_addon_config() -> dict:
    """Carrega a configuração do addon, utilizando um cache interno."""
    global _memorymosaic_cached_config
    if _memorymosaic_cached_config is not None:
        return _memorymosaic_cached_config

    if not mw or not hasattr(mw, "addonManager") or not mw.addonManager: 
        _memorymosaic_cached_config = {} # Cache com dict vazio se addonManager não estiver pronto
        return _memorymosaic_cached_config
        
    config = mw.addonManager.getConfig(__name__)
    
    if config is None: # Nenhuma configuração salva
        _memorymosaic_cached_config = {} # Cache com dict vazio
    else:
        _memorymosaic_cached_config = config # Cacheia a configuração lida
    
    return _memorymosaic_cached_config

# --- Fim das Definições de Configuração ---


# Cores de Fundo (Agora serão lidas da configuração, estas são apenas referências antigas)
# COLOR_NEW = "#FFFFFF"             # Branco (para Novos, não estudados)
# COLOR_MATURE = "#66B266"         # Verde Escuro
# COLOR_YOUNG_LEARN = "#A1E0A1"    # Verde Claro (para jovem/aprendizado)
# COLOR_RELEARNING_LAPSE = "#E53935" # Vermelho (para reaprendizado/lapso)
# COLOR_SUSPENDED_BURIED = "#222222" # Alterado para Cinza bem escuro
# COLOR_DEFAULT_BG = "#E0E0E0"        # Cinza Claro (fallback / erro ao obter cartão)

# Constantes de cor de borda e funções relacionadas removidas

# DEFAULT_TILE_BORDER_COLOR = "#c0c0c0" # Borda padrão para todos os tiles (agora em config)

def _should_show_due_indicator(card: Card | None, config: dict) -> bool:
    if not config.get("show_due_indicator"): # Padrão True se a chave não existir
        return False
    
    if not card:
        return False
    
    today = mw.col.sched.today

    # Apenas cartões em aprendizado (1), revisão (2), ou reaprendizado (3)
    if card.queue in [1, 2, 3]:
        if card.due <= today:
            return True
            
    return False

def _get_tile_bg_color(card: Card | None, config: dict) -> str:
    """Determina a cor de fundo do tile com base no status do cartão."""
    
    if not card:
        return config.get("color_default_bg")

    # 1. Verificar estados que anulam outros (suspenso/enterrado)
    if card.queue == -1 or card.queue == -2 or card.queue == -3:
        return config.get("color_suspended_buried")

    # 2. Se não suspenso/enterrado, verificar tipo
    if card.type == 0:
        return config.get("color_new")
    
    # 3. Se não suspenso/enterrado/novo, verificar se está em reaprendizado
    if card.queue == 3:
        return config.get("color_relearning_lapse")
    
    # 4. Se não ..., verificar se está em aprendizado
    if card.type == 1:
        return config.get("color_young_learn")
        
    # 5. Se não ..., verificar se é revisão
    if card.type == 2:
        if card.ivl >= 21:
            return config.get("color_mature")
        else:
            return config.get("color_young_learn")
            
    return config.get("color_default_bg")

def _format_last_review_date(cid: int) -> str:
    """Busca e formata a data da última revisão para um cartão."""
    last_rev_timestamp_ms = mw.col.db.scalar("SELECT max(id) FROM revlog WHERE cid = ?", cid)
    if last_rev_timestamp_ms:
        # Timestamp no revlog é em milissegundos
        last_rev_dt = datetime.fromtimestamp(last_rev_timestamp_ms / 1000)
        return last_rev_dt.strftime("%Y-%m-%d %H:%M")
    return "N/A"

def _open_card_in_browser(cid: int) -> None:
    """Abre o cartão com o cid especificado no Navegador do Anki."""
    try:
        search_string = f"cid:{cid}"
        browser = dialogs.open("Browser", mw)
        if browser:
            browser.form.searchEdit.lineEdit().setText(search_string)
            browser.onSearchActivated() 
        else:
            mw.onBrowse({"search": search_string})

    except Exception as e:
        print(f"Memory Mosaic: Erro ao tentar abrir o cartão {cid} no navegador: {e}")

def _render_memorymosaic_grid_html(overview_deck_name: str | None = None) -> str:
    """Renderiza o HTML para a grade de tiles com base nos cartões da coleção, 
       filtrados opcionalmente por MEMORYMOSAIC_DEFAULT_DECK_FILTER ou overview_deck_name."""
    global _session_sort_order_override # Necessário para modificar a global
    config = _get_addon_config()
    memorymosaic_default_deck_filter = config.get("memorymosaic_default_deck_filter")

    # Leitura da ordenação
    if _session_sort_order_override:
        current_sort_order_key = _session_sort_order_override
    else:
        configured_sort_order = config.get("memorymosaic_default_sort_order") # Não usa mais valor padrão aqui
        valid_sort_keys = ["id_asc", "ivl_asc", "ivl_desc", "due_asc"]
        if configured_sort_order in valid_sort_keys:
            current_sort_order_key = configured_sort_order
        else:
            current_sort_order_key = "id_asc" # Define explicitamente o padrão se ausente ou inválido
            if configured_sort_order is not None: # Log se foi fornecido um valor inválido
                print(f"Memory Mosaic: Valor inválido '{configured_sort_order}' para 'memorymosaic_default_sort_order' no config.json. Usando padrão 'id_asc'.")

    # Mapeamento para a cláusula ORDER BY do banco de dados
    sort_order_map = {
        "id_asc": "c.id asc",      # Ordenar por ID do cartão (data de criação)
        "ivl_asc": "c.ivl asc",    # Intervalo crescente
        "ivl_desc": "c.ivl desc",  # Intervalo decrescente
        "due_asc": "c.due asc"     # Data de vencimento mais próxima
    }
    db_sort_order = sort_order_map.get(current_sort_order_key, "c.id asc") # Padrão para id_asc

    # Carregar configurações de dimensionamento
    tile_default_size_px = config.get("tile_default_size_px")
    tile_default_gap_px = config.get("tile_default_gap_px")
    tile_min_size_px = config.get("tile_min_size_px")
    grid_max_width_px = config.get("grid_max_width_px")
    grid_max_height_px = config.get("grid_max_height_px")
    # tile_border_width_px = config.get("tile_border_width_px") # Esta linha foi comentada pois não é usada com fallback
    grid_padding_px = config.get("grid_padding_px")
    
    # A largura da borda do tile está atualmente fixa em 1px no CSS.
    # A lógica de cálculo precisa saber disso.
    TILE_BORDER_WIDTH_FIXED_PX = 1 

    search_query = ""
    # Priorizar o deck do overview se estivermos nessa tela
    if overview_deck_name: 
        search_query = f'deck:"{overview_deck_name}"'
    # Caso contrário (Deck Browser), usar o filtro global se definido
    elif memorymosaic_default_deck_filter: 
        search_query = f'deck:"{memorymosaic_default_deck_filter}"'
    # Se nenhum dos anteriores (estamos no Deck Browser e memorymosaic_default_deck_filter está vazio), 
    # search_query permanece "" (todos os cartões), o que é o comportamento desejado.

    try:
        # Aplicar a ordenação aqui
        cids = mw.col.find_cards(search_query, order=db_sort_order) 
    except AttributeError:
        return "<p>Aguardando coleção do Anki...</p>"

    card_count = len(cids) 

    title_html_no_cards = f'<h4 style="text-align: center; margin-bottom: 10px;">{tr("addon_title")}:</h4>' # Título para quando não há cards
    
    if card_count == 0:
        message_no_cards = f'<p style="margin-top: 20px; margin-bottom: 15px; text-align: center;">{tr("no_cards")}</p>'
        
        # Informações do filtro para o rodapé (mesmo sem cartões)
        filter_info_footer_content_no_cards = ""
        active_filter_description_no_cards = ""
        if overview_deck_name:
            active_filter_description_no_cards = f'{tr("current_filter", filter=overview_deck_name)}'
        elif memorymosaic_default_deck_filter:
            active_filter_description_no_cards = f'{tr("current_filter", filter=memorymosaic_default_deck_filter)} ({tr("filter_subdecks")})'
        else:
            active_filter_description_no_cards = tr("all_decks")
        filter_info_footer_content_no_cards = f'<p style="margin: 3px 0;"><b>{tr("current_filter", filter="")}</b> {active_filter_description_no_cards}</p>'
        
        filter_info_footer_no_cards_html = f'''
<div id="memorymosaic-filter-footer" style="text-align: center; margin-top: 0px; padding-top: 0px; font-size: 0.9em; max-width: {grid_max_width_px}px; margin-left: auto; margin-right: auto;">
    {filter_info_footer_content_no_cards}
</div>
'''
        # Não há contagem de status se não há cartões
        return title_html_no_cards + message_no_cards + filter_info_footer_no_cards_html

    # Título e Controles de Ordenação (agora combinados)
    title_and_controls_html = f'''
<div id="memorymosaic-header-controls" style="display: flex; justify-content: center; align-items: center; margin-bottom: 10px; margin-top: 10px;">
    <h4 style="margin: 0 15px 0 0; padding:0;">{tr("addon_title")}:</h4>
    <select id="memorymosaic-sort-order" onchange="onMemoryMosaicSortOrderChanged(this.value)" style="padding: 5px; border-radius: 4px; border: 1px solid #ccc;">
        <option value="id_asc">{tr("sort_by_creation")}</option>
        <option value="ivl_asc">{tr("sort_by_interval_asc")}</option>
        <option value="ivl_desc">{tr("sort_by_interval_desc")}</option>
        <option value="due_asc">{tr("sort_by_due_date")}</option>
    </select>
</div>
'''

    current_tile_size_px = tile_default_size_px 
    current_tile_gap_px = tile_default_gap_px
    
    if card_count > 0:
        ANKI_TABLE_CELL_PADDING_PX = 5 
        TITLE_AREA_ESTIMATED_HEIGHT_PX = 35 

        eff_grid_width = grid_max_width_px - (2 * ANKI_TABLE_CELL_PADDING_PX) - (2 * grid_padding_px)
        eff_grid_height = (grid_max_height_px - 
                           TITLE_AREA_ESTIMATED_HEIGHT_PX - 
                           (2 * ANKI_TABLE_CELL_PADDING_PX) - 
                           (2 * grid_padding_px))

        eff_grid_height = max(eff_grid_height, tile_min_size_px) 

        estimated_s_content = math.sqrt((eff_grid_width * eff_grid_height) / card_count) - (2 * TILE_BORDER_WIDTH_FIXED_PX + current_tile_gap_px)
        estimated_s_content = math.floor(estimated_s_content)
        
        # Limitando o tamanho estimado entre o mínimo e o padrão
        s_for_calc = min(tile_default_size_px, max(tile_min_size_px, estimated_s_content))
        
        final_s_content = s_for_calc  # Inicializa com o valor calculado, não com o mínimo
        temp_s_content = s_for_calc
        
        while temp_s_content >= tile_min_size_px:
            tile_visual_dim = temp_s_content + (2 * TILE_BORDER_WIDTH_FIXED_PX)
            if (temp_s_content + current_tile_gap_px) <= 0: 
                num_cols_css = 0
            else:
                num_cols_css = math.floor((eff_grid_width + current_tile_gap_px) / (temp_s_content + current_tile_gap_px))

            if num_cols_css <= 0: 
                temp_s_content -=1
                continue

            width_occupied_visual = num_cols_css * tile_visual_dim + max(0, num_cols_css - 1) * current_tile_gap_px
            
            if width_occupied_visual > eff_grid_width:
                temp_s_content -= 1
                continue 

            num_rows_needed = math.ceil(card_count / num_cols_css)
            height_occupied_visual = num_rows_needed * tile_visual_dim + max(0, num_rows_needed - 1) * current_tile_gap_px

            if height_occupied_visual <= eff_grid_height:
                final_s_content = temp_s_content 
                break 
            
            temp_s_content -= 1
        
        current_tile_size_px = final_s_content
    
    due_indicator_color = config.get("due_indicator_color") # Padrão Vermelho
    due_indicator_size_ratio = config.get("due_indicator_size_ratio") # Padrão 25%
    calculated_due_indicator_size_px = max(1, math.floor(current_tile_size_px * due_indicator_size_ratio if due_indicator_size_ratio is not None and current_tile_size_px is not None else 1))

    tile_size_px = current_tile_size_px
    tile_gap_px = current_tile_gap_px 
    due_indicator_size_px = calculated_due_indicator_size_px 

    tiles_html_list = []
    color_counts = {} # Inicializa o contador de cores

    for cid in cids: 
        card = mw.col.get_card(cid)
        bg_color = _get_tile_bg_color(card, config)
        color_counts[bg_color] = color_counts.get(bg_color, 0) + 1 # Incrementa a contagem da cor
        
        due_indicator_html = ""
        if _should_show_due_indicator(card, config):
            indicator_style = (
                f"position: absolute; top: 50%; left: 50%; "
                f"width: {due_indicator_size_px}px; height: {due_indicator_size_px}px; "
                f"background-color: {due_indicator_color}; border-radius: 50%; " 
                f"transform: translate(-50%, -50%); pointer-events: none;" 
            )
            due_indicator_html = f'<div style="{indicator_style}"></div>'

        tooltip_parts = [tr("tooltip_card_id", cid=cid)]
        if card:
            deck_name = mw.col.decks.name(card.did)
            tooltip_parts.append(tr("tooltip_deck", deck=deck_name))
            last_review_str = _format_last_review_date(cid)
            if last_review_str == "N/A":
                tooltip_parts.append(tr("tooltip_never_reviewed"))
            else:
                tooltip_parts.append(tr("tooltip_last_review", date=last_review_str))
            tooltip_parts.append(tr("tooltip_due", due=card.due))
            tooltip_parts.append(tr("tooltip_queue", queue=card.queue))
            tooltip_parts.append(tr("tooltip_type", type=card.type))
            tooltip_parts.append(tr("tooltip_interval", interval=card.ivl))
        title_tooltip = "&#10;".join(tooltip_parts)

        border_color_from_config = config.get('tile_border_color') # Padrão Cinza
        # A largura da borda é 1px, conforme TILE_BORDER_WIDTH_FIXED_PX. O estilo CSS reflete isso.
        tile_style = (
            f"position: relative; width: {tile_size_px}px; height: {tile_size_px}px; "
            f"background-color: {bg_color}; border: {TILE_BORDER_WIDTH_FIXED_PX}px solid {border_color_from_config};"
        )

        tile_html = (
            f'<div class="memorymosaic-tile" data-cid="{cid}" title="{title_tooltip}" style="{tile_style}" onclick="onMemoryMosaicTileClick({cid})">'
            f'{due_indicator_html}' 
            f'</div>'
        )
        tiles_html_list.append(tile_html)
    
    all_tiles_html = "".join(tiles_html_list)

    grid_container_style = (
        f'display: grid; grid-template-columns: repeat(auto-fit, {tile_size_px}px); '
        f'gap: {tile_gap_px}px; margin-top: 0px; margin-bottom: 15px;'
        f'padding: {grid_padding_px}px; max-width: {grid_max_width_px}px; max-height: {grid_max_height_px}px; '
        f'overflow: auto; justify-content: center; align-content: center;'
    )

    # Mapeamento de cores para rótulos do sumário
    color_to_label_map = {
        config.get("color_new"): tr("card_status_new"),
        config.get("color_mature"): tr("card_status_mature"),
        config.get("color_young_learn"): tr("card_status_young"),
        config.get("color_relearning_lapse"): tr("card_status_relearning"),
        config.get("color_suspended_buried"): tr("card_status_suspended"),
        config.get("color_default_bg"): tr("card_status_default")
    }

    # Informação do filtro para o rodapé
    filter_info_footer_content = ""
    active_filter_description = ""
    if overview_deck_name:
        active_filter_description = f'{tr("current_filter", filter=overview_deck_name)}'
    elif memorymosaic_default_deck_filter:
        active_filter_description = f'{tr("current_filter", filter=memorymosaic_default_deck_filter)} ({tr("filter_subdecks")})'
    else:
        active_filter_description = tr("all_decks")
    filter_info_footer_content = f'<p style="margin: 3px 0;"><b>{tr("showing")}:</b> {active_filter_description} ({tr("total_cards", count=card_count)})</p>'

    filter_info_footer_html = f'''
<div id="memorymosaic-filter-footer" style="text-align: center; margin-top: 0px; padding-top: 0px; font-size: 0.9em; max-width: {grid_max_width_px}px; margin-left: auto; margin-right: auto;">
    {filter_info_footer_content}
</div>
'''

    # Contagem de cores para o sumário (agora antes da grade)
    color_summary_items_html_parts = []
    sorted_colors = sorted(
        color_counts.items(), 
        key=lambda item: color_to_label_map.get(item[0], "ŻŻŻ " + item[0]).lower()
    )
    for color_hex, count in sorted_colors:
        label = color_to_label_map.get(color_hex, f"Cor Desconhecida ({color_hex})")
        color_swatch_style = f"display: inline-block; width: 12px; height: 12px; background-color: {color_hex}; border: 1px solid #888; margin-right: 5px; vertical-align: middle;"
        color_summary_items_html_parts.append(f'<span style="display: inline-flex; align-items: center; white-space: nowrap;"><span style="{color_swatch_style}"></span>{label}: {count}</span>')
    
    color_summary_items_html = ' ' .join(color_summary_items_html_parts) # Espaço entre itens

    color_summary_container_html = f'''
<div id="memorymosaic-color-summary-container" style="max-width: {grid_max_width_px}px; margin-left: auto; margin-right: auto; margin-bottom: 5px; padding: 8px 0; display: flex; align-items: center; justify-content: center; flex-wrap: wrap; gap: 10px 15px; font-size: 0.9em;">
    <p style="font-weight: bold; margin: 0; white-space: nowrap;">{tr("summary_title")}:</p>
    {color_summary_items_html}
</div>
'''

    grid_html_content = f'<div id="memorymosaic-grid-container" style="{grid_container_style}">{all_tiles_html}</div>'

    script_html = f"""
<script>
    // Garante que o cursor volte ao normal quando a grade for redesenhada
    document.body.style.cursor = 'default';

    let currentSortOrder = '{current_sort_order_key}'; // Injetado pelo Python

    function onMemoryMosaicTileClick(cid) {{
        pycmd("memorymosaic_open_card:" + cid);
    }}

    function onMemoryMosaicSortOrderChanged(newSortOrder) {{
        document.body.style.cursor = 'wait'; // Muda o cursor para ampulheta
        pycmd("memorymosaic_sort_change:" + newSortOrder);
    }}

    function setMemoryMosaicSortOrderDropdown(sortOrderToSet) {{
        const selectElement = document.getElementById('memorymosaic-sort-order');
        if (selectElement) {{
            selectElement.value = sortOrderToSet;
        }}
        currentSortOrder = sortOrderToSet;
    }}

    // Inicializa o dropdown com a ordenação correta ao carregar a grade
    (function() {{
        setMemoryMosaicSortOrderDropdown(currentSortOrder);
    }})();
</script>
"""

    return title_and_controls_html + color_summary_container_html + grid_html_content + filter_info_footer_html + script_html

def request_refresh_if_memorymosaic_visible() -> None:
    """Força o refresh do Deck Browser ou Overview se o Memory Mosaic estiver visível."""
    if mw.state == "deckBrowser":
        if hasattr(mw, 'deckBrowser') and mw.deckBrowser:
            mw.deckBrowser.refresh()
            mw.deckBrowser.show() # Adicionado para garantir que a atualização seja visível
    elif mw.state == "overview":
        if hasattr(mw, 'overview') and mw.overview:
            mw.overview.refresh()
            mw.overview.show() # Adicionado para garantir que a atualização seja visível

def on_overview_will_render_content(overview_obj: Overview, content_obj: OverviewContent) -> None:
    """Adiciona o container do Memory Mosaic ao conteúdo da visão geral do deck."""
    current_deck_name: str | None = None
    current_deck_id: int | None = None

    try:
        # Tenta o método direto primeiro, comum em versões mais antigas ou certas APIs
        current_deck_id = overview_obj.deck_id
    except AttributeError:
        # Fallback para versões onde deck_id não está diretamente em overview_obj
        # ou para obter o deck ativo de forma mais geral.
        if mw and hasattr(mw, "col") and mw.col and hasattr(mw.col, "decks"):
            current_deck_id = mw.col.decks.get_current_id()
        else:
            print("Memory Mosaic: Não foi possível obter mw.col.decks para determinar o deck_id na visão geral.")
            # Considerar não renderizar a grade ou renderizar com filtro global se mw.col não estiver pronto

    if current_deck_id: 
        try:
            deck = mw.col.decks.get(current_deck_id)
            if deck:
                current_deck_name = deck['name']
        except Exception as e:
            print(f"Memory Mosaic: Não foi possível obter o nome do deck para did {current_deck_id}: {e}")
            
    grid_html = _render_memorymosaic_grid_html(overview_deck_name=current_deck_name)
    content_obj.table += grid_html

def on_deck_browser_will_render_content(deck_browser_obj: DeckBrowser, content_obj: DeckBrowserContent) -> None:
    """Adiciona o container do Memory Mosaic ao conteúdo da lista de decks (deck browser)."""
    grid_html = _render_memorymosaic_grid_html()
    content_obj.stats += grid_html

# Hooks
overview_will_render_content.append(on_overview_will_render_content)
deck_browser_will_render_content.append(on_deck_browser_will_render_content)
sync_did_finish.append(request_refresh_if_memorymosaic_visible)


# --- Lógica de Configuração Removida (on_memorymosaic_settings_clicked, memorymosaic_get_default_config) ---


def handle_memorymosaic_pycmd(handled: tuple[bool, Any], message: str, context: Any) -> tuple[bool, Any]:
    """Manipula comandos pycmd específicos do Memory Mosaic enviados da webview."""
    if handled[0]: 
        return handled

    if message.startswith("memorymosaic_open_card:"):
        try:
            cid_str = message.split(":")[1]
            cid = int(cid_str)
            _open_card_in_browser(cid)
            return (True, None) 
        except ValueError:
            print(f"Memory Mosaic: Erro ao processar pycmd '{message}'. CID inválido: '{cid_str}'.")
            return (True, None) 
        except Exception as e:
            print(f"Memory Mosaic: Erro inesperado ao processar pycmd '{message}': {e}")
            return (True, None) 
    elif message.startswith("memorymosaic_sort_change:"):
        try:
            global _session_sort_order_override # Necessário para modificar a global
            new_sort_order = message.split(":")[1]
            valid_sort_orders = ["id_asc", "ivl_asc", "ivl_desc", "due_asc"]
            if new_sort_order in valid_sort_orders:
                _session_sort_order_override = new_sort_order # Salva na variável de sessão
                # mw.pm.profile['memorymosaic_sort_order'] = new_sort_order # REMOVIDO: Não salvar no perfil
                request_refresh_if_memorymosaic_visible()
            else:
                print(f"Memory Mosaic: Ordem de sorteio inválida recebida: {new_sort_order}")
            return (True, None)
        except Exception as e:
            print(f"Memory Mosaic: Erro ao processar memorymosaic_sort_change: {e}")
            return (True, None)
    
    return (False, None) 


from aqt import gui_hooks
gui_hooks.webview_did_receive_js_message.append(handle_memorymosaic_pycmd)

# Remover setConfigAction e setWebExports
# if mw and mw.addonManager:
#     mw.addonManager.setConfigAction(__name__, on_memorymosaic_settings_clicked) # Removido

# if mw and hasattr(mw, "addonManager") and mw.addonManager:
#     addon_package = mw.addonManager.addonFromModule(__name__)
#     if addon_package:
#         user_files_dir = os.path.join(mw.pm.addonFolder(), addon_package, "web") # os não importado
#         if os.path.isdir(user_files_dir):
#             mw.addonManager.setWebExports(__name__, r"web/.*") # Removido
#         else:
#             print(f"Memory Mosaic: Pasta 'web' não encontrada. A tela de configuração customizada não funcionaria.")


# Após a configuração ser salva (via editor JSON padrão do Anki), 
# precisamos atualizar a visualização se estiver visível.
def on_config_changed_refresh_memorymosaic(addon_name: str, key: str, new_value: Any):
    # O hook config_did_change_hook passa o nome do addon, não o objeto do addon.
    if addon_name == __name__: 
        global _memorymosaic_cached_config
        _memorymosaic_cached_config = None # Invalida o cache
        print(f"Memory Mosaic: Configuração alterada ('{key}'), cache invalidado e visualização será atualizada.")
        request_refresh_if_memorymosaic_visible()

if mw and hasattr(mw, "addonManager") and hasattr(mw.addonManager, "config_did_change_hook"): 
    mw.addonManager.config_did_change_hook.append(on_config_changed_refresh_memorymosaic)
elif mw and hasattr(mw, "config") and hasattr(mw.config, "config_did_change_hook"): # Algumas versões mais antigas podem ter o hook em mw.config
     mw.config.config_did_change_hook.append(on_config_changed_refresh_memorymosaic)


# O código anterior de add_memorymosaic_placeholder_widget e seu hook main_window_did_init foi removido.
# Se houvesse outro código além do placeholder da status bar, ele permaneceria.
# Neste caso, o arquivo __init__.py só tinha isso. 