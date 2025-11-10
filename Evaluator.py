import numpy as np
from pokerclasses import Card
from bitarray import bitarray
from itertools import combinations
from collections import defaultdict


class HandRank:
    HAND_RANKS = {
        "Royal Flush": 10,
        "Straight Flush": 9,
        "Quads": 8,
        "Full House": 7,
        "Flush": 6,
        "Straight": 5,
        "Three of A Kind": 4,
        "Two Pair": 3,
        "Pair": 2,
        "High Card": 1
    }

    def __init__(self, hand_type: str, value: int, ranks_value: int):
        self.hand_type = hand_type
        self.rank = self.HAND_RANKS[hand_type]
        self.value = value  # The freq bitstring value for tie-breaking
        self.ranks_value = ranks_value  # The ranks bitstring value

    def __lt__(self, other):
        if self.rank != other.rank:
            return self.rank < other.rank
        return self.value < other.value

    def __gt__(self, other):
        if self.rank != other.rank:
            return self.rank > other.rank
        return self.value > other.value

    def __eq__(self, other):
        return self.rank == other.rank and self.value == other.value

    def __repr__(self):
        return f"{self.hand_type} (rank={self.rank}, value={self.value})"


def evaluate_hand(hand: list[Card]) -> HandRank:
    """Evaluates a 5-card poker hand and returns its ranking"""
    if len(hand) != 5:
        raise ValueError(f"Hand must contain exactly 5 cards, got {len(hand)}")

    ranks = bitarray(15)
    ranks.setall(0)
    freqs = bitarray(15*4)
    freqs.setall(0)
    suits = [card.get_suit() for card in hand]

    # Count occurrences of each rank
    rank_counts = defaultdict(int)
    for card in hand:
        rank_counts[card.rank] += 1

    # fills up the rank and freq bitstrings (for hand type detection)
    for card in hand:
        i = 14 - card.rank
        ranks[i] = 1
        start = i*4
        for j in range(start+3, start - 1, -1):
            if freqs[j] == 0:
                freqs[j] = 1
                break

    value = int(freqs.to01(), 2)
    ranks_value = int(ranks.to01(), 2)
    hier = {"Royal Flush": False, "Straight Flush": False, "Quads": False,
            "Full House": False, "Flush": False, "Straight": False,
            "Three of A Kind": False, "Two Pair": False, "Pair": False, "High Card": True}

    match value % 15:
        case 1:
            hier["Quads"] = True
        case 10:
            hier["Full House"] = True
        case 9:
            hier["Three of A Kind"] = True
        case 7:
            hier["Two Pair"] = True
        case 6:
            hier["Pair"] = True
        case 5:
            hier["High Card"] = True

    if straight_check(ranks):
        hier["Straight"] = True
    if flush_check(suits):
        hier["Flush"] = True

    if hier["Flush"] and hier["Straight"]:
        hier["Straight Flush"] = True

    if hier["Straight Flush"] and ranks_value == 0b111110000000000:
        hier["Royal Flush"] = True

    #handles ranking by sorting the rank
    sorted_ranks = sorted(rank_counts.items(), key=lambda x: (x[1], x[0]), reverse=True)
    rank_order = [rank for rank, count in sorted_ranks]

    # Build comparison value using bit shifting (4 bits per rank, up to 5 ranks)
    comparison_value = 0
    for i, rank in enumerate(rank_order):
        comparison_value |= rank << (16 - i*4)

    # Special handling for straights (compare by high card)
    if hier["Straight"] or hier["Straight Flush"]:
        ace_low_mask = 0b1000000001111
        if ranks_value == ace_low_mask:
            comparison_value = 5  # Wheel (5-high straight is lowest)
        else:
            # Find highest rank
            for i in range(15):
                if ranks[i] == 1:
                    comparison_value = 14 - i
                    break

    # Determine the best hand type and return HandRank
    for hand_type in ["Royal Flush", "Straight Flush", "Quads", "Full House",
                      "Flush", "Straight", "Three of A Kind", "Two Pair", "Pair", "High Card"]:
        if hier[hand_type]:
            return HandRank(hand_type, comparison_value, ranks_value)




def straight_check(rankbits):
    if not rankbits:
        raise ValueError("expected bitarray")
    ace_low_mask = 0b1000000001111 #hard check for low straight

    value = int(rankbits.to01(), 2)
    lsb = value & -value
    norm = value >> (lsb.bit_length() - 1)
    
    if norm == 0b11111:
        return True
    if value == ace_low_mask:
        return True
    return False

def flush_check(suits):
    if not suits:
        raise ValueError("expected suits list")
    return all(suit == suits[0] for suit in suits)


    


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    
    h = [Card(9,"c"),Card(9,"s"),Card(9,"h"),Card(9,"d"),Card(13,"h")]
    print(f"Hand: {h}")
    print(f"Ranking: {evaluate_hand(h)}")
    print()

    royal = [Card(14,"h"),Card(13,"h"),Card(12,"h"),Card(11,"h"),Card(10,"h")]
    print(f"Hand: {royal}")
    print(f"Ranking: {evaluate_hand(royal)}")
    print()

    pair = [Card(14,"h"),Card(14,"d"),Card(10,"h"),Card(9,"h"),Card(8,"h")]
    print(f"Hand: {pair}")
    print(f"Ranking: {evaluate_hand(pair)}")
    print()

    print(f"Quads > Pair: {evaluate_hand(h) > evaluate_hand(pair)}")
    print(f"Royal Flush > Quads: {evaluate_hand(royal) > evaluate_hand(h)}")