"""Paso 1 · El modelo predictivo: el Random Forest de la Clase 6, entrenado y listo para dar probabilidades."""
from sklearn.compose import ColumnTransformer           # aplica una transformación solo a ciertas columnas
from sklearn.ensemble import RandomForestClassifier     # el modelo de conjunto de la Clase 6
from sklearn.model_selection import train_test_split    # separa datos de entrenamiento y de prueba
from sklearn.pipeline import Pipeline                   # encadena preparación y modelo
from sklearn.preprocessing import OrdinalEncoder        # convierte texto en números

from datos import cargar_datos


def entrenar_predictor():
 X, y, cols_cat, cols_num = cargar_datos()
 # 85% entrena, 15% se guarda
 X_ent, X_pru, y_ent, y_pru = train_test_split(X, y, test_size=0.15, stratify=y,
random_state=42)
 # texto → número; categoría nueva → -1
 codificador = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
 # codifica solo el texto
 prep = ColumnTransformer([("cat", codificador, cols_cat)], remainder="passthrough")
 # 150 árboles que votan
 modelo = RandomForestClassifier(n_estimators=150, random_state=42)
 # preparar + modelo, entrenado
 predictor = Pipeline([("prep", prep), ("modelo", modelo)]).fit(X_ent, y_ent)
 return predictor, X_pru, y_pru


def probabilidad_malo(predictor, X, indice):
 # una fila como tabla (el doble corchete conserva el formato)
 fila = X.iloc[[indice]]
 # columna 1 = probabilidad de la clase "malo"
 return float(predictor.predict_proba(fila)[0, 1])

