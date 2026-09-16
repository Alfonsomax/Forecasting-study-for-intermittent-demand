import numpy as np

WEIGHTS = [0.6, 0.2, 0.1, 0.1]  # del más reciente al más antiguo

def wma(y_train: np.ndarray, weights=WEIGHTS) -> float:
    window = y_train[-len(weights):][::-1]  # más reciente primero
    return float(np.dot(window, weights))



## prueba funcional
""" y = np.array([10, 0, 5, 20])
print(wma(y))  # esperado: 14.0 """