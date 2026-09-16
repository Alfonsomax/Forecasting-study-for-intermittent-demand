import numpy as np


def densify(periods: list, values: list, all_periods: list) -> np.ndarray:
    """Converts a sparse series (only periods with demand) into a
    dense vector with 0s in periods without demand, sorted by all_periods."""
    lookup = dict(zip(periods, values))
    return np.array([lookup.get(p, 0.0) for p in all_periods], dtype=float)


def run_walkforward(y: np.ndarray, methods: dict) -> dict:
    """
    y: dense vector of the entire series (sorted chronologically).
    methods: dict {method_name: function}, where each function has the signature (y_train) -> float.

    Returns a dict {method_name: {“y_real”: [...], “y_pred”: [...],
                                       “scales”: [...], “scales2”: [...]}}
    If a method fails in a fold (e.g., WMA without sufficient history),
    that fold is recorded as NaN in y_pred and does not halt the rest of the loop.
    """
    results = {name: {"y_real": [], "y_pred": [], "scales": [], "scales2": []}
               for name in methods}

    for t in range(1, len(y)):
        y_train = y[:t]
        y_real = y[t]

        scale = float(np.mean(np.abs(np.diff(y_train)))) if len(y_train) > 1 else np.nan
        scale2 = float(np.mean(np.diff(y_train) ** 2)) if len(y_train) > 1 else np.nan

        for name, func in methods.items():
            try:
                y_pred = func(y_train)
            except Exception:
                y_pred = np.nan

            results[name]["y_real"].append(y_real)
            results[name]["y_pred"].append(y_pred)
            results[name]["scales"].append(scale)
            results[name]["scales2"].append(scale2)

    return results



## prueba funcional
""" from naivezero_method import naive, zero
from wma_method import wma

y = np.array([10.0, 15.0, 0.0, 20.0, 5.0, 6.0, 6.0])
methods = {"naive": naive, "zero": zero, "wma": wma}

results = run_walkforward(y, methods)

print(results["wma"]) """