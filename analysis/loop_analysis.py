import numpy as np
import time

def loop_acceptance_probability_matrix(pfa, symbol, k):
    """
    Exact acceptance probability of repeating `symbol` k times.
    Uses matrix multiplication.
    """
    v0 = pfa.get_intial_vector()
    f = pfa.get_final_vector()
    mu = pfa.get_transition_matrices()[symbol]

    start = time.time()
    prob = float(v0 @ np.linalg.matrix_power(mu, k) @ f)
    return {
        "method": "matrix",
        "symbol": symbol,
        "k": k,
        "probability": prob,
        "time_taken": time.time() - start
    }


def loop_acceptance_probability_montecarlo(pfa, symbol, k, n_trial=10000):
    """
    Monte Carlo estimate of acceptance probability of symbol^k.
    """
    start = time.time()
    accept_count = 0
    for _ in range(n_trial):
        word = symbol * k
        is_accepted, _ = pfa.run_once(word)
        if is_accepted:
            accept_count += 1

    return {
        "method": "monte_carlo",
        "symbol": symbol,
        "k": k,
        "n_trial": n_trial,
        "probability": accept_count / n_trial,
        "time_taken": time.time() - start
    }
