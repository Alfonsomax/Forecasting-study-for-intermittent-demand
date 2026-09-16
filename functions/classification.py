import numpy as np

ADI_THRESHOLD = 1.32
CV2_THRESHOLD = 0.49


def adi(y: np.ndarray) -> float:
    n = len(y)
    n_d = np.count_nonzero(y)
    if n_d == 0:
        return np.inf
    return n / n_d


def cv2(y: np.ndarray) -> float:
    nz = y[y != 0]
    if len(nz) < 2:
        return np.nan
    return float((np.std(nz, ddof=1) / np.mean(nz)) ** 2)


def classify_sbc(y: np.ndarray) -> str:
    a = adi(y)
    c = cv2(y)

    if np.isnan(c):
        return "Not enough data"

    if a < ADI_THRESHOLD and c < CV2_THRESHOLD:
        return "Smooth"
    if a < ADI_THRESHOLD and c >= CV2_THRESHOLD:
        return "Erratic"
    if a >= ADI_THRESHOLD and c < CV2_THRESHOLD:
        return "Intermittent"
    return "Lumpy"



## prueba funcional
""" y_smooth = np.array([10, 11, 9, 10, 12, 11, 10, 9])  # demanda constante, sin ceros
y_lumpy = np.array([0, 0, 0, 0, 50, 0, 0, 0, 0, 5, 0, 0, 0, 0, 200])  # rara y muy variable

print(adi(y_smooth), cv2(y_smooth), classify_sbc(y_smooth))  # esperado: Smooth
print(adi(y_lumpy), cv2(y_lumpy), classify_sbc(y_lumpy))     # esperado: Lumpy """