default_table_style = {
    'overflowX': 'auto',
    'border': '1px solid #dee2e6',
    'borderCollapse': 'collapse',
    'width': '100%',
    'marginBottom': '0'
}

default_header_style = {
    'backgroundColor': '#f8f9fa',
    'fontWeight': 'bold',
    'border': '1px solid #dee2e6',
    'textAlign': 'center'
}

default_cell_style = {
    'textAlign': 'left',
    'padding': '8px',
    'border': '1px solid #dee2e6'
}

default_conditional_style = [
    {
        'if': {'row_index': 'odd'},
        'backgroundColor': 'rgba(248, 248, 248, 0.8)'
    },
    {
        'if': {'row_index': 'even'},
        'backgroundColor': 'rgba(255, 255, 255, 0.8)'
    }
]

dbc_table_style = {
    'style_table': default_table_style,
    'style_header': default_header_style,
    'style_cell': default_cell_style,
    'style_data_conditional': default_conditional_style
}