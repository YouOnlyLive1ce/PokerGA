# !pip install treys
from treys import Card, Evaluator, Deck
from random import shuffle, sample
import bisect
import time

class Player:
    def __init__(self, stack) -> None:
        self.stack=stack
        self.hand=None
        self.fold=False
        self.allin=False
        self.raised=False # flag that betted once already
        self.amount_rebuys=0

    def bet(self, board):
        bet_amount= self.estimate_bet(self.hand, board)
        if bet_amount>0:
            self.raised=True
        board._validate_bet(self, bet_amount) 

    def estimate_bet(self, board, hand):
        # for manual enter of bet
        bet_amount=int(input())
        return bet_amount
    
    def blind(self, blind_value,board):
        # print(blind_value)
        self.stack-=blind_value
        board.pot+=blind_value

class Board:
    def __init__(self) -> None:
        self.current_street_index=0
        self.streets=None
        self.bets_equal=False
        self.players_bets={}
        self.street_max_bet=0 # largest bet from some player
        self.pot=0
        self.amount_folds=0
        self.amount_allin=0

    def set_streets(self, deck):
        self.streets=["preflop", deck.draw(3),deck.draw(1),deck.draw(1)]

    def _validate_bet(self, player, bet_amount):
        """Ensures that bet is valid"""

        # Auto bets
        if player.fold==True:
            # print("player already folded")
            return
        if player.allin==True:
            self.save_bet(player,0)
            return
        
        # Bet no more than min total stack
        players_total_stack=tournament.get_players_available_stacks() 
        for player_temp in players_total_stack.keys():
            if player_temp in self.players_bets:
                players_total_stack[player_temp]+=self.players_bets[player_temp]
        max_bet_on_street=min(players_total_stack.values())
        # print("max bet on this street is ", max_bet_on_street)
        
        # if player himself is min player stack, then skip (he goes allin)
        if player.stack==max_bet_on_street:
            pass
        elif player in self.players_bets and bet_amount+self.players_bets[player]>max_bet_on_street:
            bet_amount=max_bet_on_street-self.players_bets[player]
            # print("bet fixed: ", bet_amount)

        # If player already bets and bet=max and not preflop <?>
        if player in self.players_bets and self.players_bets[player]==self.street_max_bet and self.current_street_index!=0:
            self.save_bet(player,0)
            return
        
        # Call allin
        if self.amount_allin>=1:
            if player in self.players_bets:
                bet_to_call_allin=min(self.street_max_bet-self.players_bets[player],player.stack)
            else:
                bet_to_call_allin=min(self.street_max_bet,player.stack)
            if bet_amount>=bet_to_call_allin:
                player.stack-=bet_to_call_allin
                self.save_bet(player,bet_to_call_allin)
                player.allin=True
                # print("player call allin with bet",bet_to_call_allin)
                return
        
        # Allin
        if bet_amount>=player.stack:
            # print("player goes all in with bet", player.stack)
            self.amount_allin+=1
            player.allin=True
            bet_amount=player.stack             
            player.stack-=bet_amount
            self.save_bet(player,bet_amount)
            time.sleep(1)
            return
        
        # Casual bet
        player.stack-=bet_amount
        self.save_bet(player,bet_amount)
        
        # Fold
        if self.players_bets[player]<self.street_max_bet and player.allin==False:
            player.fold=True
            self.amount_folds+=1
            # print("player folds")
            self.players_bets.pop(player)
            return
        
    def save_bet(self, player, bet_amount):
        # save to dict
        if player in self.players_bets:
            self.players_bets[player]+=bet_amount
        else:
            self.players_bets[player]=bet_amount
        # print("bet saved ", bet_amount)
        
        # statistics
        self.street_max_bet=max(self.street_max_bet, self.players_bets[player])
        # check if all bets on street are equal
        first_value = next(iter(self.players_bets.values()))
        self.bets_equal=all(value == first_value for value in self.players_bets.values())

    def move_bets_to_pot(self):
        # move every player bet to pot
        for player in self.players_bets.keys():
            bet_amount=self.players_bets[player]
            # print("player bet ", bet_amount)
            self.pot+=bet_amount

