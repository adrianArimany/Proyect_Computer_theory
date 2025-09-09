import streamlit as st # type: ignore
import pandas as pd
import matplotlib.pyplot as plt
import time
from utils.io import load_pfa_from_json
from simulation.monte_carlo import simulate_monte_carlo
from simulation.matrix_method import simulate_matrix_method
from utils.benchmark import benchmark_pfa
from utils.benchmark_cutpoint import benchmark_cutpoint
from utils.benchmark_cutpoint import search_cut_point_words
from analysis.loop_analysis import loop_acceptance_probability_matrix, loop_acceptance_probability_montecarlo   
from utils.monte_trace import get_mc_result_with_trace
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
        
    # ---- TAB 3: Loop  ----
    with tabs[2]:
        st.header("Loop Acceptance Probability")
        st.info("Runs Matrix (exact) and Monte Carlo (approx) together. Shows a joint table and a time-complexity plot.")   

        loop_symbol = st.text_input("Loop symbol", key="loop_symbol")
        loop_k = st.slider("Number of repetitions (k)", min_value=1, max_value=100_000, value=100, step=10, key="loop_k")
        n_trial_loop = st.number_input("Monte Carlo Trials", min_value=1_000, value=10_000, step=1_000, key="n_trial_loop")

        # Prepare session state
        if "loop_history" not in st.session_state:
            st.session_state["loop_history"] = []  # list of dict rows

        if st.button("Run Loop Analysis (Matrix + Monte Carlo)", key="run_loop_both"):
        
            if not loop_symbol:
                st.warning("Please enter a loop symbol first.")
            else:
                # Matrix (Exact)
                t0 = time.perf_counter()
                mat_res = loop_acceptance_probability_matrix(pfa, loop_symbol, loop_k)
                t1 = time.perf_counter()
                if isinstance(mat_res, dict):
                    mat_prob = mat_res.get("probability", mat_res.get("p", None))
                else:
                    mat_prob = float(mat_res)
                    mat_runtime_ms = (t1 - t0) * 1000.0

                # Monte Carlo (Approx)
                t0 = time.perf_counter()
                mc_res = loop_acceptance_probability_montecarlo(pfa, loop_symbol, loop_k, n_trial=int(n_trial_loop))
                t1 = time.perf_counter()
                if isinstance(mc_res, dict):
                    mc_prob = mc_res.get("probability", mc_res.get("p", None))
                    mc_stderr = mc_res.get("stderr", None)
                else:
                    mc_prob = float(mc_res)
                    mc_stderr = None
                    mc_runtime_ms = (t1 - t0) * 1000.0

                # One-row combined result
                row = {
                    "symbol": loop_symbol,
                    "k": int(loop_k),
                    "trials": int(n_trial_loop),
                    "matrix_prob": mat_prob,
                    "mc_prob": mc_prob,
                    "mc_stderr": mc_stderr,
                    "runtime_matrix_ms": mat_runtime_ms,
                    "runtime_mc_ms": mc_runtime_ms,
                }
                st.session_state["loop_history"].append(row)

            # === Results table ===
        if st.session_state["loop_history"]:
        
            df = pd.DataFrame(st.session_state["loop_history"])
            st.subheader("Loop Acceptance Results (Matrix vs Monte Carlo)")
            st.dataframe(df, use_container_width=True)

        # === Plot: Time complexity vs k (both methods) ===
            fig, ax = plt.subplots()
            ax.plot(df["k"], df["runtime_matrix_ms"], marker="o", label="Matrix runtime (ms)")
            ax.plot(df["k"], df["runtime_mc_ms"], marker="o", label="Monte Carlo runtime (ms)")
            ax.set_xlabel("Repetitions (k)")
            ax.set_ylabel("Runtime (ms)")
            ax.set_title("Time Complexity over k")
            ax.legend()
            st.pyplot(fig)
        
else:
    st.warning("Please upload a valid PFA JSON file to begin.")
