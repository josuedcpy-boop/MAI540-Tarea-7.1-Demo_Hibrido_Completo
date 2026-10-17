"""Paso 3 · El componente generativo: un modelo de lenguaje pequeño que redacta la explicación."""
import warnings

import torch                                                    # torch: ejecuta el modelo
from transformers import AutoModelForCausalLM, AutoTokenizer    # carga el modelo y su tokenizador
from transformers.utils import logging

warnings.filterwarnings("ignore")                               # oculta avisos que no afectan el resultado
logging.set_verbosity_error()

MODELO = "Qwen/Qwen2.5-0.5B-Instruct"                           # modelo pequeño (0.5 mil millones de parámetros)
SISTEMA = ("Eres un asistente de un banco. Explicas en español, en máximo dos frases, el resultado de un modelo de "
           "riesgo de crédito. Usa solo los datos que te dan y no inventes nada.")


def cargar_modelo_lenguaje():
 # convierte texto a números y de vuelta
 tokenizador = AutoTokenizer.from_pretrained(MODELO)
 # .eval(): solo vamos a generar
 modelo = AutoModelForCausalLM.from_pretrained(MODELO, torch_dtype=torch.float32).eval()
 return tokenizador, modelo


def explicar(tokenizador, modelo, datos, prob):
 # los datos como una línea de texto
 detalle = ", ".join(f"{k}: {v}" for k, v in datos.items())
 mensajes = [
 # las reglas del asistente
 {"role": "system", "content": SISTEMA},
 {"role": "user", "content": f"Datos: {detalle}. Probabilidad de crédito malo: {prob:.0%}. Explica."},
 ]
 # formato de chat
 texto = tokenizador.apply_chat_template(mensajes, tokenize=False,
add_generation_prompt=True)
 # texto → tensores
 entrada = tokenizador(texto, return_tensors="pt")
 # no entrenamos: solo generamos
 with torch.no_grad():
     salida = modelo.generate(**entrada, max_new_tokens=70, do_sample=False,
temperature=None, top_p=None, top_k=None)
 # solo lo que generó (no el mensaje)
 nuevos = salida[0][entrada["input_ids"].shape[1]:]
 # tensores → texto
 return tokenizador.decode(nuevos, skip_special_tokens=True).strip()



def recortar_a_oracion(texto):
    """Si el modelo se quedó sin espacio a mitad de frase, deja solo las oraciones completas."""
    if texto.endswith((".", "!", "?")):
        return texto
    corte = max(texto.rfind("."), texto.rfind("!"), texto.rfind("?"))                # último punto de cierre
    return texto[:corte + 1] if corte > 0 else texto
