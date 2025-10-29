import numpy as np
from pokerclasses import HoleCards, Card
from Gamestate import Hand, Player, Game
from bitarray import bitarray
from itertools import combinations



def evaluate_hand(hand: list[Card]):
    ranks = bitarray(15)
    ranks.setall(0)
    freqs = bitarray(15*4)
    freqs.setall(0)
    suits = [card.get_suit() for card in hand]
        
    #fills up the rank and freq bitstrings 
    for card in hand:
        i = 14 - card.rank
        ranks[i] = 1
        start = i*4
        for j  in range(start+3, start - 1, -1):
            if freqs[j] == 0:   # first available 0
                freqs[j] = 1
                break

    
       
    return 







if __name__ == "__main__":
    h = [Card(9,"c"),Card(9,"s"),Card(9,"h"),Card(9,"d"),Card(13,"h")]
    print(f"{evaluate_hand(h)}")