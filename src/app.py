import pandas as pd
import blackjack_func as bj
from dash import Dash, dcc, html, Input, Output, State, ctx, dash_table
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dbc_table_style import dbc_table_style
import plotly.express as px

# TODO add multiple hands at the table
# TODO add card counting
# TODO create realistic options for number of decks in play

deck = pd.read_csv('card_deck.csv', index_col=None)
card_deck_images = bj.create_card_deck_dict()
card_down_image_src = next((card['image'] for card in card_deck_images if card['card'] == 'back'), None)
# test_cards = ['4', '5']
# deck = deck[deck['rank'].isin(test_cards)]

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css])
server = app.server

app.layout = html.Div(className='dbc', children=[
    dbc.Container(children=[
        dbc.Row([
            dbc.Col(
                html.Div(children=[
                    html.H1('Dealer'),
                    html.Img(src=card_down_image_src, id='dealer-down-img', width='200px'),
                    html.Img(src=card_down_image_src, id='dealer-up-img', width='200px')
                ]),
                width=6
            ),
            dbc.Col(
                html.Div(children=[
                    html.H1('Stats'),
                    dbc.Alert(
                        [
                            html.H2('Coming Soon'),
                            html.Hr(),
                            html.Br(),
                            html.P('This section will keep track of your results and show you where '
                                   'you need to improve.'),
                            html.Div(id='player-stats-table-local'),
                            html.Button('Clear Data', id='clear-local-data-button', n_clicks=0)
                        ],
                        color='warning'
                    )
                ]),
                width=6
            )
        ]),
        dbc.Row([
            dbc.Col(
                html.Div(children=[
                    html.H1('Player'),
                    html.Img(src=card_down_image_src, id='player-card-1-img', width='200px'),
                    html.Img(src=card_down_image_src, id='player-card-2-img', width='200px')
                ]),
                width=6
            ),
            dbc.Col(
                html.Div(children=[
                    html.H1('Action'),
                    dbc.ButtonGroup(
                        [
                            dbc.Button('Hit', color='success', disabled=True, id='hit-button', n_clicks=0),
                            dbc.Button('Stand', color='danger', disabled=True, id='stand-button', n_clicks=0),
                            dbc.Button('Double', color='warning', disabled=True, id='double-button', n_clicks=0),
                            dbc.Button('Split', color='info', disabled=True, id='split-button', n_clicks=0)
                        ]
                    ),
                    html.Div(id='decision-result-alert'),
                    # html.Div(id='loading-spinner'),
                    dbc.Button('Deal', id='deal-cards', n_clicks=0),
                    html.Div(children=[
                        html.Div(id='dealer-down-card', style={'display': 'none'}),
                        html.Div(id='dealer-up-card', style={'display': 'none'}),
                        html.Div(id='player-card-1-card', style={'display': 'none'}),
                        html.Div(id='player-card-2-card', style={'display': 'none'}),
                        html.Div(id='correct-move', style={'display': 'none'}),
                        dcc.Store(id='current-turn-data', storage_type='memory', data=[]),
                        dcc.Store(id='player-stats-data-local', storage_type='local', data=[]),
                        dcc.Store(id='player-stats-data-session', storage_type='session', data=[])
                    ])
                ]),
                width=6
            )
        ])
    ])
])


@app.callback(
    [
        Output('dealer-down-card', 'children'),
        Output('dealer-up-card', 'children'),
        Output('player-card-1-card', 'children'),
        Output('player-card-2-card', 'children'),
        Output('dealer-down-img', 'src'),
        Output('dealer-up-img', 'src'),
        Output('player-card-1-img', 'src'),
        Output('player-card-2-img', 'src'),
        Output('hit-button', 'disabled'),
        Output('stand-button', 'disabled'),
        Output('double-button', 'disabled'),
        Output('split-button', 'disabled'),
        Output('decision-result-alert', 'children'),
        Output('hit-button', 'n_clicks'),
        Output('stand-button', 'n_clicks'),
        Output('double-button', 'n_clicks'),
        Output('split-button', 'n_clicks'),
        Output('correct-move', 'children'),
        Output('player-stats-data-session', 'data'),
        Output('current-turn-data', 'data')
    ],
    [
        Input('clear-local-data-button', 'n_clicks'),
        Input('deal-cards', 'n_clicks'),
        Input('hit-button', 'n_clicks'),
        Input('stand-button', 'n_clicks'),
        Input('double-button', 'n_clicks'),
        Input('split-button', 'n_clicks')
    ],
    [
        State('dealer-down-card', 'children'),
        State('dealer-up-card', 'children'),
        State('player-card-1-card', 'children'),
        State('player-card-2-card', 'children'),
        State('correct-move', 'children'),
        State('player-stats-data-session', 'data')
    ],
    prevent_initial_call=True
)
def deal_trigger(clear_n, deal_n, hit_click, stand_click, double_click, split_click,
                 dealer_down_card, dealer_up_card, player_card_1_card, player_card_2_card, correct_move,
                 player_stats_session):
    triggered_id = ctx.triggered_id
    print(f'Trigger ID: {triggered_id}')
    if triggered_id == 'deal-cards':
        deal_output = deal_cards(deal_n, player_stats_session)
        output_dealer_down = deal_output[0]
        output_dealer_up = deal_output[1]
        output_player_card_1 = deal_output[2]
        output_player_card_2 = deal_output[3]
        output_correct_move = deal_output[17]
        if output_correct_move == 'Blackjack!':
            return blackjack_winner(output_dealer_down, output_dealer_up, output_player_card_1, output_player_card_2,
                                    output_correct_move, player_stats_session)
        else:
            return deal_output
    elif triggered_id in ['hit-button', 'stand-button', 'double-button', 'split-button']:
        return player_action(hit_click, stand_click, double_click, split_click,
                             dealer_down_card, dealer_up_card, player_card_1_card, player_card_2_card, correct_move,
                             player_stats_session)
    elif triggered_id == 'clear-local-data-button':
        if clear_n:
            return '', '', '', '', '', '', '', '', True, True, True, True, '', 0, 0, 0, 0, None, [], []


