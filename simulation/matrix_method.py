import time
import numpy as np
from core.pfa import PFA

def simulate_matrix_method(pfa: PFA, word: str) -> dict:
    """
    Computes the acceptance probability of a word using the matrix method:
    
    A(w) = v_0 * mu(a1) * mu(a2) * ... * mu(an) * f^T
    
    where v_0 is the initial state vector, mu(a) is the transition matrix for symbol a,

    
    pfa (PFA): instance of PFA class.
    word (str): the word being tested.

    Returns:
        dict: Dictionary with exact probabilities and time taken.
    """
    
    mu = pfa.get_transition_matrices()
    v0 = pfa.get_intial_vector()
    f = pfa.get_final_vector()
    
    start_time = time.time()
    
    
    try:
        current = v0
        for symbol in word:
            if symbol not in mu:
                raise ValueError(f"Symbol {symbol} not in alphabet")
            current = np.dot(current, mu[symbol])
        
        result = float(np.dot(current, f)[0][0])
    except Exception as e:
        return {
            "word": word,
            "error": str(e),
            "exact_probability": 0.0,
            "time_taken": time.time() - start_time
        }
    end_time = time.time()
    
    return {
        "word": word,
        "exact_probability": result,
        "time_taken": end_time - start_time
    }   