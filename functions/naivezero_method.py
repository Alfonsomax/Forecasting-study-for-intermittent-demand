import numpy as np

def naive(y_train: np.ndarray) -> float:
    return y_train[-1]

def zero(y_train: np.ndarray) -> float:
    return 0.0




## prueba funcional
""" y = np.array([10, 0, 5, 20])
print(naive(y))  # expected: 20
print(zero(y))   # expected: 0.0 """