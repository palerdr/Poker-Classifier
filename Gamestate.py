import numpy as np
import random
from typing import List
from pokerclasses import PlayerStats, HoleCards, Card, StreetStats
from bitarray import bitarray



suits = {'C': '♣', 'D': '♦', 'H': '♥', 'S': '♠',}
ranks = {2:'2', 3:'3', 4:'4', 5:'5', 6:'6', 7:'7', 8:'8', 9:'9', 10:'10', 11:'J', 12:'Q', 13:'K', 14:'A'}
streets = {0:'preflop', 1:'flop', 2:'turn', 3:'river'}

class Deck:
    def __init__(self):
        self._origdeck = [Card(rank, suit)
                          for rank in ranks.keys()
                          for suit in suits.keys()]
        self.reset()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, burn = False):
        if not self.cards:
            raise ValueError("Cannot draw from an empty deck")
        if burn:
            self.cards.pop()
            return
        return self.cards.pop()
    
    def reset(self):
        self.cards = self._origdeck.copy()
        self.shuffle()

    def remain(self):
        return len(self.cards)
    
    def __repr__(self):
        return f"Deck({self.remaining()} cards remaining)"
    
class Player:
    def __init__(self, name: str):
        self.name = name
        self.holecards = None
        self.hand = None
        self.current_bet = 0
        self.stacksize = 0
        self.in_hand = True
        self.stats = None

    def fold(self):
        self.in_hand = False
        self.cards = None
        self.hand = None

    def bet(self, amount: int):
        self.current_bet = amount
        self.stacksize -= amount

    def __repr__(self):
        return f"Player({self.name}, cards:{self.cards} stack={self.stacksize})"
    
class Game:
    streets = {0:'preflop', 1:'flop', 2:'turn', 3:'river'}
    def __init__(self, players: list[Player]):
        self.street = 0
        self.pot = 0
        self.players = players              
        self.order = players             
        self.in_hand = players
        self.community_cards = []
        self.deck = Deck()

    def board(self):
        return self.community_cards

    def preflop(self):
        for player in self.order:
            c1 = self.deck.deal()
            c2 = self.deck.deal()
            hcards = HoleCards(c1,c2)
            player.holecards = hcards
            player.hand = Hand(self, hcards.get_cards())
            
        
    def flop(self):
        self.deck.deal(burn = True)
        self.community_cards.extend([self.deck.deal() for _ in range(3)])
        self.street = 1
        print(f"{self.board()}")

    def turn(self):
        self.deck.deal(burn = True)
        self.community_cards.append(self.deck.deal())
        self.street = 2
        print(f"{self.board()}")

    def river(self):
        self.deck.deal(burn = True)
        self.community_cards.append(self.deck.deal())
        self.street = 3
        print(f"{self.board()}")
    
    def hand_over(self):
        self.street = 0
        self.community_cards.clear()
        for player in self.in_hand:
            player.fold()
        self.deck.reset()


class Hand:
    def __init__(self, g: Game, cards):
        self.hand = cards
        self.cards = cards
        self.game = g
        self.update_hand()

        self.ranks = bitarray(15)
        self.ranks.setall(0)
        self.freqs = bitarray(15*4)
        self.freqs.setall(0)
        self.suits = bitarray(15*4)
        self.suits.setall(0)
        self.freqs = bitarray(15*4)
        self.freqs.setall(0)

    def update_hand(self):
        self.cards = self.hand.extend(self.game.board())

    
    def fill_ranks(self):
        rti = {2: 12, 3: 11, 4: 10, 5: 9, 6: 8, 7: 7, 8: 6, 9: 5, 10: 4, 11: 3, 12: 2, 13: 1, 14: 0}
        for card in self.hand:
            r = card.rank
            i = rti[r]
            self.hand.ranks[i] = 1
            start = i*4
            for _ in range(start, start + 4):
                if hand.freqs[i] == 0:   # first available 0
                    hand.freqs[i] = 1
                    break
                

    
      

if __name__ == "__main__":
    J = Player("James")

    g = Game([J])

    g.preflop()
    print(J)


        
