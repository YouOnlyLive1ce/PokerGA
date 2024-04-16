from treys import Card, Evaluator, Deck
from random import shuffle, sample
import bisect
import time

class Player:
    def __init__(self, stack) -> None:
        self.stack = stack
        self.hand = None
        self.fold = False
        self.allin = False
        self.amount_rebuys = 0

    def bet(self, board):
        bet_amount = self.estimate_bet(board, self.hand)
        board._validate_bet(self, bet_amount)

    def estimate_bet(self, board, hand):
        # for manual enter of bet
        bet_amount = int(input())
        return bet_amount

    def blind(self, blind_value, board):
        # print(blind_value)
        board.pot += blind_value
        self.stack -= blind_value
        board.players_bets[self] = blind_value

class Board:
    def __init__(self) -> None:
        self.current_street_index = 0
        self.streets = None
        self.bets_equal = False
        self.players_bets = {}
        self.players_stacks = {}
        self.street_max_bet = 0
        self.pot = 0
        self.amount_folds = 0
        self.amount_allin = 0

    def set_players_stacks(self, players_stacks):
        self.players_stacks = players_stacks

    def set_streets(self, deck):
        self.streets = ["preflop", deck.draw(3), deck.draw(1), deck.draw(1)]

    def _validate_bet(self, player, bet_amount):
        """Ensures that bet is valid"""

        # Auto bets
        if player.fold:
            # print("player already folded")
            return
        if player.allin:
            self._place_bet(player, 0)
            return

        # Bet no more than min total stack
        players_total_stack = self.players_stacks
        for player_temp in players_total_stack.keys():
            if player_temp in self.players_bets:
                players_total_stack[player_temp] += self.players_bets[player_temp]
        max_bet_on_street = min(players_total_stack.values())
        # print("max bet on this street is ", max_bet_on_street)

        # if player himself is min player stack, then skip (he goes allin)
        if player.stack == max_bet_on_street:
            pass
        elif player in self.players_bets and bet_amount + self.players_bets[player] > max_bet_on_street:
            bet_amount = max_bet_on_street - self.players_bets[player]
            # print("bet fixed: ", bet_amount)

        # If player already bets and bet=max and not preflop <?>
        if player in self.players_bets and self.players_bets[
            player] == self.street_max_bet and self.current_street_index != 0:
            self._place_bet(player, 0)
            return

        # Call allin
        if self.amount_allin >= 1:
            if player in self.players_bets:
                bet_to_call_allin = min(self.street_max_bet - self.players_bets[player], player.stack)
            else:
                bet_to_call_allin = min(self.street_max_bet, player.stack)
            if bet_amount >= bet_to_call_allin:
                player.stack -= bet_to_call_allin
                self._place_bet(player, bet_to_call_allin)
                player.allin = True
                # print("player call allin with bet", bet_to_call_allin)
                return

        # Allin
        if bet_amount >= player.stack:
            # print("player goes all in with bet", player.stack)
            self.amount_allin += 1
            player.allin = True
            bet_amount = player.stack

            # Bet no more than opponent stack
            # max_bet=tournament.player_min_stack().stack
            # if bet_amount>max_bet:
            #     bet_amount=max_bet

            player.stack -= bet_amount
            self._place_bet(player, bet_amount)
            return

        # Casual bet/ check = bet=0
        player.stack -= bet_amount
        self._place_bet(player, bet_amount)

        # Fold
        if self.players_bets[player] < self.street_max_bet and player.allin == False:
            player.fold = True
            self.amount_folds += 1
            # print("player folds")
            self.players_bets.pop(player)
            return

    def _place_bet(self, player, bet_amount):
        if player in self.players_bets:
            self.players_bets[player] += bet_amount
        else:
            self.players_bets[player] = bet_amount

        # print("player bet ", bet_amount)
        self.pot += bet_amount
        self.street_max_bet = max(self.street_max_bet, self.players_bets[player])
        # check if all bets on street are equal
        first_value = next(iter(self.players_bets.values()))
        self.bets_equal = all(value == first_value for value in self.players_bets.values())

