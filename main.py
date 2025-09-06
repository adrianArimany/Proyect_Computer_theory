import streamlit as st
from utils.io import load_pfa_from_json
from simulation.monte_carlo import simulate_monte_carlo
from simulation.matrix_method import simulate_matrix_method
from utils.benchmark import benchmark_pfa
from analysis.cutpoint import estimate_cut_point
from analysis.loop_analysis import loop_retun_probability
from utils.visual import draw_pfa_diagram
import pandas as pd

st.set_page_config(layout="wide")

# -- side bar --
st.sidebar.title("load PFA")
json_file = st.sidebar.file_uploader("Upload PFA JSON", type="json")


# -- main panel --
st.title("Probabilistic Finite Automata Simulator")

if json_file:
    pfa = load_pfa_from_json(json_file)
    st.success("PFA successfully loaded.")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("PFA diagram")
        fig = draw_pfa_diagram(pfa)
        st.pyplot(fig)

    with col2:
        st.subheader("PFA Details")
        st.markdown(f"**States:** {pfa.states}")
        st.markdown(f"**Alphabet:** {pfa.alphabet}")
        st.markdown(f"**Start State:** {pfa.start_state}")
        st.markdown(f"**Accept States:** {pfa.accept_states}")
        
        st.markdown("**Transition matrices**")
        for symbol in pfa.alphabet:
            matrix = pd.DataFrame(0.0, index=sorted(pfa.states), columns=sorted(pfa.states))
            for (state, sym), targets in pfa.transitions.items():
                if sym == symbol:
                    for dest, prob in targets.items():
                        matrix.at[state, dest] = prob
            st.markdown(f"**Symbol: `{symbol}`**")
            st.dataframe(matrix)

    # Show simulation controls after PFA is loaded
    with st.sidebar:
        st.markdown("---")
        method = st.selectbox("Simulation Method", ["monte_carlo", "matrix"])
        word = st.text_input("Input Word from alphabet")
        trials = st.number_input("Number of Trials for Monte Carlo", value=100000, step=1000)


        show_cutpoint = st.checkbox("Check cut point")
        cut_threshold = st.slider("Cut point threshold", 0.0, 1.0, 0.5)


        show_loop = st.checkbox("Loop Return Probability")
        loop_symbol = st.text_input("Symbol for Loop", value="")
        loop_state = st.text_input("State for Loop", value="")
        loop_k = st.number_input("Steps (k)", min_value=1, value=5)


    if word:
        st.subheader("Method Result")
        if method == "monte_carlo":
            st.info("Monte Carlo Result")
            result = simulate_monte_carlo(pfa, word, trials)
        else:
            st.info("Matrix Result")
            result = simulate_matrix_method(pfa, word)
        st.json(result)


        st.subheader("Benchmark Monte Carlo vs Matrix")
        df = benchmark_pfa(pfa, word, n_trial=trials)
        st.dataframe(df)


        if show_cutpoint:
            st.subheader("Cut-point Analysis")
            cut = estimate_cut_point(pfa, word, method=method, threshold=cut_threshold, n_trial=trials)
            st.json(cut)


        if show_loop:
            st.subheader("Loop Return Probability")
            prob = loop_retun_probability(pfa, loop_symbol, loop_state, loop_k)
            st.write(f"Return probability to '{loop_state}' after {loop_k} steps on '{loop_symbol}': {prob:.5f}")
    else:
        st.warning("Please upload a valid PFA JSON file to begin.")