
from analysis.loop_analysis import loop_acceptance_probability_montecarlo   


def get_mc_result_with_trace(pfa, symbol, k, n_trial):
        """
        Tries loop_acceptance_probability_montecarlo(..., return_trace=True).
        If not supported, falls back to no-trace and returns CI bands info instead.
        """
        import time
        t0 = time.perf_counter()
        trace = None
        stderr = None

        # Try: your function might support return_trace=True
        try:
            mc_res = loop_acceptance_probability_montecarlo(
                pfa, symbol, k, n_trial=n_trial, return_trace=True
            )
            # Expecting mc_res like {"probability": p_hat, "stderr": se?, "trace": [...] }  (be flexible)
            p_hat = mc_res.get("probability", mc_res.get("p", None))
            stderr = mc_res.get("stderr", None)
            trace = mc_res.get("trace", None)
        except TypeError:
            # Older signature—no return_trace kw
            mc_res = loop_acceptance_probability_montecarlo(
                pfa, symbol, k, n_trial=n_trial
            )
            # Could be float or dict
            if isinstance(mc_res, dict):
                p_hat = mc_res.get("probability", mc_res.get("p", None))
                stderr = mc_res.get("stderr", None)
            else:
                p_hat = float(mc_res)

        t1 = time.perf_counter()
        runtime = (t1 - t0) * 1000.0  # ms
        return {"probability": p_hat, "stderr": stderr, "trace": trace, "runtime_ms": runtime}
