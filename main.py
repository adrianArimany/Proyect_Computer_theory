import streamlit as st
import pandas as pd
from utils.io import load_pfa_from_json
from simulation.monte_carlo import simulate_monte_carlo
from simulation.matrix_method import simulate_matrix_method
from utils.benchmark import benchmark_pfa
from analysis.cutpoint import estimate_cut_point
from analysis.loop_analysis import loop_retun_probability
from utils.visual import draw_pfa_diagram

st.set_page_config(layout="wide")

# -- sidebar --
st.sidebar.title("Load PFA")
json_file = st.sidebar.file_uploader("Upload PFA JSON", type="json")

st.title("Probabilistic Finite Automata Simulator")

if json_file:
    pfa = load_pfa_from_json(json_file)
    st.success("PFA successfully loaded.")

    # diagram + details
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
            with st.expander(f"Symbol: `{symbol}`"):
                st.dataframe(matrix)

    # Main functional sections
    tabs = st.tabs(["Evaluate Word", "Cut-point Analysis", "Loop Return Probability"])

    # ---- TAB 1: Evaluate Word ----
    with tabs[0]:
        st.header("Evaluate a Specific Word")
        method = st.radio("Simulation Method", ["Monte Carlo", "Matrix"], horizontal=True)
        word = st.text_input("Input Word")
        n_trial = st.number_input("Monte Carlo Trials", value=100000, step=1000)

        if st.button("Run Evaluation"):
            if word:
                if method == "Monte Carlo":
                    result = simulate_monte_carlo(pfa, word, n_trial)
                else:
                    result = simulate_matrix_method(pfa, word)
                st.json(result)

                # Benchmark both methods
                st.subheader("Benchmark")
                df = benchmark_pfa(pfa, word, n_trial=n_trial)
                st.dataframe(df)
            else:
                st.warning("Enter a valid word.")

    # ---- TAB 2: Cut-point ----
    with tabs[1]:
        st.header("Cut-point Analysis")
        word_cut = st.text_input("Word for cut-point test")
        threshold = st.slider("Cut-point threshold", 0.0, 1.0, 0.5)
        method_cut = st.radio("Method", ["Monte Carlo", "Matrix"], horizontal=True)

        if st.button("Run Cut-point Test"):
            if word_cut:
                cut = estimate_cut_point(
                    pfa, word=word_cut, method=method_cut.lower(), threshold=threshold, n_trial=n_trial
                )
                st.json(cut)
            else:
                st.warning("Enter a word for cut-point test.")

    # ---- TAB 3: Loop Return ----
    with tabs[2]:
        st.header("Loop Return Probability")
        symbol = st.text_input("Loop symbol")
        state = st.text_input("Loop state")
        k = st.number_input("Steps (k)", min_value=1, value=5)

        if st.button("Run Loop Analysis"):
            if symbol and state:
                prob = loop_retun_probability(pfa, symbol, state, k)
                st.write(f"Return probability to '{state}' after {k} steps on '{symbol}': {prob:.5f}")
            else:
                st.warning("Specify both a symbol and a state.")

else:
    st.warning("Please upload a valid PFA JSON file to begin.")
