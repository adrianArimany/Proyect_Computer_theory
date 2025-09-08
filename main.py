import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.io import load_pfa_from_json
from simulation.monte_carlo import simulate_monte_carlo
from simulation.matrix_method import simulate_matrix_method
from utils.benchmark import benchmark_pfa
from utils.benchmark_cutpoint import benchmark_cutpoint
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
        st.markdown(f"States: {pfa.states}")
        st.markdown(f"Alphabet: {pfa.alphabet}")
        st.markdown(f"Start State: {pfa.start_state}")
        st.markdown(f"Accept States: {pfa.accept_states}")
        
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

    if "benchmark_history" not in st.session_state:
        st.session_state["benchmark_history"] = pd.DataFrame()
    
    
    # ---- TAB 1: Evaluate Word ----
    with tabs[0]:
        st.header("Evaluate a Specific Word")
        #method = st.radio("Simulation Method", ["Monte Carlo", "Matrix"], horizontal=True)
        word = st.text_input("Input Word")
        n_trial = st.number_input("Monte Carlo Trials", value=100000, step=1000, key = 'n_trial_eval')

        if st.button("Run Evaluation"):
            if word:
                mc_result = simulate_monte_carlo(pfa, word, n_trial=n_trial)
                mm_result = simulate_matrix_method(pfa, word)
                
                #Debugging info
                if isinstance(mc_result, float):
                    mc_result = {"acceptance_probability": mc_result}
                elif "acceptance_probability" not in mc_result:
                    raise ValueError(f"Unexpected Monte Carlo result format: {mc_result}")
                
                df = benchmark_pfa(pfa, [word], n_trial=n_trial)
                
                
                st.session_state["benchmark_history"] = pd.concat(
                    [st.session_state["benchmark_history"], df], ignore_index=True
                )
                               
        if not st.session_state["benchmark_history"].empty and 'df' in locals():
            st.subheader("Benchmark Results")
            
            def highlight_methods(row):
                if row["Method"] == "Monte Carlo":
                    return ['background-color: #ffcccc'] * len(row)
                elif row["Method"] == "Matrix Product":
                    return ['background-color: #cce5ff'] * len(row)
                else:
                    return [''] * len(row)
            
            styled_df = st.session_state["benchmark_history"].style.apply(highlight_methods, axis=1)
            
            st.dataframe(styled_df, use_container_width=True)
            
            st.subheader("Monte Carlo vs Matrix Method Comparison")
            df_pivot = st.session_state["benchmark_history"].pivot_table(
                index="Word", columns="Method", values="Probability"
            ).dropna()
            
            if not df_pivot.empty:
                fig, ax = plt.subplots()
                ax.scatter(df_pivot["Monte Carlo"], df_pivot["Matrix Product"], color='blue')
                ax.plot([0, 1], [0, 1], 'r--', label='Perfect Agreement')
                ax.set_xlabel("Monte Carlo Probability")
                ax.set_ylabel("Matrix Product Probability")
                ax.set_title("Monte Carlo vs Matrix Product Probability")
                ax.legend()
                st.pyplot(fig)
            else:
                st.info("Not enough data for comparison plot.")     
            
                
    # ---- TAB 2: Cut-point ----
    with tabs[1]:
        st.header("Cut-point Analysis")
        #method_cut = st.radio("Method", ["Monte Carlo", "Matrix"], horizontal=True)
        word_cut = st.text_input("Word for cut-point test")
        threshold = st.slider("Cut-point threshold", 0.0, 1.0, 0.5)
        n_trial_cut = st.number_input("Monte Carlo Trials", value=100000, step=1000, key="n_trial_cut")

        
        if st.button("Run Cut-point Test"):
            if word_cut:
                df = benchmark_cutpoint(pfa, word_cut, threshold=threshold, n_trial=n_trial_cut)
                st.session_state["benchmark_history"] = pd.concat(
                    [st.session_state["benchmark_history"], df], ignore_index=True
                )
                               
        if not st.session_state["benchmark_history"].empty and 'df' in locals():
            st.subheader("Benchmark Results")
            
            def highlight_methods(row):
                if row["Method"] == "Monte Carlo":
                    return ['background-color: #ffcccc'] * len(row)
                elif row["Method"] == "Matrix Product":
                    return ['background-color: #cce5ff'] * len(row)
                else:
                    return [''] * len(row)
            
            styled_df = st.session_state["benchmark_history"].style.apply(highlight_methods, axis=1)
            
            st.dataframe(styled_df, use_container_width=True)
            
            st.subheader("Monte Carlo vs Matrix Method Comparison")
            df_pivot = st.session_state["benchmark_history"].pivot_table(
                index="Word", columns="Method", values="Probability"
            ).dropna()
            
    # ---- TAB 3: Loop Return ----
    with tabs[2]:
        st.header("Loop Return Probability")
        symbol = st.text_input("Loop symbol")
        state = st.text_input("Loop state")
        k = st.number_input("Steps (k)", min_value=1, value=5, key="k_steps")

        if st.button("Run Loop Analysis"):
            if symbol and state:
                prob = loop_retun_probability(pfa, symbol, state, k)
                st.write(f"Return probability to '{state}' after {k} steps on '{symbol}': {prob:.5f}")
            else:
                st.warning("Specify both a symbol and a state.")

else:
    st.warning("Please upload a valid PFA JSON file to begin.")
