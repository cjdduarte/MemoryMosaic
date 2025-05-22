# Placeholder for CardGrid addon 

from __future__ import annotations
import math
from datetime import datetime
from typing import Any

# Adicionar este import para interpolação de cores
import colorsys

from aqt import mw
from aqt.gui_hooks import (
    overview_will_render_content, 
    deck_browser_will_render_content,
    sync_did_finish,
    webview_did_receive_js_message,
    profile_will_close,
    sync_will_start,
    collection_will_temporarily_close
)
from aqt.overview import Overview, OverviewContent
from aqt.deckbrowser import DeckBrowser, DeckBrowserContent
from anki.cards import Card
from aqt import dialogs

from .translations import tr

# Variáveis globais para controle de estado
_memorymosaic_cached_config: dict | None = None
_session_sort_order_override: str | None = None
_session_view_mode_override: str | None = None
_session_gradient_field_override: str | None = None
_is_syncing: bool = False
_is_closing: bool = False

# Novas variáveis de sessão para paginação
_session_current_display_limit: int | None = None
_session_last_filter_details: tuple | None = None # (filter_str, sort_order, view_mode, gradient_field)

def _get_addon_config() -> dict:
    """Carrega a configuração do addon, utilizando um cache interno."""
    global _memorymosaic_cached_config
    if _memorymosaic_cached_config is not None:
        return _memorymosaic_cached_config

    if not mw or not hasattr(mw, "addonManager") or not mw.addonManager: 
        _memorymosaic_cached_config = {}
        return _memorymosaic_cached_config
        
    config = mw.addonManager.getConfig(__name__)
    _memorymosaic_cached_config = config if config is not None else {}
    return _memorymosaic_cached_config

def _should_show_due_indicator(card: Card | None, config: dict, today_for_due_calc: int) -> bool:
    if not config.get("show_due_indicator"):
        return False
    
    if not card:
        return False
    
    return card.queue in [1, 2, 3] and card.due <= today_for_due_calc