def deal_cards(n, player_stats_session):
    if n is None:
        dealer_up_img = dealer_down_img = player_card_1_img = player_card_2_img = card_down_image_src
        hit_show = stand_show = double_show = split_show = True
        decision_result = dbc.Alert('       ', color='primary')
        hit_click = stand_click = double_click = split_click = 0
        correct_move = None
        current_turn_data = []
        return (dealer_down_img, dealer_up_img, player_card_1_img, player_card_2_img,
                hit_show, stand_show, double_show, split_show, decision_result,
                hit_click, stand_click, double_click, split_click, correct_move,
                player_stats_session, current_turn_data)
    hit_click = stand_click = double_click = split_click = 0
    decision_result = dbc.Alert('       ', color='primary')
    hit_show = stand_show = double_show = False
    dealer_up_card = bj.deal_card(deck)
    dealer_down_card = bj.deal_card(deck)
    player_card_1_card = bj.deal_card(deck)
    player_card_2_card = bj.deal_card(deck)
    player_hand = [player_card_1_card, player_card_2_card]
    current_turn_data = []

    dealer_down_img = next((card['image'] for card in card_deck_images if card['card'] == 'back'), None)
    dealer_up_img = next((card['image'] for card in card_deck_images if card['card'] == dealer_up_card), None)
    player_card_1_img = next((card['image'] for card in card_deck_images if card['card'] == player_card_1_card), None)
    player_card_2_img = next((card['image'] for card in card_deck_images if card['card'] == player_card_2_card), None)

    hand_type = bj.player_hand_type(player_hand, deck)
    if hand_type == 'pair':
        split_show = False
    else:
        split_show = True

    correct_move = bj.player_correct_move(player_hand, dealer_up_card, deck)

    print(f'Dealers Hand: {dealer_down_card}, {dealer_up_card}')
    print(f'Players Hand: {player_card_1_card}, {player_card_2_card}')
    print(f'Session Turns: {len(player_stats_session)}')

    return (dealer_down_card, dealer_up_card, player_card_1_card, player_card_2_card,
            dealer_down_img, dealer_up_img, player_card_1_img, player_card_2_img,
            hit_show, stand_show, double_show, split_show, decision_result,
            hit_click, stand_click, double_click, split_click, correct_move,
            player_stats_session, current_turn_data)


