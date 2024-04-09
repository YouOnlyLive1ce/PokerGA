# !pip install treys
from treys import Card, Evaluator, Deck

class Player:
    def __init__(self, stack) -> None:
        self.stack=stack
        self.hand=None
        self.fold=False
        self.allin=False
    def bet(self, board):
        # Auto bets
        if self.fold==True:
            print("player already folded")
            return
        if self.allin==True:
            board._player_bet(self,0)
            print("auto bet 0")
            return
        # If player already bets and bet=max and not preflop (bigblind situation)
        if self in board.players_bets and board.players_bets[self]==board.street_max_bet and board.street!="preflop":
            board._player_bet(self,0)
            return
        
        # Read bet
        bet_amount=int(input())
        
        # Call allin
        if board.amount_allin>=1:
            if self in board.players_bets:
                bet_to_call_allin=min(board.street_max_bet-board.players_bets[self],self.stack)
            else:
                bet_to_call_allin=min(board.street_max_bet,self.stack)
            if bet_amount>=bet_to_call_allin:
                self.stack-=bet_to_call_allin
                board._player_bet(self,bet_to_call_allin)
                self.allin=True
                print("player call allin with bet",bet_to_call_allin)
                return
        # Allin
        if bet_amount>self.stack:
            print("player goes all in with bet", self.stack)
            board.amount_allin+=1
            self.allin=True
            bet_amount=self.stack
            self.stack-=bet_amount
            board._player_bet(self,bet_amount)
            return
        
        # Casual bet/ check = bet=0
        self.stack-=bet_amount
        board._player_bet(self,bet_amount)
        
        # Fold
        if board.players_bets[self]<board.street_max_bet and self.allin==False:
            self.fold=True
            board.amount_folds+=1
            print("player folds")
            board.players_bets.pop(self)
            return

    def blind(self, blind_value,board):
        board.pot+=blind_value
        self.stack-=blind_value
        board.players_bets[self]=blind_value

class Board:
    def __init__(self) -> None:
        self.current_street=None
        self.streets=None
        self.bets_equal=False
        self.players=[]
        self.players_bets={}
        self.street_max_bet=0
        self.pot=0
        self.amount_folds=0
        self.amount_allin=0

    def set_streets(self, deck):
        self.streets=["preflop", deck.draw(3),deck.draw(1),deck.draw(1)]
    def set_players(self, players):
        self.players=players

    def _player_bet(self, player, bet_amount):
        if player in self.players_bets:
            self.players_bets[player]+=bet_amount
        else:
            self.players_bets[player]=bet_amount

        self.pot+=bet_amount
        self.street_max_bet=max(self.street_max_bet, self.players_bets[player])
        # check if all bets on street are equal
        first_value = next(iter(self.players_bets.values()))
        self.bets_equal=all(value == first_value for value in self.players_bets.values())

class InfiniteTournament:
    def __init__(self,players) -> None:
        self.boards = []
        self.players = players
        self.current_deck=None
        self.current_board=None

    def play_one_game(self):
        #Initialize cards
        self.current_deck=Deck()
        
        current_board=Board()
        current_board.set_streets(self.current_deck)
        self.current_board=current_board
        
        # <if stack >0 >
        self.current_board.set_players(self.players)
        for player in self.current_board.players:
            player.hand=deck.draw(2)
            Card.print_pretty_cards(player.hand)
        
        # self.boards.append(self.current_board) # save stats
        
        # <make random>
        players[0].blind(1, self.current_board)
        players[1].blind(2, self.current_board)
        
        #streets
        for self.current_board.street in self.current_board.streets:
            if self.current_board.street!="preflop":
                Card.print_pretty_cards(self.current_board.street)
            while "Bets not equal":
                for player in self.current_board.players:
                    player.bet(self.current_board)
                    
                    if self.current_board.amount_folds>=1 and self.current_board.amount_folds==len(self.current_board.players)-1:
                        print("every player except one folds")
                        self.choose_winner()
                        return
                
                if self.current_board.bets_equal and len(self.current_board.players_bets)>1:
                    print("street over, bets equal")
                    break
                print("Players total bets on street")
                for player in self.current_board.players:
                    print(self.current_board.players_bets[player])
            
            #Reset flags and temps
            self.current_board.bets_equal=False
            self.current_board.street_max_bet=0
            self.current_board.players_bets={}
        self.choose_winner()
        return

    def choose_winner(self):
        evaluator = Evaluator()
        p_score=[]
        for player in self.current_board.players:
            if player.fold==False:
                p_score.append(evaluator.evaluate(self.current_board.streets[1]+self.current_board.streets[2]+self.current_board.streets[3], player.hand))
            else:
                p_score.append(7463) #worst hand=7462
        winner_index=p_score.index(min(p_score))
        print("player #",winner_index," wins")
        self.current_board.players[winner_index].stack+=self.current_board.pot
        print("Stacks:")
        for player in self.current_board.players:
            print(player.stack)

class Chromosome:
    def __init__(self) -> None:
        self.preflop_ranges
        self.flop_ranges
        
    # fixed bet = [0,0.25,0.5,1,2] of pot
    # if AK, than not neccesairly bet 0.5*pot, also may check
    # bet_coefficient=[hand_power_range: coefficient]
    # change ranges +-50%, initially uniform
    
    def bet(self, pot, hand_power):
        bet_coefficient= ... # based on genes: flop_ranges[hand_power]->coefficient
        bet=bet_coefficient*pot
        
    def fitness(): #To understand if chromosome is good
        ...
        
# Initial stack 
deck=Deck()
# initiate players and stacks
player1=Player(10)
player2=Player(20)
players=[player1,player2]
# initiate tournament
tournament=InfiniteTournament(players)
# save stacks after each game
# play 100 games, if one die, then rebuy
tournament.play_one_game()
