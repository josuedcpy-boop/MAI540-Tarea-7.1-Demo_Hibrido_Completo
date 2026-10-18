"""Comandos reutilizables del proyecto.  Uso:  python tareas.py evaluar | auditar | probar | auditar_vivienda | auditar_explicaciones"""
import subprocess
import sys

import pandas as pd
from sklearn.model_selection import cross_val_score, StratifiedKFold   # validación cruzada (Clase 6)

from datos import cargar_datos, VIVIENDA
from predictor import entrenar_predictor


def evaluar():
    """Exactitud del predictor con validación cruzada de 5 pliegues."""
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OrdinalEncoder
    X, y, cols_cat, _ = cargar_datos()
    prep = ColumnTransformer([("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), cols_cat)], remainder="passthrough")
    pipe = Pipeline([("prep", prep), ("modelo", RandomForestClassifier(n_estimators=200, random_state=42))])
    scores = cross_val_score(pipe, X, y, cv=StratifiedKFold(5, shuffle=True, random_state=42))
    print(f"Exactitud: {scores.mean():.3f} ± {scores.std():.3f}")


def auditar():
    """Exactitud por rango de edad, sobre los casos de prueba."""
    predictor, X_pru, y_pru = entrenar_predictor()
    acierto = predictor.predict(X_pru) == y_pru.values
    rango = pd.cut(X_pru["age"], [0, 25, 35, 50, 100], labels=["hasta 25", "26-35", "36-50", "más de 50"])
    print(X_pru.assign(acierto=acierto, edad=rango).groupby("edad", observed=True)["acierto"]
          .agg(exactitud="mean", casos="count").round(2))


def auditar_vivienda():
    """Exactitud por tipo de vivienda, sobre los casos de prueba."""
    predictor, X_pru, y_pru = entrenar_predictor()
    acierto = predictor.predict(X_pru) == y_pru.values
    vivienda = X_pru["housing"].map(VIVIENDA)
    print(X_pru.assign(acierto=acierto, vivienda=vivienda).groupby("vivienda", observed=True)["acierto"]
          .agg(exactitud="mean", casos="count").round(2))


def probar():
    """Ejecuta las pruebas automáticas."""
    sys.exit(subprocess.call([sys.executable, "-m", "pytest", "-q"]))


def auditar_explicaciones(n=12):
    """Genera explicaciones reales y muestra solo las que rechazan las dos reglas nuevas
    (coherencia con los datos de la solicitud, y tono en la banda media 30%-60%)."""
    from datos import datos_legibles
    from explicador import cargar_modelo_lenguaje, explicar, recortar_a_oracion
    from predictor import probabilidad_malo
    from verificador import verificar_coherencia_datos, verificar_tono_medio

    predictor, X_pru, y_pru = entrenar_predictor()
    print("Cargando el modelo de lenguaje...")
    tokenizador, modelo = cargar_modelo_lenguaje()

    encontradas = 0
    for i in range(n):
        datos = datos_legibles(X_pru.iloc[i])
        prob = probabilidad_malo(predictor, X_pru, i)
        texto = recortar_a_oracion(explicar(tokenizador, modelo, datos, prob))
        solo_nuevas = verificar_coherencia_datos(texto, datos) + verificar_tono_medio(texto, prob)
        if solo_nuevas:
            encontradas += 1
            print(f"\n--- Solicitud {i + 1} | probabilidad: {prob:.0%} ---")
            print("Texto:", texto)
            print("Rechazada por reglas nuevas:", "; ".join(solo_nuevas))

    print(f"\n{encontradas} de {n} solicitudes fallaron por las reglas nuevas.")


COMANDOS = {"evaluar": evaluar, "auditar": auditar, "auditar_vivienda": auditar_vivienda, "probar": probar,
            "auditar_explicaciones": auditar_explicaciones}

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in COMANDOS:
        sys.exit("Uso: python tareas.py " + " | ".join(COMANDOS))
    COMANDOS[sys.argv[1]]()
