import time
import numpy as np
from core.pfa import PFA

def simulate_monte_carlo(pfa: PFA, word: str, n_trial: int = 1000, seed: int = None) -> dict:
    """
    Run a monte Carlo Simualtion to estimate the emperical acceptance probability for each word in the PFA 
    
    pfa (PFA): instance of PFA class.
    word (str): The input string to process.
    n_trial (int): The number of simulations to run.
    seed (int): Random seed for reproducibility.
    """
    if seed is not None:
        np.random.seed(seed)    
        
    
    accept_count = 0
    probabilities = []
    
    start_time = time.time()
    for _ in range(n_trial):
        accepted, prob = pfa.run_once(word)
        if accepted:
            accept_count += 1
        probabilities.append(prob)
    end_time = time.time()
    
    acceptance_prob = accept_count / n_trial
    avg_path_prob = np.mean(probabilities)
    std_path_prob = np.std(probabilities)
    
    return {
        "word": word,
        "n_trial": n_trial,
        "acceptance_prob": acceptance_prob,
        "avg_path_prob": avg_path_prob,
        "std_path_prob": std_path_prob,
        "time_taken": end_time - start_time 
    }
    