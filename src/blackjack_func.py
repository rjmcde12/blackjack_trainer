# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     notebook_metadata_filter: kernel spec
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

import pandas as pd
import os
from PIL import Image

hard_total = pd.read_csv('hard_total.csv', index_col='hand')
with_ace = pd.read_csv('with_ace.csv', index_col='hand')
with_pairs = pd.read_csv('with_pairs.csv', index_col='hand')

# +
def deal_card(deck):
    dealt_card = deck.sample(n=1)['card'].iloc[0]
    return dealt_card


def deal_player_hand_cms(deck):
    card_1 = deal_card(deck)
    card_2 = deal_card(deck)
    player_hand = [card_1, card_2]
    return player_hand


def show_card_rank(card):
    card_rank = card[:-1]
    return card_rank


def card_rank_wo_face(card, deck):
    if card.startswith('A'):
        dealer_rank = 'A'
    else:
        row = deck[deck['card'] == card]
        dealer_rank = row['value'].iloc[0]
    return dealer_rank


def show_card_value(card, deck):
    if not card.startswith('A'):
        row = deck[deck['card'] == card]
        card_value = int(row['value'].iloc[0])
    else:
        card_value = [11, 1]
    return card_value


def start_hand_value(hand, deck):
    card_1 = hand[0]
    card_2 = hand[1]
    value_1 = show_card_value(card_1, deck)
    value_2 = show_card_value(card_2, deck)
    hand_value = 0
    if isinstance(value_1, int) and isinstance(value_2, int):
        hand_value = (value_1 + value_2)
    elif isinstance(value_1, list) and isinstance(value_2, list):
        hand_value = 12
    elif isinstance(value_1, list):
        hand_value = [(value_2 + value_1[0]), (value_2 + value_1[1])]
    elif isinstance(value_2, list):
        hand_value = [(value_1 + value_2[0]), (value_1 + value_2[1])]
    return hand_value


def player_hand_type(hand, deck):
    card_1 = hand[0]
    card_2 = hand[1]
    row_1 = deck[deck['card'] == card_1]
    row_2 = deck[deck['card'] == card_2]
    if row_1['rank'].iloc[0]:
        card_1 = row_1['rank'].iloc[0]
    else:
        card_1 = 'J1'
    if row_2['rank'].iloc[0]:
        card_2 = row_2['rank'].iloc[0]
    else:
        card_1 = 'J2'
    if card_1 == card_2:
        hand_type = 'pair'
    elif card_1 == 'A' or card_2 == 'A':
        hand_type = 'ace'
    else:
        hand_type = 'hard'
    return hand_type


def player_split(hand, dealer_up, deck):
    hand_type = player_hand_type(hand, deck)
    dealer_rank = card_rank_wo_face(dealer_up, deck)
    player_is_split = False
    if hand_type == 'pair':
        pair_rank = card_rank_wo_face(hand[0], deck)
        row = with_pairs[with_pairs.index == pair_rank]
        is_split = row.loc[str(pair_rank), str(dealer_rank)]
        if is_split == 'Y':
            player_is_split = True
        else:
            player_is_split = False
    return player_is_split


def player_correct_move(hand, dealer_up, deck):
    hand_type = player_hand_type(hand, deck)
    hand_value = start_hand_value(hand, deck)
    dealer_rank = card_rank_wo_face(dealer_up, deck)
    correct_move = ''
    if hand_type is None:
        return correct_move
    if hand_type == 'pair':
        is_split = player_split(hand, dealer_up, deck)
        if is_split:
            correct_move = 'P'
        else:
            hand_type = 'hard'
    if hand_type == 'hard':
        if hand_value > 17:
            correct_move = 'S'
        elif hand_value < 4:
            correct_move = 'H'
        else:
            row = hard_total[hard_total.index == hand_value]
            correct_move = row.loc[hand_value, str(dealer_rank)]
    elif hand_type == 'ace':
        non_ace = min(hand_value[0], hand_value[1]) - 1
        if non_ace == 10:
            correct_move = 'BJ'
        else:
            row = with_ace[with_ace.index == non_ace]
            correct_move = row.loc[non_ace, str(dealer_rank)]
    action_full = {'H': 'Hit', 'S': 'Stand', 'P': 'Split', 'D': 'Double', 'BJ': 'Blackjack!'}
    correct_move = action_full.get(correct_move, '')
    return correct_move


def create_card_deck_dict():
    card_image_list = []
    for image_file in os.listdir('card_images'):
        if image_file.endswith('.png'):
            card = image_file[:-4]
            image = Image.open('card_images/' + image_file)
            card_image_dict = {'card': card, 'image': image}
            card_image_list.append(card_image_dict)
    card_image_list.append({'card': 'back', 'image': 'card_images/back.png'})
    return card_image_list


# -
if __name__ == "__main__":
    pass