def player_action(hit_click, stand_click, double_click, split_click,
                  dealer_down_card, dealer_up_card, player_card_1_card, player_card_2_card, correct_move,
                  player_stats_session):
    print(f'Correct Move: {correct_move}')
    dealer_down_img = next((card['image'] for card in card_deck_images if card['card'] == 'back'), None)
    dealer_up_img = next((card['image'] for card in card_deck_images if card['card'] == 'back'), None)
    player_card_1_img = next((card['image'] for card in card_deck_images if card['card'] == 'back'), None)
    player_card_2_img = next((card['image'] for card in card_deck_images if card['card'] == 'back'), None)
    selected_move_dict = {}
    player_hand = [player_card_1_card, player_card_2_card]
    correct_move = bj.player_correct_move(player_hand, dealer_up_card, deck)
    player_card_chart = None
    if not hit_click and not stand_click and not double_click and not split_click:
        dealer_up_img = dealer_down_img = player_card_1_img = player_card_2_img = card_down_image_src
        decision_result = dbc.Alert('       ', color='primary')
        result = None
    else:
        if correct_move == 'Hit' and not hit_click:
            decision_result = dbc.Alert(f'Wrong. Correct Move: {correct_move}', color='danger')
            result = 0
        elif correct_move == 'Stand' and not stand_click:
            decision_result = dbc.Alert(f'Wrong. Correct Move: {correct_move}', color='danger')
            result = 0
        elif correct_move == 'Double' and not double_click:
            decision_result = dbc.Alert(f'Wrong. Correct Move: {correct_move}', color='danger')
            result = 0
        elif correct_move == 'Split' and not split_click:
            decision_result = dbc.Alert(f'Wrong. Correct Move: {correct_move}', color='danger')
            result = 0
        else:
            decision_result = dbc.Alert('Correct!', color='success')
            result = 1
    selected_move_dict = {'H': hit_click, 'S': stand_click, 'D': double_click, 'P': split_click}
    selected_move = max(selected_move_dict, key=lambda key: selected_move_dict[key])
    hand_type = bj.player_hand_type(player_hand, deck)
    if hand_type == 'hard':
        player_card_chart = bj.start_hand_value(player_hand, deck)
    elif hand_type == 'ace':
        if player_card_1_card.startswith('A'):
            player_card_chart = bj.show_card_rank(player_card_2_card)
        else:
            player_card_chart = bj.show_card_rank(player_card_1_card)
    elif hand_type == 'pair':
        player_card_chart = bj.show_card_rank(player_card_1_card)
    dealer_card_chart = bj.card_rank_wo_face(dealer_up_card, deck)
    current_turn_data = [{'hand_type': hand_type, 'player_card': player_card_chart, 'dealer_up': dealer_card_chart,
                          'selected_move': selected_move, 'correct_move': correct_move, 'result': result}]
    player_stats_session.extend(current_turn_data)
    hit_click = stand_click = double_click = split_click = 0
    hit_show = stand_show = double_show = split_show = True
    return (dealer_down_card, dealer_up_card, player_card_1_card, player_card_2_card,
            dealer_down_img, dealer_up_img, player_card_1_img, player_card_2_img,
            hit_show, stand_show, double_show, split_show, decision_result,
            hit_click, stand_click, double_click, split_click, correct_move,
            player_stats_session, current_turn_data)


def blackjack_winner(dealer_down_card, dealer_up_card, player_card_1_card, player_card_2_card, correct_move,
                     player_stats_session):
    print(f'Dealers Hand: {dealer_down_card}, {dealer_up_card}')
    print(f'Players Hand: {player_card_1_card}, {player_card_2_card}')
    print(f'Correct Move: {correct_move}')
    dealer_down_img = next((card['image'] for card in card_deck_images if card['card'] == 'back'), None)
    dealer_up_img = next((card['image'] for card in card_deck_images if card['card'] == dealer_up_card), None)
    player_card_1_img = next((card['image'] for card in card_deck_images if card['card'] == player_card_1_card), None)
    player_card_2_img = next((card['image'] for card in card_deck_images if card['card'] == player_card_2_card), None)
    hit_show = stand_show = double_show = split_show = True
    hit_click = stand_click = double_click = split_click = 0
    decision_result = dbc.Alert('Blackjack!', color='success')
    current_turn_data = []
    return (dealer_down_card, dealer_up_card, player_card_1_card, player_card_2_card,
            dealer_down_img, dealer_up_img, player_card_1_img, player_card_2_img,
            hit_show, stand_show, double_show, split_show, decision_result,
            hit_click, stand_click, double_click, split_click, correct_move,
            player_stats_session, current_turn_data)


@app.callback(
    [
        Output('player-stats-data-local', 'data'),
        Output('player-stats-table-local', 'children')
    ],
    [
        Input('deal-cards', 'n_clicks'),
        Input('clear-local-data-button', 'n_clicks')
    ],
    [
        State('current-turn-data', 'data'),
        State('player-stats-data-local', 'data')
    ],
    prevent_initial_call=True
)
def data_context_func(deal_n, clear_n, current_turn_data, local_data):
    triggered_id = ctx.triggered_id
    if deal_n <= 1:
        current_turn_data = None
        return local_data, current_turn_data
    if triggered_id == 'deal-cards':
        print(f'Data Context Trigger: {triggered_id}')
        return update_local_data(current_turn_data, local_data)
    elif triggered_id == 'clear-local-data-button':
        print(f'Data Context Trigger: {triggered_id}')
        return clear_local_data(clear_n, current_turn_data, local_data)


def update_local_data(current_turn_data, local_data):
    local_data.extend(current_turn_data)
    if len(local_data) <= 1:
        player_stats_table = []
    else:
        player_stats_df = pd.DataFrame(local_data)
        player_stats_table = dash_table.DataTable(
            columns=[{'name': col, 'id': col} for col in player_stats_df.columns],
            data=player_stats_df.to_dict('records'),
            page_size=5,
            **dbc_table_style
        )
    return local_data, player_stats_table


def clear_local_data(clear_n, current_turn_data, local_data):
    if clear_n:
        current_turn_data = []
        local_data = []
        print('All historical data has been cleared.')
        return current_turn_data, local_data
    else:
        raise PreventUpdate


if __name__ == '__main__':
    app.run_server(debug=True)
    # app.run_server(debug=True, port=8050)
