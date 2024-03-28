# !pip install treys
from treys import Card, Evaluator,Deck

evaluator = Evaluator()
deck = Deck()

class Player:
    def __init__(self, stack) -> None:
        self.hand=deck.draw(2)
        self.stack=stack
        self.fold=False
    def bet(self):
        if self.fold==True:
            print("player already folded")
            return
        bet_amount=int(input())
        if bet_amount>self.stack:
            print("player goes all in with bet", self.stack)
            bet_amount=self.stack
            # <some logic>
        self.stack-=bet_amount
        board._player_bet(self,bet_amount)
    def blind(self, blind_value):
        board.pot+=blind_value
        self.stack-=blind_value
        board.players_bets[self]=blind_value

class Board:
    def __init__(self) -> None:
        self.streets=["preflop", deck.draw(3),deck.draw(1),deck.draw(1)]
        self.bets_equal=False
        self.players_bets={}
        self.street_max_bet=0
        self.amount_folds=0
        self.pot=0

    def _player_bet(self, player, bet_amount):
        if player in self.players_bets:
            self.players_bets[player]+=bet_amount
        else:
            self.players_bets[player]=bet_amount

        if self.players_bets[player]<self.street_max_bet:
            player.fold=True
            self.amount_folds+=1
            print("player folds")
            board.players_bets.pop(player)
            return

        self.pot+=bet_amount
        self.street_max_bet=max(self.street_max_bet, self.players_bets[player])
        # check if all values are equal
        first_value = next(iter(self.players_bets.values()))
        self.bets_equal=all(value == first_value for value in self.players_bets.values())

# Game
player1=Player(10)
player2=Player(20)
players=[player1,player2]
Card.print_pretty_cards(player1.hand)
Card.print_pretty_cards(player2.hand)
board=Board()
# Blinds
player1.blind(1)
player2.blind(2)

#streets
for street in board.streets:
    if street!="preflop":
        Card.print_pretty_cards(street)
    while True:
        for player in players:
            player.bet()
            # fix: check raise call <bet 0> 
        if board.bets_equal:
            print("street over")
            break
        if board.amount_folds==len(board.players_bets)-1:
            print("every player except one folds")
            break
    
    board.bets_equal=False
    board.street_max_bet=0
    board.players_bets={}

p_score=[]
for player in players:
    p_score.append(evaluator.evaluate(board.streets[1]+board.streets[2]+board.streets[3], player.hand))

print("player #",p_score.index(max(p_score))," wins")