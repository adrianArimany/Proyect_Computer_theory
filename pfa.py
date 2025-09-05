
import random


class PFA:
    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        """
        states: set of states
        alphabet: list of symbols
        transitions: dict of dicts { (state, symbol): {next_state: prob,
        """
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states
        
        
    def run_once(self, input):
        """
        docstring
        """
        current_state = self.start_state
        total_prob = 1.0
        
        for symb in input:
            if (current_state, symb) not in self.transitions:
                return False, 0.0
            
            next_states = self.transitions[(current_state, symb)]
            states = list(next_states.keys())
            probs = list(next_states.values())
            
            current_state = random.choices(states, weights=probs)[0]
            total_prob *= probs[states.index(current_state)]

        accepted = current_state in self.accept_states
        return accepted, total_prob
        
    def simulate(self, input, n = 10000):
        """
        docstring
        """
        accept_count = 0
        total_prob = 0.0
        
        for _ in range(n):
            accepted, prob = self.run_once(input)
            total_prob += prob
            if accepted:
                accept_count += 1
                
        acceptance_rate = accept_count / n
        avg_prob = total_prob / n 
        
        return acceptance_rate, avg_prob