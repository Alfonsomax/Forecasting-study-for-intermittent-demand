import numpy as np


def densify(periods: list, values: list, all_periods: list) -> np.ndarray:
    """Converts a sparse series (only periods with demand) into a
    dense vector with 0s in periods without demand, sorted by all_periods."""
    lookup = dict(zip(periods, values))
    return np.array([lookup.get(p, 0.0) for p in all_periods], dtype=float)


def round_forecast(value: float) -> float:
    """Round the forecast to whole units (you cannot ship half a piece).
    - If the value is 0, it remains 0.
    - If it rounds to 0 but the original value was > 0 (0.1 to 0.5), it is rounded up to 1.
    - NaN is left as is (folds without sufficient historical data, e.g., annual WMA)."""
    if np.isnan(value):
        return value
    if value <= 0:
        return 0.0
    rounded = np.floor(value + 0.5)   # redondeo comercial (half-up)
    if rounded == 0:
        rounded = 1.0
    return float(rounded)


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
                y_pred = round_forecast(func(y_train))
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