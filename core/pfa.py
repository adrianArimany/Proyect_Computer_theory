import numpy as np
import random
import warnings

class PFA:
    def __init__(self, states, alphabet, transitions, start_state, accept_states, allow_substochastic=True):
        """
        states: set of states
        alphabet: list of symbols
        transitions: dict of dicts
        start_state: start state
        accept_states: set of accept states
        state_index: mapping from state to index
        allow_substochastic: if True, allows transitions that sum to less than 1
        """
        self.states = list(states)
        self.alphabet = list(alphabet)
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = set(accept_states)
        self.state_index = {state: i for i, state in enumerate(self.states)}
        self.allow_substochastic = allow_substochastic
        self._validate()
        
        
    def _validate(self):
        for (state, symbol), outcomes in self.transitions.items():
            if symbol not in self.alphabet:
                raise ValueError(f"Symbol {symbol} not in alphabet")
            if state not in self.states:
                raise ValueError(f"State {state} not in states")
            total = sum(outcomes.values())
            #The following is in case the PFA is a substochastic one.
            if total > 1.0 + 1e-8:
                raise ValueError(f"Probabilities from ({state}, '{symbol}') exceed 1. Got {total}.")
            if total < 1.0 - 1e-8:
                if self.allow_substochastic:
                    warnings.warn(f"Warning: Substochastic transition at ({state}, '{symbol}'), total = {total}")
                else:
                    raise ValueError(f"Probabilities from ({state}, '{symbol}') are substochastic but not allowed.")
    
    
    def run_once(self, word):
        current = self.start_state
        prob = 1.0
        for symbol in word:
            key = (current, symbol)
            if key not in self.transitions:
                return False, 0.0 # No transition defined
            outcomes = self.transitions[key]
            next_states = list(outcomes.keys())
            weights = list(outcomes.values())
            chosen = random.choices(next_states, weights=weights, k=1)[0]
            prob *= outcomes[chosen]
            current = chosen
        return current in self.accept_states, prob
    
    def get_transition_matrices(self):
        """_summary_
        Creates a matrix for each symbol in the alphabet, where the entry (i, j)
        Returns:
            matrix: dim(Q x Q)
        """
        Q = len(self.states)
        matrices = {symbol: np.zeros((Q, Q)) for symbol in self.alphabet}
        
        for (src, sym), outcomes in self.transitions.items():
            i = self.state_index[src]
            for dst, prob in outcomes.items():
                j = self.state_index[dst]
                matrices[sym][i,j] = prob
        return matrices
    
    def get_intial_vector(self):
        v = np.zeros((1, len(self.states)))
        v[0, self.state_index[self.start_state]] = 1.0
        return v
    
    def get_final_vector(self):
        v = np.zeros((len(self.states), 1))
        for state in self.accept_states:
            v[self.state_index[state], 0] = 1.0
        return v       