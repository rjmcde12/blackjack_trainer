import pandas as pd
import blackjack_func as bj
from dash import Dash, dcc, html, Input, Output, State, ctx, Patch, MATCH, ALLSMALLER, callback, dash_table
import dash_bootstrap_components as dbc
from dbc_table_style import dbc_table_style
import os
from PIL import Image
import plotly.express as px

# TODO add multiple hands at the table
# TODO add card counting
# TODO create realistic options for number of decks in play

deck = pd.read_csv('card_deck.csv', index_col=None)
card_deck_images = bj.create_card_deck_dict()
card_down_image_src = next((card['image'] for card in card_deck_images if card['card'] == 'back'), None)

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
                                   'you need to improve.')
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
                            dbc.Button('Hit', color='success', disabled=True, id='hit-action', n_clicks=0),
                            dbc.Button('Stand', color='danger', disabled=True, id='stand-action', n_clicks=0),
                            dbc.Button('Double', color='warning', disabled=True, id='double-action', n_clicks=0),
                            dbc.Button('Split', color='info', disabled=True, id='split-action', n_clicks=0)
                        ]
                    ),
                    html.Div(id='decision-result-alert'),
                    # html.H3('pending', id='decision-result'),
                    # html.Div(id='loading-spinner'),
                    dbc.Button('Deal', id='deal-cards', n_clicks=0),
                    # dbc.Button('Clear', id='clear-table', n_clicks=0),
                    html.Div(children=[
                        html.Div(id='dealer-down-card', style={'display': 'none'}),
                        html.Div(id='dealer-up-card', style={'display': 'none'}),
                        html.Div(id='player-card-1-card', style={'display': 'none'}),
                        html.Div(id='player-card-2-card', style={'display': 'none'}),
                        html.Div(id='correct-move', style={'display': 'none'}),
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
        Output('hit-action', 'disabled'),
        Output('stand-action', 'disabled'),
        Output('double-action', 'disabled'),
        Output('split-action', 'disabled'),
        Output('decision-result-alert', 'children'),
        Output('hit-action', 'n_clicks'),
        Output('stand-action', 'n_clicks'),
        Output('double-action', 'n_clicks'),
        Output('split-action', 'n_clicks'),
        Output('correct-move', 'children')
    ],
    [
        Input('deal-cards', 'n_clicks'),
        Input('hit-action', 'n_clicks'),
        Input('stand-action', 'n_clicks'),
        Input('double-action', 'n_clicks'),
        Input('split-action', 'n_clicks')
    ],
    [
        State('dealer-down-card', 'children'),
        State('dealer-up-card', 'children'),
        State('player-card-1-card', 'children'),
        State('player-card-2-card', 'children'),
        State('correct-move', 'children')
    ],
    prevent_initial_call=True
)
def deal_trigger(deal_n, hit_action, stand_action, double_action, split_action,
                 dealer_down_card, dealer_up_card, player_card_1_card, player_card_2_card, correct_move):
    triggered_id = ctx.triggered_id
    if triggered_id == 'deal-cards':
        print(f'Trigger ID: {triggered_id}')
        return deal_cards(deal_n)
    else:
        if correct_move == 'Blackjack!':
            return blackjack_winner(hit_action, stand_action, double_action, split_action,
                                    dealer_down_card, dealer_up_card, player_card_1_card, player_card_2_card,
                                    correct_move)
        else:
            print(f'Trigger ID: {triggered_id}')
            return player_action(hit_action, stand_action, double_action, split_action,
                                 dealer_down_card, dealer_up_card, player_card_1_card, player_card_2_card, correct_move)


def deal_cards(n):
    if n is None:
        dealer_up_img = dealer_down_img = player_card_1_img = player_card_2_img = card_down_image_src
        hit_action = stand_action = double_action = split_action = True
        decision_result = dbc.Alert('       ', color='primary')
        hit_click = stand_click = double_click = split_click = 0
        correct_move = None
        return (dealer_down_img, dealer_up_img, player_card_1_img, player_card_2_img,
                hit_action, stand_action, double_action, split_action, decision_result,
                hit_click, stand_click, double_click, split_click, correct_move)
    hit_click = stand_click = double_click = split_click = 0
    decision_result = dbc.Alert('       ', color='primary')
    hit_action = stand_action = double_action = False
    dealer_up_card = bj.deal_card(deck)
    dealer_down_card = bj.deal_card(deck)
    player_card_1_card = bj.deal_card(deck)
    player_card_2_card = bj.deal_card(deck)
    player_hand = [player_card_1_card, player_card_2_card]

    dealer_down_img = next((card['image'] for card in card_deck_images if card['card'] == 'back'), None)
    dealer_up_img = next((card['image'] for card in card_deck_images if card['card'] == dealer_up_card), None)
    player_card_1_img = next((card['image'] for card in card_deck_images if card['card'] == player_card_1_card), None)
    player_card_2_img = next((card['image'] for card in card_deck_images if card['card'] == player_card_2_card), None)

    hand_type = bj.player_hand_type(player_hand, deck)
    if hand_type == 'pair':
        split_action = False
    else:
        split_action = True

    correct_move = bj.player_correct_move(player_hand, dealer_up_card, deck)
    if correct_move == 'Blackjack!':
        player_action(hit_click, stand_click, double_click, split_click,
                      dealer_down_card, dealer_up_card, player_card_1_card, player_card_2_card, correct_move)
        return (dealer_down_card, dealer_up_card, player_card_1_card, player_card_2_card,
                dealer_down_img, dealer_up_img, player_card_1_img, player_card_2_img,
                hit_action, stand_action, double_action, split_action, decision_result,
                hit_click, stand_click, double_click, split_click, correct_move)

    print(f'Correct Move: {correct_move}')
    print(f'Dealers Hand: {dealer_down_card}, {dealer_up_card}')
    print(f'Players Hand: {player_card_1_card}, {player_card_2_card}')

    return (dealer_down_card, dealer_up_card, player_card_1_card, player_card_2_card,
            dealer_down_img, dealer_up_img, player_card_1_img, player_card_2_img,
            hit_action, stand_action, double_action, split_action, decision_result,
            hit_click, stand_click, double_click, split_click, correct_move)


