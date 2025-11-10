import numpy as np

def freq(sample: int, total: int ):
        if total != 0:
            return sample/total
        else:
            return 0.0
        
suits = {'c': '♣', 'd': '♦', 'h': '♥', 's': '♠',}
ranks = {2:'2', 3:'3', 4:'4', 5:'5', 6:'6', 7:'7', 8:'8', 9:'9', 10:'10', 11:'J', 12:'Q', 13:'K', 14:'A'}
streets = {0:'preflop', 1:'flop', 2:'turn', 3:'river'}

class Card:
    suits = {'c': '♣', 'd': '♦', 'h': '♥', 's': '♠',}
    ranks = {2:'2', 3:'3', 4:'4', 5:'5', 6:'6', 7:'7', 8:'8', 9:'9', 10:'10', 11:'J', 12:'Q', 13:'K', 14:'A'}
    def __init__(self, rank: int, suit: str):
        self.suit = suit
        self.rank = rank

    def get_rank(self):
        return self.rank
    
    def get_suit(self):
        return suits[self.suit]

    def __repr__(self):
        return f"{ranks[self.rank]}{suits[self.suit]}"


class HoleCards():
    
    def __init__(self, card1: Card, card2: Card):
        self.card1 = card1
        self.card2 = card2

        self.pair = (self.card1.get_rank() == self.card2.get_rank())
        self.suited = (self.card1.get_suit() == self.card2.get_suit()) and not self.pair
        self.connectors = (abs(self.card2.get_rank() - self.card1.get_rank() == 1) or {self.card2.get_rank(), self.card1.get_rank()} == {2,14})
        self.broadways = ((self.card1.get_rank() >= 10) and (self.card2.get_rank() >= 10)) and not self.pair

#getters
    def get_cards(self):
        return [self.card1,self.card2]

    def __repr__(self):
        return f"{str(self.card1)}{str(self.card2)}"


class PlayerStats:
    def __init__(self, name, cards: HoleCards = None):
        self.name = name
        self.total_hands = 0
        self.played_hands = []
        self.hands_pipped = 0
        self.VPIP = 0
        self.playRate = 0

        self.PreStats = StreetStats("preflop")
        self.FlopStats = StreetStats('flop')
        self.TurnStats = StreetStats('turn')
        self.RiverStats = StreetStats('river')

class StreetStats:
    def __init__(self, name): #generic bet class for each betting street
        self.name = name
        self.handsreachedstreet = 0
        self.bets = []
        self.raises = []
        self.threebets = []
        self.fourbetsplus = []

    def update(self, action: str = 'check', sizing: int = 0):
        if action == 'bet':
            self.bets.append(sizing)
        elif action == "raise":
            self.raises.append(sizing)
        elif action == "3bet":
            self.threebets.append(sizing)
        else:
            self.fourbetsplus.append(sizing)
    @property
    def avg_bet(self):
        if self.bets:
            return np.mean(self.bets)
        else:
            return 0.0
    @property
    def avg_raise(self):
        if self.raises:
            return np.mean(self.raises)
        else:
            return 0.0
    @property
    def avg_3bet(self):
        if self.threebets:
            return np.mean(self.threebets)
        else:
            return 0.0
    @property
    def avg_4betsplus(self):
        if self.fourbetsplus:
            return np.mean(self.fourbetsplus)
        else:
            return 0.0
    @property
    def bet_freq(self):
        return freq(len(self.bets), self.handsreachedstreet)
    @property
    def raise_freq(self):
        return freq(len(self.raises), self.handsreachedstreet)
    @property
    def three_bet_freq(self):
        return freq(len(self.threebets), self.handsreachedstreet)
    @property
    def four_bet_freq(self):
        return freq(len(self.fourbetsplus), self.handsreachedstreet)
    @property
    def passive_freq(self):
        if self.handsreachedstreet:
            return max(0, 1 - self.bet_freq - self.raise_freq)
        else:
            return 0.0
    
    def __repr__(self):
        return (f"{self.name.capitalize()} Stats → "
                f"BetFreq: {self.bet_freq:.2f}, RaiseFreq: {self.raise_freq:.2f}, "
                f"Passive: {self.passive_freq:.2f}")

if __name__ == "__main__":
    redaces = HoleCards(Card(14,"h"), Card(14,"d"))
    print(f"{redaces}")