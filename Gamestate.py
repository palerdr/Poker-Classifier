import numpy as np
import random
from typing import List
from pokerclasses import PlayerStats, HoleCards, Card, StreetStats
from bitarray import bitarray
from itertools import combinations
from Evaluator import evaluate_hand



suits = {'c': '♣', 'd': '♦', 'h': '♥', 's': '♠',}
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
    def __init__(self, name: str, stack: float):
        self.name = name
        self.holecards = None
        self.hand = None
        self.current_bet = 0.0
        self.stacksize = stack
        self.in_hand = True
        self.stats = None

    def fold(self):
        self.in_hand = False
        self.cards = None
        self.hand = None

    def bet(self, amount: int):
        self.current_bet = amount
        self.stacksize -= amount

    def get_best_hand(self):
        """Returns the player's best HandRank"""
        if self.hand:
            self.hand.update_hand()
            return self.hand.rank
        return None

    def __repr__(self):
        return f"Player({self.name}, cards:{self.cards} stack={self.stacksize})"
    
class Game:
    streets = {0:'preflop', 1:'flop', 2:'turn', 3:'river', 4:'showdown'}
    def __init__(self, players: list[Player]):
        self.street = 0
        self.pot = 0.0
        self.hands_played = 0
        self.players = players
        self.button = 0  # Index of button position
        self.community_cards = []
        self.deck = Deck()

    def board(self):
        return self.community_cards

    def get_active_players(self):
        """Returns list of players still in the hand"""
        return [p for p in self.players if p.in_hand]

    def get_order(self):
        """Returns betting order based on button position"""
        # Button is last to act, so order starts after button
        n = len(self.players)
        return [self.players[(self.button + 1 + i) % n] for i in range(n)]

    def preflop(self):
        for player in self.get_order():
            c1 = self.deck.deal()
            c2 = self.deck.deal()
            hcards = HoleCards(c1,c2)
            player.holecards = hcards
            player.hand = Hand(self, hcards.get_cards())
            player.in_hand = True  # Reset in_hand status for new hand
            
        
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

    def showdown(self):
        """Determines winner or winners and awards pot"""
        active_players = self.get_active_players()

        if len(active_players) == 1:
            # Only one player left - they win by default
            active_players[0].stacksize += self.pot
            print(f"{active_players[0].name} wins ${self.pot} (everyone else folded)")
        else:
            # Update all hands and find best
            for player in active_players:
                player.hand.update_hand()

            # Find the best hand(s)
            best_rank = None
            winners = []

            for player in active_players:
                player_rank = player.hand.rank  # This is the HandRank after update_hand()

                if best_rank is None or player_rank > best_rank:
                    best_rank = player_rank
                    winners = [player]
                elif player_rank == best_rank:
                    winners.append(player)

            # Award pot (split if tie)
            winnings = self.pot / len(winners)
            for winner in winners:
                winner.stacksize += winnings

            if len(winners) == 1:
                print(f"{winners[0].name} wins ${self.pot} with {best_rank.hand_type}")
            else:
                print(f"Pot split between {', '.join(w.name for w in winners)} with {best_rank.hand_type} (${winnings} each)")

        self.street = 4

    def hand_over(self):
        """Resets game state for next hand"""
        self.street = 0
        self.pot = 0
        self.hands_played += 1
        self.community_cards.clear()

        # Rotate button
        self.button = (self.button + 1) % len(self.players)

        # Reset all players
        for player in self.players:
            player.fold()

        self.deck.reset()


class Hand:
    def __init__(self, g: Game, holecards: List[Card]):
        self.holecards = holecards  # Store the original 2 hole cards
        self.all = holecards.copy()  # All 7 cards (starts with just hole cards)
        self.game = g
        self.rank = None  # Best HandRank 

    def update_hand(self):
        """Updates self.all with hole cards + community cards, then finds best hand"""
        self.all = self.holecards + self.game.board()
        self.rank = self.get_best_hand()

    def get_best_hand(self):
        """Finds best HandRank from all 5-card combinations"""
        if len(self.all) < 5:
            return None  # Not enough cards yet

        best = None
        for combo in combinations(self.all, 5):
            current_rank = evaluate_hand(list(combo))
            if best is None or current_rank > best:
                best = current_rank

        return best


    
    

                

    
      

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # Create players
    alice = Player("Alice", 1000)
    bob = Player("Bob", 1000)
    charlie = Player("Charlie", 1000)

    # Create game
    g = Game([alice, bob, charlie])

    print("=== Starting Hand ===")
    print(f"Button position: {g.button}")
    print()

    # Deal preflop
    g.preflop()
    print("Hole cards dealt:")
    for player in g.players:
        print(f"{player.name}: {player.holecards}")

    # Simulate some betting (each player antes $10)
    for player in g.players:
        player.bet(10)
        g.pot += 10
    print(f"Pot: ${g.pot}")
    print()

    # Deal flop
    g.flop()
    print("After flop:")
    for player in g.get_active_players():
        player.hand.update_hand()
        print(f"{player.name}: {player.hand.rank}")
    print()

    # Deal turn
    g.turn()
    print("After turn:")
    for player in g.get_active_players():
        player.hand.update_hand()
        print(f"{player.name}: {player.hand.rank}")
    print()

    # Deal river
    g.river()
    print("After river:")
    for player in g.get_active_players():
        player.hand.update_hand()
        print(f"{player.name}: {player.hand.rank}")
    print()

    # Showdown
    print("=== SHOWDOWN ===")
    g.showdown()
    print()
    print("Final stacks:")
    for player in g.players:
        print(f"{player.name}: ${player.stacksize}")


        
