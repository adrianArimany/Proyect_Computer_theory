import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.io import load_pfa_from_json
from simulation.monte_carlo import simulate_monte_carlo
from simulation.matrix_method import simulate_matrix_method
from utils.benchmark import benchmark_pfa
from utils.benchmark_cutpoint import benchmark_cutpoint
from utils.benchmark_cutpoint import search_cut_point_words
from utils.benchmark_loop import benchmark_loop
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
            
        #This is if the user wants to search for words within a cutpoint or interval without specifying a word.    
        st.subheader("Search Words by Cut-point or Interval")
        
        colA, colB = st.columns(2)
        with colA:
            threshold_search = st.number_input("Cut-point threshold", 0.0, 1.0, 0.5, key="cp_threshold")
        with colB:
            interval_low = st.number_input("Interval low", 0.0, 1.0, 0.0, key="cp_low")
            interval_high = st.number_input("Interval high", 0.0, 1.0, 1.0, key="cp_high")
        
        max_length = st.number_input("Max word length", min_value=1, max_value=10, value=3, step=1, key="cp_maxlen")
        time_limit = st.number_input("Time limit (seconds)", 1, 60, 10, key="cp_timelimit")
    
        df_results, timing = pd.DataFrame(), {}
        
        if st.button("Search all Cut-points"):
            df_results, timing = search_cut_point_words(
            pfa,
            max_length=max_length,
            threshold=threshold_search if interval_low == interval_high else None,
            interval=(interval_low, interval_high) if interval_low < interval_high else None,
            n_trial=n_trial_cut,
            time_limit=time_limit
        )

    if not df_results.empty:
        st.success(f"Found {len(df_results)} words within criteria")
        st.dataframe(df_results, use_container_width=True)

        # runtime comparison plot
        fig, ax = plt.subplots()
        ax.bar(["Monte Carlo", "Matrix"], [timing["Monte Carlo"], timing["Matrix Product"]],
               color=["red", "blue"])
        ax.set_ylabel("Total Time (s)")
        ax.set_title("Runtime to find matching words")
        st.pyplot(fig)
    else:
        st.warning("No words found within the given cut-point/interval and time limit.")
        
    # ---- TAB 3: Loop Return ----
    with tabs[2]:
        st.header("Loop Return Probability")
        st.info("Currently only supports single-symbol loops, and ")
        loop_symbol = st.text_input("Loop symbol", key="loop_symbol")
        loop_state = st.text_input("Loop state", key="loop_state")
        loop_k = st.number_input("Steps (k)", min_value=1, value=5, key="loop_k")
        
        if st.button("Run Loop Analysis"):
            if loop_symbol and loop_state:
                df = benchmark_loop(pfa, loop_symbol, loop_state, loop_k)
                if "loop_history" not in st.session_state:
                    st.session_state["loop_history"] = pd.DataFrame()
                st.session_state["loop_history"] = pd.concat(
                    [st.session_state["loop_history"], df], ignore_index=True
                )
            else:
                st.warning("Please provide both loop symbol and state.")
        
        if "loop_history" in st.session_state and not st.session_state["loop_history"].empty:
            st.subheader("Loop Return Results")
            st.dataframe(st.session_state["loop_history"], use_container_width=True)

            # Plot: probability vs steps
            fig, ax = plt.subplots()
            for state in st.session_state["loop_history"]["State"].unique():
                state_df = st.session_state["loop_history"][
                    st.session_state["loop_history"]["State"] == state
                ]
                ax.plot(state_df["Steps (k)"], state_df["Return Probability"],
                    marker="o", label=f"State {state}")
            ax.set_xlabel("Steps (k)")
            ax.set_ylabel("Return Probability")
            ax.set_title("Loop Return Probability over Steps")
            ax.legend()
            st.pyplot(fig)
        else:
            st.info("No loop within this transitions")
        
        
else:
    st.warning("Please upload a valid PFA JSON file to begin.")
