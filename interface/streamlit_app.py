import streamlit as st
from utils.io import load_pfa_from_json
from simulation.monte_carlo import simulate_monte_carlo
from simulation.matrix_method import simulate_matrix_method
from utils.benchmark import benchmark_pfa
from analysis.cutpoint import estimate_cut_point
from analysis.loop_analysis import loop_retun_probability

# -- side bar --
st.sidebar.title("load PFA")
json_file = st.sidebar.file_uploader("Upload PFA JSON", type=["json"])

method = st.sidebar.selectbox("Simulation Method", ["monte_carlo", "matrix_method"])
word = st.sidebar.text_input("Input Word from alphabet", value=" ")
trails = st.sidebar.number_input("Number of Trials for Monte Carlo", value=100000, step=1000)

show_cutpoint = st.sidebar.checkbox("Check cut point")
cut_threshold = st.sidebar.slider("Cut point threshold", 0.0, 1.0, 0.5)

show_loop = st.sidebar.checkbox("Loop Return Probability")
loop_symbol = st.sidebar.text_input("Symbol for Loop", value="a")
loop_state = st.sidebar.text_input("State for Loop", value="q0")
loop_k = st.sidebar.number_input("Steps (k)", min_value=1, value=5)


# -- main panel --
st.title("Probabilistic Finite Automata Simulator")

if json_file:
    pfa = load_pfa_from_json(json_file)
    st.success("PFA Loaded Successfully")
    
    st.subheader("Monte Carlo Results")
    if method == "monte_carlo":
        result = simulate_monte_carlo(pfa, word, n_trial=trails)
    else:
        result = simulate_matrix_method(pfa, word)
    st.json(result)
    
    st.subheader("Benchmarking Results: Monte Carlo vs Matrix Method")
    df = benchmark_pfa(pfa, [word], n_trial=trails)
    st.dataframe(df)
    
    if show_cutpoint:
        st.subheader("Cut Point Analysis")
        cut = estimate_cut_point(pfa, word, n_traials=trails, method=method, threshold=cut_threshold)
        st.json(cut)
        
    if show_loop:
        st.subheader("Loop Return Probability")
        try:
            prob = loop_retun_probability(pfa, loop_symbol, loop_state, loop_k)
            st.write(f"Probability of returning to state '{loop_state}' after {loop_k} steps using symbol '{loop_symbol}': {prob:.6f}")
        except AssertionError as e:
            st.error(str(e))
else:
    st.warning("Please upload a valid PFA JSON file to begin.")