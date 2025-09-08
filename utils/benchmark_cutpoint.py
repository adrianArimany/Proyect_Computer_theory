import pandas as pd
import itertools
import time
from analysis.cutpoint import estimate_cut_point


def benchmark_cutpoint(pfa, word, threshold=0.5, n_trial=1000):
    """
    Run cut-point analysis using both Monte Carlo and Matrix methods,
    and return results as a normalized DataFrame.

    Args:
        pfa (PFA): Probabilistic Finite Automaton
        word (str): Word to evaluate
        threshold (float): Cut-point threshold
        n_trial (int): Monte Carlo trials

    Returns:
        pd.DataFrame: Cut-point results (one row per method).
    """
    mc_cut = estimate_cut_point(pfa, word, n_trails=n_trial, method="monte_carlo", threshold=threshold)
    mm_cut = estimate_cut_point(pfa, word, method="matrix_method", threshold=threshold)

    df = pd.DataFrame([
        {
            "Word": mc_cut["word"],
            "Method": "Monte Carlo",
            "Probability": mc_cut["probability"],
            "Cut-point Threshold": mc_cut["threshold"],
            "Above Cut?": mc_cut["is_above_threshold"],
            "Trials": n_trial
        },
        {
            "Word": mm_cut["word"],
            "Method": "Matrix Product",
            "Probability": mm_cut["probability"],
            "Cut-point Threshold": mm_cut["threshold"],
            "Above Cut?": mm_cut["is_above_threshold"],
            "Trials": None
        }
    ])

    return df


def search_cut_point_words(pfa, max_length=3, threshold = None, interval = None, n_trial = 10000, time_limit= 10):
    """
    Search for words within a cut-point or interval probability.

    Args:
        pfa: PFA instance
        max_length (int): maximum word length
        threshold (float): single cut-point threshold
        interval (tuple[float,float]): probability interval [low, high]
        n_trial (int): Monte Carlo trials
        time_limit (float): max seconds allowed

    Returns:
        pd.DataFrame, dict: (results dataframe, timing summary)
    """
    
    start_time = time.time()
    results = []
    timing = {'Monte Carlo': [], 'Matrix Product': []}
    
    for length in range(1, max_length + 1):
        for word_tuple in itertools.product(sorted(pfa.alphabet), repeat=length):
            word = ''.join(word_tuple)
            
            
            if time.time() - start_time > time_limit:
                return pd.DataFrame(results), {
                    "Monte Carlo": sum(timing["Monte Carlo"]),
                    "Matrix Product": sum(timing["Matrix Product"]),
                    "StoppedEarly": True
                }
            
            
            
            # Monte Carlo
            t0 = time.time()
            mc = estimate_cut_point(pfa, word, n_trails=n_trial, method="monte_carlo", 
                                    threshold=threshold if threshold else 0.0)
            
            t1 = time.time()
            
            # Matrix Method
            t2 = time.time()
            mm = estimate_cut_point(pfa, word, method="matrix_method", 
                                    threshold=threshold if threshold else 0.0)
            
            t3 = time.time()
            
            
            timing["Monte Carlo"].append(t1 - t0)
            timing["Matrix Product"].append(t3 - t2)
            
            prob_mc, prob_mm = mc["probability"], mm["probability"]
            
            #If word is allowed:
            include = False
            if threshold is not None:
                include = prob_mc >= threshold or prob_mm >= threshold
            elif interval is not None:
                lo, hi = interval
                include = (lo <= prob_mc <= hi) or (lo <= prob_mm <= hi)
            else:
                raise ValueError("Either threshold or interval must be specified.")
            
            if include:
                results.append({
                    "Word": word,
                    "Monte Carlo Prob": prob_mc,
                    "Matrix Prob": prob_mm,
                    "Cut-point": threshold if threshold is not None else interval,
                    "MC Time (s)": t1 - t0,
                    "MM Time (s)": t3 - t2
                })
            
    return pd.DataFrame(results), {
        "Monte Carlo": sum(timing["Monte Carlo"]),
        "Matrix Product": sum(timing["Matrix Product"]),
        "StoppedEarly": False
    }
            