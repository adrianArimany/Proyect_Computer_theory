import numpy as np
from core.pfa import PFA

def loop_retun_probability(pfa: PFA, symbol: str, state: str, k: int) -> float:
    """
    Computes the probability of returning to a given state after k steps
    using only the specified symbol.
    
    Args:
        pfa (PFA): instance of PFA class.
        symbol (str): the symbol to be used for transitions.
        state (str): the state to return to.
        k (int): number of steps.

    Returns:
        float: Probability of returning to the state after k steps.
    """
    assert symbol in pfa.alphabet, f"Symbol {symbol} not in alphabet"
    assert state in pfa.states, f"State {state} not in states"
    assert k >= 1, "k must be at least 1"
    
    mu = pfa.get_transition_matrices()
    T = mu[symbol] # Transition matrix for this symbol only
    
    index = list(pfa.states).index(state)
    v = np.zeros((1,len(pfa.states)))
    v[0,index] = 1.0 # Initial vector at the given state
    
    #Evolve k times
    T_k = np.linalg.matrix_power(T, k)
    result = float(np.dot(v, T_k)[0][index])
    return result