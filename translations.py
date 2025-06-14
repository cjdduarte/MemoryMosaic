from aqt.qt import QLocale
from aqt import mw

def get_language():
    """Obtém o idioma atual do Anki ou do sistema."""
    try:
        lang = mw.pm.meta.get('defaultLang', 'en')
        if lang.startswith("pt"):
            return "pt_BR"
        return "en"
    except:
        # Fallback para o idioma do sistema
        lang = QLocale().name()
        if lang.startswith("pt"):
            return "pt_BR"
        return "en"

translations = {
    "pt_BR": {
        # Títulos e cabeçalhos
        "addon_title": "Memory Mosaic",
        "summary_title": "Sumário de Cartões",
        
        # Estatísticas de cartões
        "total_cards": "Total de cartões: {count}",
        "new_cards": "Novos: {count}",
        "mature_cards": "Maduros: {count}",
        "young_cards": "Jovens: {count}",
        "relearning_cards": "Reaprendendo: {count}",
        "suspended_cards": "Suspensos: {count}",
        
        # Filtro de deck
        "current_filter": "Filtro atual: {filter}",
        "all_decks": "Todos os cartões da coleção",
        "filter_subdecks": "incluindo subdecks",
        "showing": "Exibindo",
        
        # Tooltips
        "tooltip_card_id": "ID do Cartão: {cid}",
        "tooltip_deck": "Deck: {deck}",
        "tooltip_last_review": "Última Revisão: {date}",
        "tooltip_due": "Vencimento: {due}",
        "tooltip_queue": "Fila: {queue}",
        "tooltip_type": "Tipo: {type}",
        "tooltip_interval": "Intervalo: {interval} dias",
        "tooltip_never_reviewed": "Nunca revisado",
        "tooltip_factor": "Fator: {factor}",
        
        # Status dos cartões (para tooltips e sumário)
        "card_status_new": "Novos",
        "card_status_mature": "Maduros",
        "card_status_young": "Jovens/Aprend.",
        "card_status_relearning": "Reaprend./Lapso",
        "card_status_suspended": "Suspensos/Enterrados",
        "card_status_default": "Padrão/Erro",
        "card_status_due": "Vencido Hoje",
        "card_status_buried": "Enterrado",
        
        # Ordenação
        "sort_by_creation": "Criação",
        "sort_by_interval_asc": "Intervalo (Cresc.)",
        "sort_by_interval_desc": "Intervalo (Decresc.)",
        "sort_by_due_date": "Vencimento",
        
        # Visualização - Novos
        "view_mode": "Modo de Visualização",
        "view_categorical": "Estados dos Cartões",
        "view_gradient": "Gradiente",
        "gradient_field": "Campo para Gradiente",
        "gradient_field_factor": "Facilidade",
        "gradient_field_ivl": "Intervalo/Maturidade",
        "gradient_field_lapses": "Lapsos",
        "gradient_field_due": "Tempo até Vencimento",
        "gradient_tooltip_value": "Valor: {value}",
        "gradient_tooltip_range": "Faixa do Gradiente: {min} a {max}",
        "gradient_normalized_value": "Valor normalizado (real: {real})",
        "gradient_dynamic_scale": "Usando escala dinâmica (não normalizada)",
        "legend_higher_is_better": "(maior é melhor)",
        "legend_lower_is_better": "(menor é melhor)",
        "legend_dynamic_scale": "(escala dinâmica)",
        
        # Mensagens
        "loading_mosaic": "Carregando Memory Mosaic...",
        "no_cards": "Nenhum cartão encontrado para exibir.",
        "click_to_browser": "Clique para abrir no navegador",
        
        # Erros
        "error_loading": "Erro ao carregar Memory Mosaic: {error}",
        "error_config": "Erro nas configurações: {error}",

        # Paginação (Novo)
        "no_cards_in_initial_load": "Nenhum cartão para exibir na carga inicial (total no filtro: {count}). Clique em 'Mostrar Todos'.",
        "cards_shown_of_total": "{count_shown} de {count_total} cartões",
        "pagination_show_more": "Mostrar mais {count}",
        "pagination_show_all": "Mostrar Todos ({count})",
    },
    "en": {
        # Titles and headers
        "addon_title": "Memory Mosaic",
        "summary_title": "Card Summary",
        
        # Card statistics
        "total_cards": "Total cards: {count}",
        "new_cards": "New: {count}",
        "mature_cards": "Mature: {count}",
        "young_cards": "Young: {count}",
        "relearning_cards": "Relearning: {count}",
        "suspended_cards": "Suspended: {count}",
        
        # Deck filter
        "current_filter": "Current filter: {filter}",
        "all_decks": "All cards in collection",
        "filter_subdecks": "including subdecks",
        "showing": "Showing",
        
        # Tooltips
        "tooltip_card_id": "Card ID: {cid}",
        "tooltip_deck": "Deck: {deck}",
        "tooltip_last_review": "Last Review: {date}",
        "tooltip_due": "Due: {due}",
        "tooltip_queue": "Queue: {queue}",
        "tooltip_type": "Type: {type}",
        "tooltip_interval": "Interval: {interval} days",
        "tooltip_never_reviewed": "Never reviewed",
        "tooltip_factor": "Factor: {factor}",
        
        # Card statuses (for tooltips and summary)
        "card_status_new": "New",
        "card_status_mature": "Mature",
        "card_status_young": "Young/Learning",
        "card_status_relearning": "Relearning/Lapse",
        "card_status_suspended": "Suspended/Buried",
        "card_status_default": "Default/Error",
        "card_status_due": "Due Today",
        "card_status_buried": "Buried",
        
        # Sorting
        "sort_by_creation": "Creation",
        "sort_by_interval_asc": "Interval (Asc.)",
        "sort_by_interval_desc": "Interval (Desc.)",
        "sort_by_due_date": "Due Date",
        
        # Visualization - New
        "view_mode": "View Mode",
        "view_categorical": "Card States",
        "view_gradient": "Gradient",
        "gradient_field": "Gradient Field",
        "gradient_field_factor": "Ease Factor",
        "gradient_field_ivl": "Interval/Maturity",
        "gradient_field_lapses": "Lapses",
        "gradient_field_due": "Time Until Due",
        "gradient_tooltip_value": "Value: {value}",
        "gradient_tooltip_range": "Gradient Range: {min} to {max}",
        "gradient_normalized_value": "Normalized value (actual: {real})",
        "gradient_dynamic_scale": "Using dynamic scale (non-normalized)",
        "legend_higher_is_better": "(higher is better)",
        "legend_lower_is_better": "(lower is better)",
        "legend_dynamic_scale": "(dynamic scale)",
        
        # Messages
        "loading_mosaic": "Loading Memory Mosaic...",
        "no_cards": "No cards found to display.",
        "click_to_browser": "Click to open in browser",
        
        # Errors
        "error_loading": "Error loading Memory Mosaic: {error}",
        "error_config": "Configuration error: {error}",

        # Pagination (New)
        "no_cards_in_initial_load": "No cards to display in initial load (total in filter: {count}). Click 'Show All'.",
        "cards_shown_of_total": "{count_shown} of {count_total} cards",
        "pagination_show_more": "Show {count} more",
        "pagination_show_all": "Show All ({count})",
    }
}

def tr(key, **kwargs):
    """Traduz uma chave para o idioma atual com substituição de parâmetros opcional."""
    lang = get_language()
    text = translations.get(lang, translations["en"]).get(key, key)
    return text.format(**kwargs) if kwargs else text 