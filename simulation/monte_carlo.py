def simulate_monte_carlo(pfa, input_string, num_simulations=1000) -> dict:
    """
    Simulates the PFA on the given input string multiple times and estimates the acceptance probability.
    
    
    pfa (PFA): The probabilistic finite automaton to simulate.
    input_string (str): The input string to process.
    num_simulations (int): The number of simulations to run.
        
    Returns:
        float: Estimated acceptance probability.
    """
    accept_count = 0
    for _ in range(num_simulations):
        current_state = pfa.start_state
        for symbol in input_string:
            current_state = pfa.next_state(current_state, symbol)
            if current_state is None:
                break
        if current_state in pfa.accept_states:
            accept_count += 1
    return accept_count / num_simulations