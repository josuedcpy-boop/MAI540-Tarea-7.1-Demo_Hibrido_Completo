"""Paso 4 · Verificar la capa generativa: que el texto no afirme nada que el modelo no sustente."""
import re


def _numeros(texto):
    """Todos los números que aparecen en un texto, como conjunto de floats."""
    return {float(n.replace(",", ".")) for n in re.findall(r"\d+(?:[.,]\d+)?", texto)}


def verificar_numeros(texto, datos, prob):
 # datos + la probabilidad en %
 permitidos = _numeros(" ".join(str(v) for v in datos.values())) | {float(round(prob *
100))}
 # lo que sobra es inventado
 return [f"número no sustentado: {n:g}" for n in sorted(_numeros(texto) - permitidos)]


def verificar_tono(texto, prob):
 # minúsculas para comparar
 t = texto.lower()
 problemas = []
 # probabilidad baja pero dice "alto"
 if prob < 0.30 and "alto" in t:
  problemas.append("dice que el riesgo es alto, pero la probabilidad es baja")
 # probabilidad alta pero dice "bajo"
 if prob > 0.60 and "bajo" in t:
  problemas.append("dice que el riesgo es bajo, pero la probabilidad es alta")
 # certezas que el modelo no da
 for absoluta in ("garantiza", "garantizado", "sin riesgo", "seguro que", "imposible"):
  if absoluta in t:
   problemas.append(f"afirmación absoluta: '{absoluta}'")
 return problemas


def explicacion_segura(datos, prob):
 # categoría según la probabilidad
 nivel = "bajo" if prob < 0.30 else ("medio" if prob <= 0.60 else "alto")
 # los datos de la solicitud
 detalle = ", ".join(f"{k}: {v}" for k, v in datos.items())
 return f"El modelo estima una probabilidad de {prob:.0%} de que el crédito sea malo(riesgo {nivel}). Datos: {detalle}."



def verificar_explicacion(texto, datos, prob):
    """Reúne todas las verificaciones. Lista vacía = el texto se puede mostrar."""
    return verificar_numeros(texto, datos, prob) + verificar_tono(texto, prob)
