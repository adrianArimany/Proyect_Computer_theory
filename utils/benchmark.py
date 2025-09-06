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
        
    mc_result = simulate_monte_carlo(pfa, words[0], n_trial=n_trial)
    mm_result = simulate_matrix_method(pfa, words[0])
    
    if "acceptance_probability" not in mc_result:
        raise ValueError("Monte Carlo simulation failed or returned invalid structure.")

    
    df = pd.DataFrame([
    {
    "Method": "Monte Carlo",
    "Probability": mc_result["acceptance_probability"],
    "Average Path Prob": mc_result["average_path_probability"],
    "Stddev Path Prob": mc_result["stddev_path_probability"],
    "Elapsed Time (s)": mc_result["time_taken"],
    "Trials": mc_result["n_trial"]
    },
    {
    "Method": "Matrix Product",
    "Probability": mm_result.exact_result.get("exact_probability", 0.0),
    "Average Path Prob": None,
    "Stddev Path Prob": None,
    "Elapsed Time (s)": mm_result.exact_result["time_taken"],
    "Trials": None
    }
    ])
    
    return df