def _get_tile_bg_color(card: Card | None, config: dict) -> str:
    """Determina a cor de fundo do tile com base no status do cartão."""
    if not mw or not mw.col or not config:
        return config.get("color_default_bg")

    if not card:
        return config.get("color_default_bg")

    # 1. Verificar estados que anulam outros (suspenso/enterrado)
    if card.queue in [-1, -2, -3]:
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
        return config.get("color_mature") if card.ivl >= 21 else config.get("color_young_learn")
            
    return config.get("color_default_bg")

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
    
    # Variáveis de sessão para o modo de visualização e campo de gradiente
    global _session_view_mode_override
    global _session_gradient_field_override
    
    # Variáveis de sessão para paginação
    global _session_current_display_limit
    global _session_last_filter_details

    # Verificação crucial no início da função
    if not mw or not mw.col or not mw.col.sched or not mw.col.db or not mw.col.decks:
        # Tenta usar tr() para a mensagem, com fallback se tr() não estiver disponível
        # ou se as traduções ainda não foram carregadas corretamente.
        try:
            return f"<p>{tr('waiting_for_anki_collection_long')}</p>"
        except Exception: # Captura ampla se tr() ou suas dependências falharem
            return "<p>Memory Mosaic: Aguardando a coleção de dados do Anki estar completamente pronta...</p>"
            
    config = _get_addon_config()
    memorymosaic_default_deck_filter = config.get("memorymosaic_default_deck_filter")

    # Espaçamento para separar o addon do conteúdo acima
    spacing_html = '<div style="margin-top: 25px; border-top: 1px solid #e0e0e0; padding-top: 15px;"></div>'

    # >>> PASSO 1: Otimizar mw.col.sched.today <<<
    today_val = mw.col.sched.today
    # >>> FIM PASSO 1 <<<

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
    
    # Leitura do modo de visualização
    if _session_view_mode_override:
        current_view_mode = _session_view_mode_override
    else:
        configured_view_mode = config.get("memorymosaic_default_view_mode")
        valid_view_modes = ["categorical", "gradient"]
        if configured_view_mode in valid_view_modes:
            current_view_mode = configured_view_mode
        else:
            current_view_mode = "categorical"
            if configured_view_mode is not None:
                print(f"Memory Mosaic: Valor inválido '{configured_view_mode}' para 'memorymosaic_default_view_mode' no config.json. Usando padrão 'categorical'.")
    
    # Leitura do campo de gradiente
    if _session_gradient_field_override:
        current_gradient_field = _session_gradient_field_override
    else:
        configured_gradient_field = config.get("memorymosaic_default_gradient_field")
        valid_gradient_fields = ["factor", "ivl", "lapses", "due"]
        if configured_gradient_field in valid_gradient_fields:
            current_gradient_field = configured_gradient_field
        else:
            current_gradient_field = "ivl"
            if configured_gradient_field is not None:
                print(f"Memory Mosaic: Valor inválido '{configured_gradient_field}' para 'memorymosaic_default_gradient_field' no config.json. Usando padrão 'ivl'.")

    # Mapeamento para a cláusula ORDER BY do banco de dados
    sort_order_map = {
        "id_asc": "c.id asc",      # Ordenar por ID do cartão (data de criação)
        "ivl_asc": "c.ivl asc",    # Intervalo crescente
        "ivl_desc": "c.ivl desc",  # Intervalo decrescente
        "due_asc": "c.due asc"     # Data de vencimento mais próxima
    }
    db_sort_order = sort_order_map.get(current_sort_order_key) # Padrão para id_asc

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

    # Configurações de Paginação
    initial_card_load_count = config.get("initial_card_load_count")
    incremental_card_load_count = config.get("incremental_card_load_count")

    search_query_final = ""
    # Priorizar o deck do overview se estivermos nessa tela
    if overview_deck_name: 
        search_query_final = f'deck:"{overview_deck_name}"'
    # Caso contrário (Deck Browser), usar o filtro global se definido
    elif memorymosaic_default_deck_filter: 
        search_query_final = f'deck:"{memorymosaic_default_deck_filter}"'
    # Se nenhum dos anteriores (estamos no Deck Browser e memorymosaic_default_deck_filter está vazio), 
    # search_query_final permanece "" (todos os cartões), o que é o comportamento desejado.

    # Lógica de reset da paginação
    current_filter_details = (search_query_final, current_sort_order_key, current_view_mode, current_gradient_field)
    if _session_last_filter_details != current_filter_details:
        _session_current_display_limit = None # Resetar ao mudar filtro/ordem
        _session_last_filter_details = current_filter_details

    if _session_current_display_limit is None:
        _session_current_display_limit = initial_card_load_count

    try:
        # Aplicar a ordenação aqui
        all_cids_full_list = mw.col.find_cards(search_query_final, order=db_sort_order)
    except AttributeError: # Esta exceção já existia e é uma boa proteção
        # Tenta usar tr() para a mensagem
        try:
            return f"<p>{tr('waiting_for_anki_collection_short')}</p>"
        except Exception:
            return "<p>Aguardando coleção do Anki...</p>"

    total_cards_in_filter = len(all_cids_full_list)

    # Aplicar o limite de exibição (paginação)
    # Se _session_current_display_limit for float('inf'), significa mostrar todos
    limit_for_slicing = _session_current_display_limit 
    if limit_for_slicing == float('inf'):
        # Não podemos fatiar com float('inf'), então usamos o tamanho total ou None para pegar tudo
        limit_for_slicing = None 
    
    cids = all_cids_full_list[:limit_for_slicing] # Usa a lista fatiada para renderização

    card_count_displayed = len(cids) # Número de cartões realmente exibidos

    # >>> PASSO 2: Otimizar busca da última data de revisão <<<
    last_review_timestamps_map = {}
    if cids:
        # Busca todos os timestamps de uma vez
        # O resultado é uma lista de tuplas (cid, timestamp_ms)
        query_results = mw.col.db.all(
            f"SELECT cid, MAX(id) FROM revlog WHERE cid IN ({ ', '.join(map(str, cids)) }) GROUP BY cid"
        )
        if query_results:
            for cid_db, timestamp_ms in query_results:
                if timestamp_ms:
                    last_review_timestamps_map[cid_db] = timestamp_ms
    # >>> FIM PASSO 2 <<<

    title_html_no_cards = f'<h4 style="text-align: center; margin-bottom: 10px;">{tr("addon_title")}:</h4>' # Título para quando não há cards
    
    if card_count_displayed == 0:
        # Mesmo se não há cartões exibidos, pode haver cartões no filtro total que seriam mostrados com "Mostrar Todos"
        if total_cards_in_filter > 0 and _session_current_display_limit != float('inf'):
             message_no_cards = f'<p style="margin-top: 20px; margin-bottom: 15px; text-align: center;">{tr("no_cards_in_initial_load", count=total_cards_in_filter)}</p>'
        else:
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
        return spacing_html + title_html_no_cards + message_no_cards + filter_info_footer_no_cards_html

    # Título e Controles de Ordenação e Visualização (agora com modo de visualização)
    title_and_controls_html = f'''
<div id="memorymosaic-header-controls" style="display: flex; justify-content: center; align-items: center; margin-bottom: 10px; margin-top: 10px; flex-wrap: wrap; gap: 10px;">
    <h4 style="margin: 0 15px 0 0; padding:0;">{tr("addon_title")}:</h4>
    
    <div style="margin-right: 15px;">
        <label for="memorymosaic-sort-order" style="margin-right: 5px; font-weight: normal; font-size: 14px;">{config.get("label_sort_order_group")}</label>
        <select id="memorymosaic-sort-order" onchange="onMemoryMosaicSortOrderChanged(this.value)" style="padding: 5px; border-radius: 4px; border: 1px solid #ccc;">
            <option value="id_asc">{tr("sort_by_creation")}</option>
            <option value="ivl_asc">{tr("sort_by_interval_asc")}</option>
            <option value="ivl_desc">{tr("sort_by_interval_desc")}</option>
            <option value="due_asc">{tr("sort_by_due_date")}</option>
        </select>
    </div>
    
    <div style="margin-right: 15px;">
        <label for="memorymosaic-view-mode" style="margin-right: 5px; font-weight: normal; font-size: 14px;">{tr("view_mode")}:</label>
        <select id="memorymosaic-view-mode" onchange="onMemoryMosaicViewModeChanged(this.value)" style="padding: 5px; border-radius: 4px; border: 1px solid #ccc;">
            <option value="categorical">{tr("view_categorical")}</option>
            <option value="gradient">{tr("view_gradient")}</option>
        </select>
    </div>
    
    <div id="memorymosaic-gradient-field-container" style="display: {('block' if current_view_mode == 'gradient' else 'none')};">
        <label for="memorymosaic-gradient-field" style="margin-right: 5px; font-weight: normal; font-size: 14px;">{tr("gradient_field")}:</label>
        <select id="memorymosaic-gradient-field" onchange="onMemoryMosaicGradientFieldChanged(this.value)" style="padding: 5px; border-radius: 4px; border: 1px solid #ccc;">
            <option value="factor">{tr("gradient_field_factor")}</option>
            <option value="ivl">{tr("gradient_field_ivl")}</option>
            <option value="lapses">{tr("gradient_field_lapses")}</option>
            <option value="due">{tr("gradient_field_due")}</option>
        </select>
    </div>
</div>
'''

    current_tile_size_px = tile_default_size_px 
    current_tile_gap_px = tile_default_gap_px
    
    if card_count_displayed > 0:
        ANKI_TABLE_CELL_PADDING_PX = 5 
        TITLE_AREA_ESTIMATED_HEIGHT_PX = 35 

        eff_grid_width = grid_max_width_px - (2 * ANKI_TABLE_CELL_PADDING_PX) - (2 * grid_padding_px)
        eff_grid_height = (grid_max_height_px - 
                           TITLE_AREA_ESTIMATED_HEIGHT_PX - 
                           (2 * ANKI_TABLE_CELL_PADDING_PX) - 
                           (2 * grid_padding_px))

        eff_grid_height = max(eff_grid_height, tile_min_size_px) 

        estimated_s_content = math.sqrt((eff_grid_width * eff_grid_height) / card_count_displayed) - (2 * TILE_BORDER_WIDTH_FIXED_PX + current_tile_gap_px)
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

            num_rows_needed = math.ceil(card_count_displayed / num_cols_css)
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
    gradient_value_stats = {} # Estatísticas para o modo gradiente

    # >>> INÍCIO DAS NOVAS ADIÇÕES PARA IVL DINÂMICO <<<
    actual_min_ivl_for_norm: int | None = None
    actual_max_ivl_for_norm: int | None = None
    normalize_ivl_active = config.get("gradient_ivl_normalize") # Padrão True conforme config.md

    if current_view_mode == "gradient" and current_gradient_field == "ivl" and normalize_ivl_active:
        temp_min_ivl = float('inf')
        temp_max_ivl = float('-inf')
        found_any_ivl = False
        for i_cid in cids: # Usar uma variável de loop diferente para não conflitar com 'cid' depois
            card_obj = mw.col.get_card(i_cid)
            if card_obj and card_obj.type != 0 and card_obj.queue not in [-1, -2, -3]:
                # Considerar apenas cartões que efetivamente usarão o gradiente
                temp_min_ivl = min(temp_min_ivl, card_obj.ivl)
                temp_max_ivl = max(temp_max_ivl, card_obj.ivl)
                found_any_ivl = True
        
        if found_any_ivl:
            actual_min_ivl_for_norm = int(temp_min_ivl)
            actual_max_ivl_for_norm = int(temp_max_ivl)
        else:
            # Fallback para config se nenhum cartão aplicável for encontrado
            actual_min_ivl_for_norm = config.get("gradient_ivl_min")
            actual_max_ivl_for_norm = config.get("gradient_ivl_max")
        
        # Garantir que min não seja maior que max, e que não sejam iguais para _get_gradient_color
        if actual_min_ivl_for_norm is not None and actual_max_ivl_for_norm is not None:
            if actual_min_ivl_for_norm > actual_max_ivl_for_norm: # Caso raro, mas possível se houver apenas um valor e ele for usado para ambos
                 actual_max_ivl_for_norm = actual_min_ivl_for_norm 
            # _get_gradient_color já trata min_val == max_val retornando a cor média
    # >>> FIM DAS NOVAS ADIÇÕES PARA IVL DINÂMICO <<<

    # >>> PASSO 3: Otimizar leitura de config para tooltip IVL (modo gradiente, campo ivl, normalização desligada) <<<
    tooltip_config_min_ivl_for_gradient_tooltip: int | None = None
    tooltip_config_max_ivl_for_gradient_tooltip: int | None = None
    if current_view_mode == "gradient" and current_gradient_field == "ivl" and not (normalize_ivl_active and actual_min_ivl_for_norm is not None and actual_max_ivl_for_norm is not None):
        tooltip_config_min_ivl_for_gradient_tooltip = config.get("gradient_ivl_min")
        tooltip_config_max_ivl_for_gradient_tooltip = config.get("gradient_ivl_max")
    # >>> FIM PASSO 3 <<<

    for cid in cids: 
        card = mw.col.get_card(cid)
        
        # Determinar a cor com base no modo de visualização
        if current_view_mode == "gradient":
            bg_color = "" # Inicializa bg_color
            if current_gradient_field == "ivl":
                min_limit_for_color = config.get("gradient_ivl_min")
                max_limit_for_color = config.get("gradient_ivl_max")
                if normalize_ivl_active and actual_min_ivl_for_norm is not None and actual_max_ivl_for_norm is not None:
                    min_limit_for_color = actual_min_ivl_for_norm
                    max_limit_for_color = actual_max_ivl_for_norm
                
                bg_color = _get_gradient_tile_color(card, current_gradient_field, config, today_val, ivl_min_override=min_limit_for_color, ivl_max_override=max_limit_for_color)
            else:
                # Para outros campos, não há overrides de ivl
                bg_color = _get_gradient_tile_color(card, current_gradient_field, config, today_val)
            
            # Coletar estatísticas para o modo gradiente
            if card and current_gradient_field in ["factor", "ivl", "lapses", "due"]:
                field_value = 0
                if current_gradient_field == "factor":
                    field_value = card.factor
                elif current_gradient_field == "ivl":
                    field_value = card.ivl
                elif current_gradient_field == "lapses":
                    field_value = card.lapses
                elif current_gradient_field == "due" and card.queue == 2:
                    today = mw.col.sched.today
                    field_value = max(0, card.due - today)
                
                # Agrupar valores para estatísticas simplificadas
                if field_value not in gradient_value_stats:
                    gradient_value_stats[field_value] = 0
                gradient_value_stats[field_value] += 1
        else:
            bg_color = _get_tile_bg_color(card, config)
        
        color_counts[bg_color] = color_counts.get(bg_color, 0) + 1 # Incrementa a contagem da cor
        
        due_indicator_html = ""
        if _should_show_due_indicator(card, config, today_val):
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
            
            # last_review_str = _format_last_review_date(cid) # <--- REMOVIDO
            last_rev_timestamp_ms = last_review_timestamps_map.get(cid)
            if last_rev_timestamp_ms:
                last_rev_dt = datetime.fromtimestamp(last_rev_timestamp_ms / 1000)
                last_review_str = last_rev_dt.strftime("%Y-%m-%d %H:%M")
            else:
                last_review_str = "N/A"

            if last_review_str == "N/A":
                tooltip_parts.append(tr("tooltip_never_reviewed"))
            else:
                tooltip_parts.append(tr("tooltip_last_review", date=last_review_str))
            tooltip_parts.append(tr("tooltip_due", due=card.due))
            tooltip_parts.append(tr("tooltip_queue", queue=card.queue))
            tooltip_parts.append(tr("tooltip_type", type=card.type))
            tooltip_parts.append(tr("tooltip_interval", interval=card.ivl))
            tooltip_parts.append(tr("tooltip_factor", factor=card.factor))
            
            # Adicionar informações específicas do gradiente se no modo gradiente
            if current_view_mode == "gradient":
                if current_gradient_field == "factor":
                    tooltip_parts.append(tr("gradient_tooltip_value", value=card.factor))
                    tooltip_parts.append(tr("gradient_tooltip_range", min=config.get("gradient_factor_min"), max=config.get("gradient_factor_max")))
                elif current_gradient_field == "ivl":
                    tooltip_parts.append(tr("gradient_tooltip_value", value=card.ivl))
                    
                    # normalize_ivl_active e actual_min/max_ivl_for_norm já foram definidos anteriormente
                    if normalize_ivl_active and actual_min_ivl_for_norm is not None and actual_max_ivl_for_norm is not None:
                        # Usar a faixa dinâmica para o tooltip
                        tooltip_parts.append(tr("gradient_tooltip_range", min=actual_min_ivl_for_norm, max=actual_max_ivl_for_norm))
                        # Não é necessário (valor real: X) aqui, pois a cor e a faixa refletem o conjunto de dados
                    else:
                        # Usar a faixa do config para o tooltip
                        tooltip_parts.append(tr("gradient_tooltip_range", min=tooltip_config_min_ivl_for_gradient_tooltip, max=tooltip_config_max_ivl_for_gradient_tooltip))
                        # Se o valor real do cartão estiver fora da faixa de config (e não estamos normalizando dinamicamente),
                        # adicionar uma nota com o valor real.
                        if card.ivl < tooltip_config_min_ivl_for_gradient_tooltip or card.ivl > tooltip_config_max_ivl_for_gradient_tooltip:
                            tooltip_parts.append(tr("gradient_normalized_value", real=card.ivl))
                            
                elif current_gradient_field == "lapses":
                    tooltip_parts.append(tr("gradient_tooltip_value", value=card.lapses))
                    tooltip_parts.append(tr("gradient_tooltip_range", min=config.get("gradient_lapses_min"), max=config.get("gradient_lapses_max")))
                elif current_gradient_field == "due" and card.queue == 2:
                    # today = mw.col.sched.today # <--- REMOVIDO, usar today_val
                    days_until_due = max(0, card.due - today_val) # <--- USADO today_val
                    tooltip_parts.append(tr("gradient_tooltip_value", value=days_until_due))
                    tooltip_parts.append(tr("gradient_tooltip_range", min=config.get("gradient_due_min"), max=config.get("gradient_due_max")))
                    
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
    filter_info_footer_content = f'<p style="margin: 3px 0;"><b>{tr("showing")}:</b> {active_filter_description} ({tr("cards_shown_of_total", count_shown=card_count_displayed, count_total=total_cards_in_filter)})</p>'

    filter_info_footer_html = f'''
<div id="memorymosaic-filter-footer" style="text-align: center; margin-top: 0px; padding-top: 0px; font-size: 0.9em; max-width: {grid_max_width_px}px; margin-left: auto; margin-right: auto;">
    {filter_info_footer_content}
</div>
'''

    # Sumário de cores para o modo categórico
    color_summary_container_html = ""
    if current_view_mode == "categorical":
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
        
        # Adicionar legenda para o indicador de cartões devidos hoje
        if config.get("show_due_indicator"):
            due_dot_style = f"display: inline-block; width: 12px; height: 12px; background-color: {due_indicator_color}; border: 1px solid #888; margin-right: 5px; vertical-align: middle; border-radius: 50%;"
            color_summary_items_html_parts.append(f'<span style="display: inline-flex; align-items: center; white-space: nowrap;"><span style="{due_dot_style}"></span>{tr("card_status_due")}</span>')
        
        color_summary_items_html = ' ' .join(color_summary_items_html_parts) # Espaço entre itens

        color_summary_container_html = f'''
<div id="memorymosaic-color-summary-container" style="max-width: {grid_max_width_px}px; margin-left: auto; margin-right: auto; margin-bottom: 5px; padding: 8px 0; display: flex; align-items: center; justify-content: center; flex-wrap: wrap; gap: 10px 15px; font-size: 0.9em;">
    <p style="font-weight: bold; margin: 0; white-space: nowrap;">{tr("summary_title")}:</p>
    {color_summary_items_html}
</div>
'''
    # Para modo gradiente, mostrar a legenda do gradiente
    elif current_view_mode == "gradient":
        # Obtém os valores min/max para o campo atual
        min_val = 0
        max_val = 100
        gradient_field_label = ""
        
        # Determinar a ordem do gradiente PRIMEIRO, para usar no texto da legenda
        order_config_key_legend = f"gradient_{current_gradient_field}_order"
        default_order_legend = "asc"
        if current_gradient_field == "lapses": # Lapses: menor é melhor por padrão
            default_order_legend = "desc"
        field_order_legend = config.get(order_config_key_legend)
        # Agora field_order_legend pode ser usado para o texto e para as cores da barra

        field_order_for_legend_text = field_order_legend # Usar a ordem determinada para o texto
        
        if current_gradient_field == "factor":
            min_val = config.get("gradient_factor_min")
            max_val = config.get("gradient_factor_max")
            gradient_field_label = tr("gradient_field_factor")
        elif current_gradient_field == "ivl":
            gradient_field_label = tr("gradient_field_ivl")
            if normalize_ivl_active and actual_min_ivl_for_norm is not None and actual_max_ivl_for_norm is not None:
                min_val = actual_min_ivl_for_norm
                max_val = actual_max_ivl_for_norm
                gradient_field_label += f" {tr('legend_dynamic_scale')}" # Adiciona (escala dinâmica)
            else:
                min_val = config.get("gradient_ivl_min")
                max_val = config.get("gradient_ivl_max")
        elif current_gradient_field == "lapses":
            min_val = config.get("gradient_lapses_min")
            max_val = config.get("gradient_lapses_max")
            gradient_field_label = tr("gradient_field_lapses")
        elif current_gradient_field == "due":
            min_val = config.get("gradient_due_min")
            max_val = config.get("gradient_due_max")
            gradient_field_label = tr("gradient_field_due")

        # Adicionar indicador de "melhor" para a legenda
        if field_order_for_legend_text == "asc":
            gradient_field_label += f" {tr('legend_higher_is_better')}"
        elif field_order_for_legend_text == "desc":
            gradient_field_label += f" {tr('legend_lower_is_better')}"
            
        # Cores do gradiente para a legenda
        display_start_color = config.get("gradient_color_start")
        display_mid_color = config.get("gradient_color_mid")
        display_end_color = config.get("gradient_color_end")
        
        # field_order_legend já foi definido acima
        if field_order_legend == "desc":
            # Inverter as cores para a legenda se a ordem for descendente
            display_start_color, display_end_color = display_end_color, display_start_color
            # A cor do meio permanece a mesma, pois a inversão é entre start e end

        # Criar uma legenda de gradiente
        gradient_legend_html = f'''
<div style="max-width: {grid_max_width_px}px; margin-left: auto; margin-right: auto; margin-bottom: 5px; padding: 8px 0; display: flex; flex-direction: column; align-items: center; font-size: 0.9em;">
    <p style="font-weight: bold; margin: 0 0 5px 0;">{tr("summary_title")}: {gradient_field_label} ({min_val} - {max_val})</p>
    <div style="width: 80%; max-width: 400px; height: 20px; background: linear-gradient(to right, {display_start_color}, {display_mid_color}, {display_end_color}); border-radius: 3px; margin-bottom: 3px;"></div>
    <div style="display: flex; justify-content: space-between; width: 80%; max-width: 400px;">
        <span>{min_val}</span>
        <span>{(min_val + max_val) // 2}</span>
        <span>{max_val}</span>
    </div>
</div>
'''
        color_summary_container_html = gradient_legend_html
        
        # Adicionar legenda para o indicador de cartões devidos hoje no modo gradiente, se estiver ativado
        if config.get("show_due_indicator"):
            due_dot_style = f"display: inline-block; width: 12px; height: 12px; background-color: {due_indicator_color}; border: 1px solid #888; margin-right: 5px; vertical-align: middle; border-radius: 50%;"
            due_indicator_legend_html = f'''
<div style="text-align: center; margin-top: 0px; max-width: {grid_max_width_px}px; margin-left: auto; margin-right: auto; font-size: 0.9em;">
    <span style="display: inline-flex; align-items: center; white-space: nowrap;"><span style="{due_dot_style}"></span>{tr("card_status_due")}</span>
</div>
'''
            color_summary_container_html += due_indicator_legend_html

    grid_html_content = f'<div id="memorymosaic-grid-container" style="{grid_container_style}">{all_tiles_html}</div>'

    # Botões de Paginação
    pagination_buttons_html = ""
    if _session_current_display_limit != float('inf') and total_cards_in_filter > card_count_displayed:
        load_more_count = min(incremental_card_load_count, total_cards_in_filter - card_count_displayed)
        btn_show_more_text = tr("pagination_show_more", count=load_more_count)
        btn_show_all_text = tr("pagination_show_all", count=total_cards_in_filter)

        pagination_buttons_html = f'''
<div id="memorymosaic-pagination-controls" style="text-align: center; margin-top: 15px; margin-bottom: 10px;">
    <button onclick="onMemoryMosaicLoadMore()" style="padding: 8px 15px; margin-right: 10px; border-radius: 4px; border: 1px solid #ccc; background-color: #f0f0f0; cursor: pointer;">{btn_show_more_text}</button>
    <button onclick="onMemoryMosaicLoadAll()" style="padding: 8px 15px; border-radius: 4px; border: 1px solid #ccc; background-color: #f0f0f0; cursor: pointer;">{btn_show_all_text}</button>
</div>'''

    script_html = f"""
<script>
    // Garante que o cursor volte ao normal quando a grade for redesenhada
    document.body.style.cursor = 'default';

    let currentSortOrder = '{current_sort_order_key}'; // Injetado pelo Python
    let currentViewMode = '{current_view_mode}'; // Modo de visualização atual
    let currentGradientField = '{current_gradient_field}'; // Campo de gradiente atual

    function onMemoryMosaicTileClick(cid) {{
        pycmd("memorymosaic_open_card:" + cid);
    }}

    function onMemoryMosaicSortOrderChanged(newSortOrder) {{
        document.body.style.cursor = 'wait'; // Muda o cursor para ampulheta
        pycmd("memorymosaic_sort_change:" + newSortOrder);
    }}
    
    function onMemoryMosaicViewModeChanged(newViewMode) {{
        document.body.style.cursor = 'wait';
        
        const gradientFieldContainer = document.getElementById('memorymosaic-gradient-field-container');
        if (gradientFieldContainer) {{
            gradientFieldContainer.style.display = (newViewMode === 'gradient') ? 'block' : 'none';
        }}
        
        pycmd("memorymosaic_view_mode_change:" + newViewMode);
    }}
    
    function onMemoryMosaicGradientFieldChanged(newField) {{
        document.body.style.cursor = 'wait';
        pycmd("memorymosaic_gradient_field_change:" + newField);
    }}

    function onMemoryMosaicLoadMore() {{
        document.body.style.cursor = 'wait';
        pycmd("memorymosaic_load_more");
    }}

    function onMemoryMosaicLoadAll() {{
        document.body.style.cursor = 'wait';
        pycmd("memorymosaic_load_all");
    }}

    function setMemoryMosaicSortOrderDropdown(sortOrderToSet) {{
        const selectElement = document.getElementById('memorymosaic-sort-order');
        if (selectElement) {{
            selectElement.value = sortOrderToSet;
        }}
        currentSortOrder = sortOrderToSet;
    }}
    
    function setMemoryMosaicViewModeDropdown(viewModeToSet) {{
        const selectElement = document.getElementById('memorymosaic-view-mode');
        if (selectElement) {{
            selectElement.value = viewModeToSet;
        }}
        currentViewMode = viewModeToSet;
        
        const gradientFieldContainer = document.getElementById('memorymosaic-gradient-field-container');
        if (gradientFieldContainer) {{
            gradientFieldContainer.style.display = (viewModeToSet === 'gradient') ? 'block' : 'none';
        }}
    }}
    
    function setMemoryMosaicGradientFieldDropdown(fieldToSet) {{
        const selectElement = document.getElementById('memorymosaic-gradient-field');
        if (selectElement) {{
            selectElement.value = fieldToSet;
        }}
        currentGradientField = fieldToSet;
    }}

    // Inicializa os dropdowns com os valores corretos ao carregar a grade
    // Apenas se os elementos existirem (para o caso de não haver cartões e, portanto, não haver controles)
    (function() {{
        if (document.getElementById('memorymosaic-sort-order')) {{
            setMemoryMosaicSortOrderDropdown(currentSortOrder);
        }}
        if (document.getElementById('memorymosaic-view-mode')) {{
            setMemoryMosaicViewModeDropdown(currentViewMode);
        }}
        if (document.getElementById('memorymosaic-gradient-field')) {{
            setMemoryMosaicGradientFieldDropdown(currentGradientField);
        }}
    }})();
</script>
"""

    # Atualiza os detalhes do filtro da sessão para a próxima renderização
    _session_last_filter_details = current_filter_details

    return spacing_html + title_and_controls_html + color_summary_container_html + grid_html_content + pagination_buttons_html + filter_info_footer_html + script_html

