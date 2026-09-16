import numpy as np
from statsmodels.tsa.holtwinters import SimpleExpSmoothing, Holt

def ses(y_train: np.ndarray) -> float:
    model = SimpleExpSmoothing(y_train, initialization_method="estimated").fit()
    return float(model.forecast(1)[0])

def holt(y_train: np.ndarray) -> float:
    model = Holt(y_train, initialization_method="estimated").fit()
    return float(model.forecast(1)[0])





## prueba funcional
""" y = np.array([10, 20, 30, 40, 50])  # clear upward trend

print(ses(y))   # Expected: close to 50 (SES does not extrapolate the trend)
print(holt(y))  # esperado: por encima de 50 (Holt sí extrapola tendencia, ~60) """