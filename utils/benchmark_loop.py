import pandas as pd
from analysis.loop_analysis import loop_retun_probability

def benchmark_loop(pfa, symbol, state, k):
    """
    Run loop return probability analysis and return results as DataFrame.

    Args:
        pfa (PFA): automaton
        symbol (str): loop symbol
        state (str): loop state
        k (int): number of steps

    Returns:
        pd.DataFrame
    """
    prob = loop_retun_probability(pfa, symbol, state, k)

    df = pd.DataFrame([{
        "Symbol": symbol,
        "State": state,
        "Steps (k)": k,
        "Return Probability": prob
    }])

    return df