class Tournament:
    def __init__(self, players, rebuy_allowed=True) -> None:
        self.boards = []
        self.players = players
        self.current_deck = None
        self.current_board = None
        self.rebuy_allowed = rebuy_allowed

    def get_players_available_stacks(self):
        players_stacks = {}
        for player in self.players:
            players_stacks[player] = player.stack
        return players_stacks

    def play_one_game(self):
        # Initialize cards
        self.current_deck = Deck()
        current_board = Board()
        current_board.set_players_stacks(self.get_players_available_stacks())
        current_board.set_streets(self.current_deck)
        self.current_board = current_board

        for player in self.players:
            if player.stack <= 2 and self.rebuy_allowed:
                # print("player rebuys")
                player.stack = 100
                player.amount_rebuys += 1
            player.hand = self.current_deck.draw(2)
            # Card.print_pretty_cards(player.hand)

        # Blinds
        players_blinds = [1, 2]
        shuffle(players_blinds)
        for i in range(len(self.players)):
            self.players[i].blind(players_blinds[i], self.current_board)

        # streets
        for self.current_board.current_street_index in range(len(self.current_board.streets)):
            if self.current_board.current_street_index != 0:  # if not preflop
                pass
                # Card.print_pretty_cards(self.current_board.streets[self.current_board.current_street_index])
            while "Bets not equal":
                for player in self.players:
                    player.bet(self.current_board)

                    if self.current_board.amount_folds >= 1 and self.current_board.amount_folds == len(
                            self.players) - 1:
                        # print("every player except one folds")
                        self.choose_winner()
                        return
                if self.current_board.amount_allin == len(self.players):
                    # print("all players allin")
                    break
                if self.current_board.bets_equal and len(self.current_board.players_bets) > 1:
                    # print("street over, bets equal")
                    break
                # print("Players total bets on street")
                for player in self.players:
                    pass # print(self.current_board.players_bets[player])

            # Reset board flags and temps <create new?>
            self.current_board.bets_equal = False
            self.current_board.street_max_bet = 0
            self.current_board.players_bets = {}
            # self.current_board.amount_allin=0
            # self.current_board.amount_folds=0
        self.choose_winner()
        return

    # def play_till_lose(self):

    def choose_winner(self):
        hand_scores = []
        for player in self.players:
            if not player.fold:
                hand_scores.append(evaluator.evaluate(player.hand,
                                                      self.current_board.streets[1] + self.current_board.streets[2] +
                                                      self.current_board.streets[3]))
            else:
                hand_scores.append(7463)  # worst hand=7462

        winner_index = hand_scores.index(min(hand_scores))
        # print("player #", winner_index, " wins")
        self.players[winner_index].stack += self.current_board.pot
        # print("Stacks:")
        for player in self.players:
            pass
            #print(player.stack)

        # Reset player flags
        for player in self.players:
            player.hand = None
            player.fold = False
            player.allin = False


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
        self.preflop_ranges = [1] + preflop_bounds + [7462]
        self.postflop_ranges = [1] + postflop_bounds + [7462]
        self.pot_coefficients = [2, 1, 0.5, 0.25, 0]

    def estimate_bet(self, board, hand):
        # ?if AK, than not neccesairly bet 0.5*pot, also may check (kinda bluffs) (prevent overfold)?
        board_cards_known = []
        # if board.current_street_index==0:
        #     board_cards_known=[Card.new('Ah'), Card.new('Kd'), Card.new('Qs')]
        # else:
        #     for i in range(1, board.current_street_index+1):
        #         board_cards_known.append(board.streets[i])
        hand_power = evaluator.evaluate(hand, board.streets[1] + board.streets[2] + board.streets[3])

        range_index = bisect.bisect_left(self.postflop_ranges, hand_power)
        bet_coefficient = self.pot_coefficients[range_index - 1]
        bet = bet_coefficient * board.pot
        return bet

    def fitness(self):
        # To understand if chromosome is good
        return self.stack / (self.amount_rebuys + 1)

    def mutate_postflop(self):
        # ?change ranges +-50% ?
        mutate_bound = sample(range(1, 7462), 1)[0]
        mutate_index = bisect.bisect_left(self.postflop_ranges, mutate_bound)
        self.postflop_ranges[mutate_index - 1] = mutate_bound

    def mutate_preflop(self):
        # ?change ranges +-50% ?
        mutate_bound = sample(range(1, 7462), 1)[0]
        mutate_index = bisect.bisect_left(self.preflop_ranges, mutate_bound)
        self.preflop_ranges[mutate_index - 1] = mutate_bound

    def crossover_postflop(self, chromosome2):
        crossover_index = sample(range(2, 5), 1)[0]
        temp = self.postflop_ranges[crossover_index - 1]
        self.postflop_ranges[crossover_index - 1] = chromosome2.postflop_ranges[crossover_index]
        chromosome2.postflop_ranges[crossover_index] = temp
        chromosome2.postflop_ranges.sort()
        self.postflop_ranges.sort()
        return chromosome2


# Initial stack
deck = Deck()
evaluator = Evaluator()
# initiate random chromosomes
random_player = GeneticPlayer()  # will not evolve
genetic_players = []
tournaments = []

class GeneticAlgorithm:
    def __init__(self):
        self.deck = deck
        self.evaluator = Evaluator()
        self.genetic_players = []

    def create_initial_players(self, n=200):
        for i in range(n):
            self.genetic_players.append(GeneticPlayer())

    def play_tournament(self, n=100):
        for i in range(0, len(self.genetic_players), 2):
            tournament = Tournament([self.genetic_players[i], self.genetic_players[i+1]])
            print("a")
            for game_number in range(n):
                tournament.play_one_game()
            stacks = tournament.get_players_available_stacks()
            self.genetic_players[i] = stacks[self.genetic_players[i]]
            self.genetic_players[i+1] = stacks[self.genetic_players[i+1]]
        # self.print_generation()

    def print_generation(self, n=None):
        extra_space = ''
        if type(n) == int:
            print(f"Generation #{n}:")
            extra_space = '  '
        for i, player in enumerate(self.genetic_players):
            print(f"{extra_space}Player #{i+1}: {player.fitness()}")

    def new_generation(self):
        generation = self.genetic_players
        generation.sort(key=lambda player: player.fitness(), reverse=True)
        generation = generation[:int(len(self.genetic_players)/2)]
        for i in range(len(generation)):
            generation[i].stack = 100
        new_generation = [player for player in generation]
        # crossover
        for player in generation:
            player.mutate_postflop()
            player.mutate_preflop()
            new_generation.append(player)
        self.genetic_players = [new for new in new_generation]


algorithm = GeneticAlgorithm()
algorithm.create_initial_players()
for i in range(1000):
    algorithm.play_tournament()
    # algorithm.print_generation(n=i+1)
    algorithm.new_generation()
