from simulation.monte_carlo import simulate_monte_carlo
from simulation.matrix_method import simulate_matrix_method

def estimate_cut_point(pfa, word,n_trails = 10000, method = "monte_carlo", threshold = 0.5):
    """_summary_

    Args:
        pfa: PFA instance_
        word (str): word to be analyzed
        n_traials (int): Number of trails for the monte carlo, Defaults to 10000.
        method (str): Method being tested, either monte Carlo or Matrix method. Defaults to "monte_carlo".
        threshold (float): Cut point threshold in [0,1]. Defaults to 0.5.

    Raises:
        ValueError: if a method is not specified correctly.

    Returns:
        dict: dictionary with probability, threshhold, and comparison result.
    """
    assert 0 <= threshold <= 1, "Threshold must be in [0,1]"
    if method == "monte_carlo":
        result = simulate_monte_carlo(pfa, word, n_trial=n_trails)
        prob = result["acceptance_probability"]
    elif method == "matrix_method":
        result = simulate_matrix_method(pfa, word)
        prob = result["exact_probability"]
    else:
        raise ValueError("Method must be either 'monte_carlo' or 'matrix_method'")
    
    return {
        "word": word,
        "method": method,
        "probability": prob,
        "threshold": threshold,
        "is_above_threshold": prob > threshold
    }
    