import time
import pandas as pd
from analysis.loop_analysis import (
    loop_acceptance_probability_matrix,
    loop_acceptance_probability_montecarlo
)

def benchmark_loop(pfa, symbol, k, n_trial=10000):
    """
    Benchmark loop acceptance probability with both methods.

    Args:
        pfa (PFA): automaton
        symbol (str): loop symbol
        k (int): number of repetitions
        n_trial (int): Monte Carlo trials

    Returns:
        pd.DataFrame: one row with results of both methods
    """
    # Matrix method
    t0 = time.perf_counter()
    mat_res = loop_acceptance_probability_matrix(pfa, symbol, k)
    t1 = time.perf_counter()
    mat_prob = mat_res.get("probability", None)
    runtime_matrix_ms = (t1 - t0) * 1000.0

    # Monte Carlo method
    t0 = time.perf_counter()
    mc_res = loop_acceptance_probability_montecarlo(pfa, symbol, k, n_trial=n_trial)
    t1 = time.perf_counter()
    mc_prob = mc_res.get("probability", None)
    mc_stderr = mc_res.get("stderr", None)
    runtime_mc_ms = (t1 - t0) * 1000.0

    row = {
        "Symbol": symbol,
        "k": int(k),
        "Trials": int(n_trial),
        "Matrix Probability": mat_prob,
        "Monte Carlo Probability": mc_prob,
        "Monte Carlo StdErr": mc_stderr,
        "Runtime Matrix (ms)": runtime_matrix_ms,
        "Runtime Monte Carlo (ms)": runtime_mc_ms,
    }

    return pd.DataFrame([row])