class Tournament:
    def __init__(self,players, rebuy_allowed=True) -> None:
        self.boards = []
        self.players = players
        self.current_deck=None
        self.current_board=None
        self.rebuy_allowed=rebuy_allowed

    def get_players_available_stacks(self):
        players_stacks={}
        for player in self.players:
            players_stacks[player]=player.stack
        return players_stacks
    
    def play_one_game(self):
        #Initialize cards
        self.current_deck=Deck()
        
        current_board=Board()
        current_board.set_streets(self.current_deck)
        self.current_board=current_board
        
        for player in self.players:
            if player.stack<=2 and self.rebuy_allowed:
                # print("player rebuys")
                player.stack=100
                player.amount_rebuys+=1
            player.hand=self.current_deck.draw(2)
            # Card.print_pretty_cards(player.hand)
        
        # Blinds
        players_blinds=[1,1]
        shuffle(players_blinds)
        for i in range(len(self.players)):
            self.players[i].blind(players_blinds[i], self.current_board)
        
        #streets
        for self.current_board.current_street_index in range(len(self.current_board.streets)):
            # if self.current_board.current_street_index!=0: # if not preflop
            #     Card.print_pretty_cards(self.current_board.streets[self.current_board.current_street_index])
            while "Bets not equal":
                for player in self.players:
                    player.bet(self.current_board)
                    
                    if self.current_board.amount_folds>=1 and self.current_board.amount_folds==len(self.players)-1:
                        # print("every player except one folds")
                        self.choose_winner()
                        return
                if self.current_board.amount_allin==len(self.players):
                    # print("all players allin")
                    break
                
                # print("Players total bets on street")
                # for player in self.players:
                    # print(self.current_board.players_bets[player])
                
                if self.current_board.bets_equal and len(self.current_board.players_bets)>1:
                    # print("street over, bets equal")
                    break
                
                # Check whose raise is less, make them fold
                every_player_raised=True
                for player in self.players:
                    if not player.raised:
                        every_player_raised=False
                if every_player_raised:
                    for player in self.players:
                        if self.current_board.players_bets[player]!=self.current_board.street_max_bet:
                            player.fold=True
                    self.choose_winner()  
                    return  
            self.current_board.move_bets_to_pot()
            
            # Reset player flags before next street
            for player in self.players:
                player.raised=False
            
            #Reset board flags and temps before next street
            self.current_board.bets_equal=False
            self.current_board.street_max_bet=0
            self.current_board.players_bets={}
        self.choose_winner()
        return
    
    def choose_winner(self):
        hand_scores=[]
        for player in self.players:
            if player.fold==False:
                hand_scores.append(evaluator.evaluate(player.hand, self.current_board.streets[1]+self.current_board.streets[2]+self.current_board.streets[3]))
            else:
                hand_scores.append(7463) #worst hand=7462

        winner_index=hand_scores.index(min(hand_scores))
        # print("player #",winner_index," wins")
        
        # Give pot and last raise back
        self.players[winner_index].stack+=self.current_board.pot
        self.players[winner_index].stack+=sum(list(self.current_board.players_bets.values()))
        # print("Stacks:")
        # for player in self.players:
        #     print(player.stack)
        
        # if game_number%20==0:
        #     sum_stacks=0
        #     for player in self.players:
        #         sum_stacks+=player.stack
        #     print(game_number, sum_stacks)
            
        # Reset player flags
        for player in self.players:
            player.hand=None
            player.fold=False
            player.allin=False

class GeneticPlayer(Player):
    def __init__(self) -> None:
        # Based on power of hand, player will bet some % of pot
        # Ranges will be corrected by genetic algorithm
        # Range is a slice of possible hand powers (1...7462), 1 is best
        # Initially bounds are random
    
        super().__init__(100)
        
        # Genes
        preflop_bounds = sample(range(1, 7462), 4)
        postflop_bounds = sample(range(1, 7462), 4)
        preflop_bounds.sort()
        postflop_bounds.sort()
        self.preflop_ranges=[1]+preflop_bounds+[7462]
        self.postflop_ranges=[1]+postflop_bounds+[7462]
        self.pot_coefficients=[2,1,0.5,0.25,0]
    
        def __str__(self):
            return f"stack: {self.stack}, preflop: {self.preflop_ranges}, postflop: {self.postflop_ranges}"
    
    def estimate_bet(self, hand, board):
        # ?if AK, than not neccesairly bet 0.5*pot, also may check (kinda bluffs) (prevent overfold)?
        board_cards_known=board.streets[1] #initially flop known
        if board.current_street_index==2:
            board_cards_known=board.streets[1]+board.streets[2]
        elif board.current_street_index==3:
            board_cards_known=board.streets[1]+board.streets[2]+board.streets[3]
            
        hand_power=evaluator.evaluate(hand, board_cards_known)
        # Find range of bet
        range_index=bisect.bisect_left(self.postflop_ranges, hand_power)
        bet_coefficient=self.pot_coefficients[range_index-1]
        
        # to avoid infinite re-raise
        if self.raised:
            bet_coefficient=0
        
        bet=bet_coefficient*board.pot
        return bet

    def fitness(self): 
        #To understand if chromosome is good
        return self.stack/(self.amount_rebuys+1)

    def mutate_postflop(self):
        # ?change ranges +-50% ?
        mutate_bound = sample(range(1, 7462), 1)[0]
        mutate_index=bisect.bisect_left(self.postflop_ranges, mutate_bound)
        self.postflop_ranges[mutate_index-1]=mutate_bound
    
    def crossover_postflop(self, chromosome2):
        crossover_index = sample(range(2, 5), 1)[0]
        temp=self.postflop_ranges[crossover_index-1]
        self.postflop_ranges[crossover_index-1]=chromosome2.postflop_ranges[crossover_index]
        chromosome2.postflop_ranges[crossover_index]=temp
        chromosome2.postflop_ranges.sort()
        self.postflop_ranges.sort()
        return chromosome2

# Initial stack 
deck=Deck()
evaluator = Evaluator()
# initiate random chromosomes
genetic_players=[]
tournaments=[]
# initiate 10 chromosomes
amount_chromosomes=10
crossover_rate=0.4
mutate_rate=0.3

for i in range (amount_chromosomes):
    genetic_players.append(GeneticPlayer())
    
# create 45 heads-up tournaments (each with each other)
for i in range (amount_chromosomes):
    for j in range(i+1,amount_chromosomes):
        tournament=Tournament([genetic_players[i],genetic_players[j]])
        tournaments.append(tournament)

for _ in range (10):
    for tournament in tournaments:
        # play 100 games, if one lose, then rebuy
        for game_number in range(100):
            tournament.play_one_game()
        
    #TODO: crossover crossover_rate*amount chromosomes with wheel: the better the chromosomes, the larger are chances
    #TODO: mutate mutate_rate*amount_chromosomes, chances are equal
    sorted_players=sorted(genetic_players, key=lambda player: player.fitness(), reverse=True)
  
def store_info():
    with open('results.txt', 'w') as file:
        for i in range(len(genetic_players)):
            file.write(f"Player # {i}: + stack: {genetic_players[i].stack}, preflop: {genetic_players[i].preflop_ranges}, postflop: {genetic_players[i].postflop_ranges}  + '\n'")
store_info()