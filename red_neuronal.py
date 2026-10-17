"""Paso 2 · Una red neuronal sencilla sobre los mismos datos, para ver capas y pesos."""
from sklearn.compose import ColumnTransformer
from sklearn.neural_network import MLPClassifier       # MLP: red neuronal de capas completamente conectadas
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler  # texto → columnas 0/1; números → misma escala


def crear_red(cols_cat, cols_num):
 prep = ColumnTransformer([
 # cada categoría se vuelve una columna 0/1
 ("cat", OneHotEncoder(handle_unknown="ignore"), cols_cat),
 # los números quedan en la misma escala
 ("num", StandardScaler(), cols_num),
 ])
 # 2 capas ocultas con ReLU
 red = MLPClassifier(hidden_layer_sizes=(32, 16), activation="relu", max_iter=1000,
random_state=42)
 # preparar → red
 return Pipeline([("prep", prep), ("red", red)])


def describir_red(red_entrenada):
 # la red dentro del Pipeline
 mlp = red_entrenada.named_steps["red"]
 # neuronas: entrada, ocultas, salida
 capas = [mlp.coefs_[0].shape[0]] + [c.shape[1] for c in mlp.coefs_]
 # pesos + sesgos aprendidos
 pesos = sum(c.size for c in mlp.coefs_) + sum(b.size for b in mlp.intercepts_)
 return capas, int(pesos)  # convertir a int para que se vea bonito en la salida