def player_action(hit_click, stand_click, double_click, split_click,
                  dealer_down_card, dealer_up_card, player_card_1_card, player_card_2_card, correct_move):
    print(f'Dealers Hand: {dealer_down_card}, {dealer_up_card}')
    print(f'Players Hand: {player_card_1_card}, {player_card_2_card}')
    print(f'Correct Move: {correct_move}')
    dealer_down_img = next((card['image'] for card in card_deck_images if card['card'] == 'back'), None)
    dealer_up_img = next((card['image'] for card in card_deck_images if card['card'] == 'back'), None)
    player_card_1_img = next((card['image'] for card in card_deck_images if card['card'] == 'back'), None)
    player_card_2_img = next((card['image'] for card in card_deck_images if card['card'] == 'back'), None)
    decision_result = dbc.Alert('       ', color='primary')
    hit_action = stand_action = double_action = split_action = False
    if correct_move == 'Blackjack!':
        hit_click = stand_click = double_click = split_click = 0
        decision_result = dbc.Alert('Blackjack!', color='success')
        return (dealer_down_card, dealer_up_card, player_card_1_card, player_card_2_card,
                dealer_down_img, dealer_up_img, player_card_1_img, player_card_2_img,
                hit_action, stand_action, double_action, split_action, decision_result,
                hit_click, stand_click, double_click, split_click, correct_move)
    if player_card_2_card is not None:
        player_hand = [player_card_1_card, player_card_2_card]
        correct_move = bj.player_correct_move(player_hand, dealer_up_card, deck)
        if not hit_click and not stand_click and not double_click and not split_click:
            hit_action = stand_action = double_action = split_action = True
            dealer_up_img = dealer_down_img = player_card_1_img = player_card_2_img = card_down_image_src
            decision_result = dbc.Alert('       ', color='primary')
        else:
            if correct_move == 'H' and not hit_click:
                decision_result = dbc.Alert('Wrong.', color='danger')
            elif correct_move == 'S' and not stand_click:
                decision_result = dbc.Alert('Wrong.', color='danger')
            elif correct_move == 'D' and not double_click:
                decision_result = dbc.Alert('Wrong.', color='danger')
            elif correct_move == 'P' and not split_click:
                decision_result = dbc.Alert('Wrong.', color='danger')
            else:
                decision_result = dbc.Alert('Correct!', color='success')

    print(f'H: {str(hit_click)} S: {str(stand_click)} D: {str(double_click)} P: {str(split_click)}')
    hit_click = stand_click = double_click = split_click = 0
    hit_action = stand_action = double_action = split_action = True
    return (dealer_down_card, dealer_up_card, player_card_1_card, player_card_2_card,
            dealer_down_img, dealer_up_img, player_card_1_img, player_card_2_img,
            hit_action, stand_action, double_action, split_action, decision_result,
            hit_click, stand_click, double_click, split_click, correct_move)


def blackjack_winner(hit_click, stand_click, double_click, split_click,
                     dealer_down_card, dealer_up_card, player_card_1_card, player_card_2_card, correct_move):
    print(f'Dealers Hand: {dealer_down_card}, {dealer_up_card}')
    print(f'Players Hand: {player_card_1_card}, {player_card_2_card}')
    print(f'Correct Move: {correct_move}')
    dealer_down_img = next((card['image'] for card in card_deck_images if card['card'] == 'back'), None)
    dealer_up_img = next((card['image'] for card in card_deck_images if card['card'] == 'back'), None)
    player_card_1_img = next((card['image'] for card in card_deck_images if card['card'] == 'back'), None)
    player_card_2_img = next((card['image'] for card in card_deck_images if card['card'] == 'back'), None)
    hit_action = stand_action = double_action = split_action = True
    hit_click = stand_click = double_click = split_click = 0
    decision_result = dbc.Alert('Blackjack!', color='success')
    return (dealer_down_card, dealer_up_card, player_card_1_card, player_card_2_card,
            dealer_down_img, dealer_up_img, player_card_1_img, player_card_2_img,
            hit_action, stand_action, double_action, split_action, decision_result,
            hit_click, stand_click, double_click, split_click, correct_move)


if __name__ == '__main__':
     app.run_server(debug=True)
