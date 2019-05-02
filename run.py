from pprint import pprint
from decks.deck_normal import card_deck_struct
import random
from game.board import Board
from game.player import Player
from game.card import Card
from os import system, name

def clear(): 
    if name == 'nt': 
        _ = system('cls') 
    else:
        _ = system('clear') 

       


def phase1(board: Board, p: Player)->bool:
    """
    Фаза взятия карты и игры паники
    Возвращает необходимость продолжать код
    """
    cmd = None
    while cmd != None:
        cmd = input("Фаза 1. Берите карту [t] >>> ")
    card = p.pull_deck()
    clear()
    if not card.is_panic():
        p.take_on_hand(card)
        board.print_hands()
    else:
        p.play_panic(card)
        board.deck.append(card) # карта паники ушла в колоду
        return False
    return True

def phase2(board: Board, p: Player):
    """
    Фаза сброса или игры карты с руки
    """
    cmd = None
    while cmd not in ["p", "d"]:
        cmd = input("Фаза 2. Играйте или скинье карту [P]lay, [D]rop >>> ") 
    
    if cmd == "p":
        possible = p.get_possible_play()
    elif cmd == "d":
        possible = p.get_possible_drop()
    
    indices = []
    for i, c in enumerate(p.hand):
        if c.uuid not in possible:
            continue
        print(f"{i} {c.name}")
        indices.append(str(i))
    card_index = None
    while card_index not in indices:
        card_index = input(f"Какую карту? {indices} >>> ")

    card = p.hand.pop(int(card_index)) # выбранная карта
    if cmd == "p":
        p.play_card(card, target=None)
    p.drop_card(card) # в любом случае в колоду
    return

def phase3(board: Board, p: Player):
    print("Фаза 3. Обмен картами со следующим игроком")
    next_player = board.player_next()
    possible = p.get_possible_give(next_player)
    indices = []
    for i, c in enumerate(p.hand):
        if c.uuid not in possible:
            continue
        print(f"{i} {c.name}")
        indices.append(str(i))
    card_index = None
    while card_index not in indices:
        card_index = input(f"Какую карту даём ему? {indices} >>> ")
    my_card = p.hand.pop(int(card_index)) # выбранная карта      
    p.swap_cards(my_card, next_player)
    return


    
def main():
    random.seed(6)
    board = Board(4)
    try:
        while not board.is_end:
            board.next_turn()
            p = board.current_player()
            _ = input(">>> ")
            clear()
            print(f"ход {board.move}")
            board.print_hands()
            if not phase1(board, p):
                continue
            phase2(board, p)
            phase3(board, p)
    except KeyboardInterrupt:
        print("The end")

if __name__ == "__main__":
    main()













