import json
from core.pfa import PFA

def load_pfa_from_json(file_path: str, allow_substochastic=True) -> PFA:
    '''
    The JSON file should have the following structure:
    {
        "states": ["q0", "q1", "q2"],
        "alphabet": ["a", "b"],
        "transitions": {
            "(q0, 'a')": {"q0": 0.5, "q1": 0.5},
            "(q0, 'b')": {"q0": 1.0},
            "(q1, 'a')": {"q2": 1.0},
            "(q1, 'b')": {"q1": 0.7, "q2": 0.3},
            "(q2, 'a')": {"q2": 1.0},
            "(q2, 'b')": {"q2": 1.0}
        },
        "start_state": "q0",
        "accept_states": ["q2"]
    }
    where transitions are represented as a dictionary with keys as tuples (state, symbol)
    file_path: path to the JSON file
    allow_substochastic: if True, allows transitions that sum to less than 1    
    '''
    
    if hasattr(file_path, 'read'):
        # file_like is Streamlit's UploadedFile
        data = json.load(file_path)
    else:
        with open(file_path, 'r') as f:
            data = json.load(f)
    
    parsed_transitions = {}
    for key, outcomes in data['transitions'].items():
        state, symbol = key.split(",")
        parsed_transitions[(state.strip(), symbol.strip())] = outcomes
        
    return PFA(
        states=set(data['states']),
        alphabet=set(data['alphabet']),
        transitions=parsed_transitions,
        start_state=data['start_state'],
        accept_states=set(data['accept_states']),
        allow_substochastic=allow_substochastic
    )
    
