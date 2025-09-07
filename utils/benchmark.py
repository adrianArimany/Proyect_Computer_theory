import pandas as pd
from simulation.monte_carlo import simulate_monte_carlo
from simulation.matrix_method import simulate_matrix_method

def benchmark_pfa(pfa, words, n_trial=1000):
    """_summary_

    Args:
        pfa (_type_): _description_
        words (_type_): _description_
        n_trial (int, optional): _description_. Defaults to 1000.
    """
    
    word = words[0]
    
    #-- Monte carlo ---    
    mc_result = simulate_monte_carlo(pfa, word, n_trial=n_trial)
    
    # Normalize Monte Carlo keys
    mc_row = {
        "Word": mc_result.get("word", word),
        "Method": "Monte Carlo",
        "Probability": mc_result.get("acceptance_probability")
                      or mc_result.get("acceptance_prob", 0.0),
        "Average Path Prob": mc_result.get("average_path_probability")
                             or mc_result.get("avg_path_prob", None),
        "Stddev Path Prob": mc_result.get("stddev_path_probability")
                            or mc_result.get("std_path_prob", None),
        "Elapsed Time (s)": mc_result.get("time_taken", None),
        "Trials": mc_result.get("n_trial", n_trial),
    }
    
    #--- Matrix Method ---
    
    mm_result = simulate_matrix_method(pfa, word)
    
    mm_row = {
        "Word": mm_result.get("word", word),
        "Method": "Matrix Product",
        "Probability": mm_result.get("exact_probability", 0.0),
        "Average Path Prob": None,
        "Stddev Path Prob": None,
        "Elapsed Time (s)": mm_result.get("time_taken", None),
        "Trials": None,
    }
    
    if "acceptance_probability" not in mc_result or mm_result is None:
        raise ValueError("Monte Carlo simulation or Matrix method  failed or returned invalid structure.")
    
    return pd.DataFrame([mc_row, mm_row])

