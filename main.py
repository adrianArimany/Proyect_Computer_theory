import core.pfa as pfa


if __name__ == "__main__":
    states = {'q1', 'q2'}
    alphabet = ['a']
    transitions = {('q1', 'a'): {'q1': 0.5, 'q2': 0.5},
                       ('q2', 'a'): {'q1': 0.3, 'q2': 0.7}}
    start_state = 'q1'
    accept_states = {'q2'}
    
    pfa = pfa.PFA(states, alphabet, transitions, start_state, accept_states)
    
    result = pfa.simulate('aaaa', n=10000)
    print(f"Acceptance Rate: {result[0]}, Average Probability: {result[1]}")
    