def _is_collection_usable() -> bool:
    """Verifica se a coleção está em um estado utilizável."""
    if _is_syncing or _is_closing:
        return False
        
    if not mw or not hasattr(mw, 'col') or not mw.col:
        return False
        
    if not hasattr(mw.col, 'db') or not mw.col.db:
        return False
        
    if getattr(mw, '_closeEventHasRun', False):
        return False
        
    if getattr(mw, 'state', '') in ['closing', 'profileManager']:
        return False
        
    try:
        if not mw.col.db.scalar("SELECT 1"):
            return False
    except Exception:
        return False
        
    return True

def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Converte cor hexadecimal para RGB."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    """Converte cor RGB para hexadecimal."""
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

def _get_gradient_color(value: float, min_val: float, max_val: float, config: dict, invert_gradient: bool = False) -> str:
    """Calcula a cor do gradiente para um valor entre o mínimo e o máximo."""
    # Prevenir divisão por zero
    if min_val == max_val:
        return config.get("gradient_color_mid")
        
    # Normalizar o valor para [0, 1]
    normalized = max(0, min(1, (value - min_val) / (max_val - min_val)))
    
    if invert_gradient:
        normalized = 1.0 - normalized
    
    # Obter cores do gradiente do config
    start_color = config.get("gradient_color_start")  # Amarelo
    mid_color = config.get("gradient_color_mid")      # Verde
    end_color = config.get("gradient_color_end")      # Azul
    
    # Converter para RGB para interpolação
    start_rgb = _hex_to_rgb(start_color)
    mid_rgb = _hex_to_rgb(mid_color)
    end_rgb = _hex_to_rgb(end_color)
    
    # Interpolação baseada na posição normalizada
    if normalized <= 0.5:
        # Entre start e mid (0.0 a 0.5)
        normalized_adjusted = normalized * 2  # Ajusta para range 0-1
        r = int(start_rgb[0] + (mid_rgb[0] - start_rgb[0]) * normalized_adjusted)
        g = int(start_rgb[1] + (mid_rgb[1] - start_rgb[1]) * normalized_adjusted)
        b = int(start_rgb[2] + (mid_rgb[2] - start_rgb[2]) * normalized_adjusted)
    else:
        # Entre mid e end (0.5 a 1.0)
        normalized_adjusted = (normalized - 0.5) * 2  # Ajusta para range 0-1
        r = int(mid_rgb[0] + (end_rgb[0] - mid_rgb[0]) * normalized_adjusted)
        g = int(mid_rgb[1] + (end_rgb[1] - mid_rgb[1]) * normalized_adjusted)
        b = int(mid_rgb[2] + (end_rgb[2] - mid_rgb[2]) * normalized_adjusted)
    
    # Converter de volta para hex
    return _rgb_to_hex((r, g, b))

def _get_gradient_tile_color(card: Card | None, field: str, config: dict, today_for_due_calc: int, ivl_min_override: int | None = None, ivl_max_override: int | None = None) -> str:
    """Determina a cor do tile com base no gradiente do campo selecionado."""
    if not card:
        return config.get("color_default_bg")
        
    # Cartões suspensos/enterrados sempre têm a mesma cor
    if card.queue in [-1, -2, -3]:
        return config.get("color_suspended_buried")
        
    # Cartões novos devem usar a cor de 'novo' do config, mesmo no modo gradiente
    if card.type == 0:
        return config.get("color_new") # Cor para cartões novos
        
    # Obter o valor de acordo com o campo
    value = None
    min_val = 0
    max_val = 100  # Valores padrão
    
    if field == "factor":
        value = card.factor
        min_val = config.get("gradient_factor_min")
        max_val = config.get("gradient_factor_max")
    elif field == "ivl":
        value = card.ivl
        if ivl_min_override is not None and ivl_max_override is not None:
            min_val = ivl_min_override
            max_val = ivl_max_override
        else: # Fallback se overrides não forem passados (não deveria acontecer com a nova lógica)
            min_val = config.get("gradient_ivl_min")
            max_val = config.get("gradient_ivl_max")
    elif field == "lapses":
        value = card.lapses
        min_val = config.get("gradient_lapses_min")
        max_val = config.get("gradient_lapses_max")
    elif field == "due":
        # Calcular dias até o vencimento
        if card.queue == 2:  # Cartão em revisão
            days_until_due = card.due - today_for_due_calc
            value = max(0, days_until_due)  # Não negativo
            min_val = config.get("gradient_due_min")
            max_val = config.get("gradient_due_max")
        else:
            # Para cartões que não estão em revisão, usar verde médio
            return config.get("gradient_color_mid")
    else:
        # Campo não reconhecido, usar cor padrão
        return config.get("color_default_bg")
    
    if value is None:
        return config.get("color_default_bg")
        
    # Determinar se o gradiente deve ser invertido
    invert_gradient = False
    order_config_key = f"gradient_{field}_order"
    
    # Definir padrões de ordem para cada campo
    default_order = "asc"
    if field == "lapses": # Para lapsos, menor é melhor, então a ordem natural do gradiente invertido é desejada
        default_order = "desc"
    
    field_order = config.get(order_config_key)
    if field_order == "desc":
        invert_gradient = True
        
    # Calcular a cor do gradiente
    return _get_gradient_color(value, min_val, max_val, config, invert_gradient=invert_gradient)

def on_sync_will_start():
    """Handler para quando a sincronização vai começar."""
    global _is_syncing
    _is_syncing = True

def on_sync_did_finish():
    """Handler para quando a sincronização termina."""
    global _is_syncing
    _is_syncing = False
    
    if not _is_collection_usable():
        return
        
    # Pequeno delay para garantir que a coleção esteja estável
    try:
        mw.progress.single_shot(
            1000,  # Aumentado para 1 segundo para dar mais tempo após sincronização
            lambda: request_refresh_if_memorymosaic_visible() if _is_collection_usable() else None
        )
    except Exception:
        pass

def on_profile_will_close():
    """Handler para quando o perfil vai ser fechado."""
    global _is_closing
    _is_closing = True

def on_collection_will_temporarily_close():
    """Handler para quando a coleção vai ser temporariamente fechada."""
    global _is_closing
    _is_closing = True

def request_refresh_if_memorymosaic_visible() -> None:
    """Força o refresh do Deck Browser ou Overview se o Memory Mosaic estiver visível."""
    if not _is_collection_usable():
        return

    if not hasattr(mw, 'state') or mw.state not in ["deckBrowser", "overview"]:
        return

    if mw.state == "deckBrowser":
        if hasattr(mw, 'deckBrowser') and mw.deckBrowser:
            try:
                mw.deckBrowser.refresh()
            except Exception:
                pass
    elif mw.state == "overview":
        if hasattr(mw, 'overview') and mw.overview:
            try:
                mw.overview.refresh()
            except Exception:
                pass

def on_overview_will_render_content(overview_obj: Overview, content_obj: OverviewContent) -> None:
    """Adiciona o container do Memory Mosaic ao conteúdo da visão geral do deck."""
    # Verificação de segurança
    if not mw or not mw.col or mw.state == "closing" or mw.state == "profileManager":
        return
        
    current_deck_name: str | None = None
    current_deck_id: int | None = None

    try:
        if not overview_obj or not content_obj:
            return
            
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
    # Verificação de segurança
    if not mw or not mw.col or mw.state == "closing" or mw.state == "profileManager":
        return
        
    if not deck_browser_obj or not content_obj:
        return
        
    try:
        grid_html = _render_memorymosaic_grid_html()
        content_obj.stats += grid_html
    except Exception as e:
        print(f"Memory Mosaic: Erro ao renderizar grid no deck browser: {e}")

# Atualiza os hooks com as novas funções
overview_will_render_content.append(on_overview_will_render_content)
deck_browser_will_render_content.append(on_deck_browser_will_render_content)

def on_config_changed_refresh_memorymosaic(addon_name: str, key: str, new_value: Any):
    """Handler para mudanças de configuração."""
    # O hook config_did_change_hook passa o nome do addon, não o objeto do addon.
    if addon_name == __name__: 
        global _memorymosaic_cached_config
        _memorymosaic_cached_config = None # Invalida o cache
        
        # Verifica se é seguro atualizar a interface
        if not mw or not mw.col or mw.state == "closing" or mw.state == "profileManager":
            return
            
        print(f"Memory Mosaic: Configuração alterada ('{key}'), cache invalidado e visualização será atualizada.")
        request_refresh_if_memorymosaic_visible()

# Registra os novos hooks
sync_will_start.append(on_sync_will_start)
sync_did_finish.append(on_sync_did_finish)
profile_will_close.append(on_profile_will_close)
collection_will_temporarily_close.append(on_collection_will_temporarily_close)

# Após a configuração ser salva (via editor JSON padrão do Anki), 
# precisamos atualizar a visualização se estiver visível.
if mw and hasattr(mw, "addonManager") and hasattr(mw.addonManager, "config_did_change_hook"): 
    mw.addonManager.config_did_change_hook.append(on_config_changed_refresh_memorymosaic)
elif mw and hasattr(mw, "config") and hasattr(mw.config, "config_did_change_hook"): 
    mw.config.config_did_change_hook.append(on_config_changed_refresh_memorymosaic)

def handle_memorymosaic_pycmd(handled: tuple[bool, Any], message: str, context: Any) -> tuple[bool, Any]:
    """Manipula comandos pycmd específicos do Memory Mosaic enviados da webview."""
    # Declarações globais no início da função para todas as globais modificadas aqui
    global _session_sort_order_override
    global _session_view_mode_override
    global _session_gradient_field_override
    global _session_current_display_limit
    # _session_last_filter_details é modificado em _render_memorymosaic_grid_html, não aqui diretamente,
    # então não precisa de global aqui, mas não faria mal se estivesse.

    if not _is_collection_usable():
        return handled

    if handled[0]: 
        return handled

    if message.startswith("memorymosaic_open_card:"):
        try:
            cid_str = message.split(":")[1]
            cid = int(cid_str)
            _open_card_in_browser(cid)
            return (True, None) 
        except Exception:
            return (True, None) 
    elif message.startswith("memorymosaic_sort_change:"):
        try:
            if not _is_collection_usable():
                return (True, None)
                
            new_sort_order = message.split(":")[1]
            valid_sort_orders = ["id_asc", "ivl_asc", "ivl_desc", "due_asc"]
            if new_sort_order in valid_sort_orders:
                _session_sort_order_override = new_sort_order
                try:
                    mw.progress.single_shot(
                        100,
                        lambda: request_refresh_if_memorymosaic_visible() if _is_collection_usable() else None
                    )
                except Exception:
                    pass
            return (True, None)
        except Exception:
            return (True, None)
    elif message.startswith("memorymosaic_view_mode_change:"):
        try:
            if not _is_collection_usable():
                return (True, None)
                
            new_view_mode = message.split(":")[1]
            valid_view_modes = ["categorical", "gradient"]
            if new_view_mode in valid_view_modes:
                _session_view_mode_override = new_view_mode
                try:
                    mw.progress.single_shot(
                        100,
                        lambda: request_refresh_if_memorymosaic_visible() if _is_collection_usable() else None
                    )
                except Exception:
                    pass
            return (True, None)
        except Exception:
            return (True, None)
    elif message.startswith("memorymosaic_gradient_field_change:"):
        try:
            if not _is_collection_usable():
                return (True, None)
                
            new_gradient_field = message.split(":")[1]
            valid_gradient_fields = ["factor", "ivl", "lapses", "due"]
            if new_gradient_field in valid_gradient_fields:
                _session_gradient_field_override = new_gradient_field
                try:
                    mw.progress.single_shot(
                        100,
                        lambda: request_refresh_if_memorymosaic_visible() if _is_collection_usable() else None
                    )
                except Exception:
                    pass
            return (True, None)
        except Exception:
            return (True, None)
    elif message.startswith("memorymosaic_load_more"):
        try:
            if not _is_collection_usable():
                return (True, None)
            
            config = _get_addon_config() # Para pegar incremental_card_load_count
            incremental_load = config.get("incremental_card_load_count")
            
            if _session_current_display_limit is None: # Caso inicial, embora já deva ser setado em render
                _session_current_display_limit = config.get("initial_card_load_count")
            elif _session_current_display_limit != float('inf'):
                _session_current_display_limit += incremental_load
            
            mw.progress.single_shot(100, lambda: request_refresh_if_memorymosaic_visible() if _is_collection_usable() else None)
            return (True, None)
        except Exception as e:
            print(f"MemoryMosaic error in load_more: {e}")
            return (True, None)
    elif message.startswith("memorymosaic_load_all"):
        try:
            if not _is_collection_usable():
                return (True, None)
            
            _session_current_display_limit = float('inf') # Sinaliza para carregar todos
            
            mw.progress.single_shot(100, lambda: request_refresh_if_memorymosaic_visible() if _is_collection_usable() else None)
            return (True, None)
        except Exception as e:
            print(f"MemoryMosaic error in load_all: {e}")
            return (True, None)
    
    return (False, None)

from aqt import gui_hooks
gui_hooks.webview_did_receive_js_message.append(handle_memorymosaic_pycmd)

# O código anterior de add_memorymosaic_placeholder_widget e seu hook main_window_did_init foi removido.
# Se houvesse outro código além do placeholder da status bar, ele permaneceria.
# Neste caso, o arquivo __init__.py só tinha isso. 