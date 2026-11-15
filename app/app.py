"""Kairox AI — app web (Streamlit). Flujo de 2 pasos en una sola página: 1 Datos -> 2 Resultado."""
import html
import sys
import time
from pathlib import Path

# La app agrega src/ a sys.path (no se usa pip install -e .)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402
import streamlit as st  # noqa: E402

from kairox import ejemplos, modelo  # noqa: E402
from kairox.explicacion import explicar  # noqa: E402
from kairox.indicadores import (  # noqa: E402
    CIFRAS_BALANCE, CIFRAS_ENTRADA, CIFRAS_RESULTADOS, ETIQUETAS_CIFRAS, INDICADORES,
    VARIABLES_MODELO, calcular_variables)
from kairox.validaciones import leer_csv, validar_cifras  # noqa: E402

st.set_page_config(page_title="Kairox AI", page_icon="📈", layout="centered")


@st.cache_resource
def modelo_cargado():
    return modelo.cargar_modelo()


# ----------------------------------------------------------------------------- estilo
CSS = """
<style>
:root{--prim:#5B3DB5;--prim-h:#47299A;--acento:#8A64DB;--f1:#EDE6FB;--f2:#F1ECFB;--f3:#F8F5FE;
--b1:#E9E1F8;--b2:#CDBEF0;--txt:#1B1340;--t2:#4A4568;--t3:#5A5578;--t4:#6B6688;}
html,body,[class*="css"]{font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:var(--txt);}
.block-container{max-width:860px;padding-top:2rem;padding-bottom:3rem;}
.kx-num,.kx-mono{font-family:ui-monospace,SFMono-Regular,Consolas,"Liberation Mono",monospace;}
.kx-cab h1{font-size:2.1rem;font-weight:800;color:var(--acento);margin:0;letter-spacing:-.5px;}
.kx-cab p{color:var(--t2);margin:.2rem 0 1rem;}
.kx-card{background:#fff;border:1px solid var(--b1);border-radius:22px;padding:1.1rem 1.3rem;margin:.6rem 0;}
.kx-alcance{background:var(--f2);border:1px solid var(--b2);border-radius:20px;padding:1rem 1.2rem;
  color:var(--t2);font-size:.95rem;line-height:1.5;}
.kx-paso{font-weight:800;color:var(--prim);font-size:1.25rem;margin:1.6rem 0 .3rem;}
.kx-paso span{background:var(--prim);color:#fff;border-radius:999px;padding:.05rem .6rem;margin-right:.5rem;font-size:1rem;}
.kx-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:.6rem;}
.kx-ind{background:#fff;border:1px solid var(--b1);border-radius:14px;padding:.55rem .75rem;}
.kx-ind small{display:block;color:var(--t3);font-size:.78rem;}
.kx-ind b{font-size:1.05rem;}
.kx-aviso{background:#FFF6DC;border:1px solid #F1DFA3;color:#5C4707;border-radius:14px;padding:.55rem .8rem;margin:.3rem 0;font-size:.92rem;}
.kx-bloqueo{background:#FBE3E8;border:1px solid #A12A47;color:#8E1F3A;border-radius:14px;padding:.55rem .8rem;margin:.3rem 0;font-size:.92rem;font-weight:600;}
.kx-res{display:flex;flex-wrap:wrap;gap:1.4rem;align-items:center;}
.kx-anillo{width:172px;height:172px;border-radius:50%;display:grid;place-items:center;flex:none;
  background:conic-gradient(var(--c) var(--p),#E9E1F8 0);}
.kx-anillo-i{width:134px;height:134px;border-radius:50%;background:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;}
.kx-puntaje{font-size:2.4rem;font-weight:800;line-height:1;}
.kx-anillo-i small{color:var(--t3);font-size:.78rem;margin-top:.25rem;}
.kx-etq{display:inline-block;border-radius:999px;padding:.3rem .9rem;font-weight:800;font-size:1.05rem;}
.kx-riesgo{background:#FBE3E8;color:#8E1F3A;} .kx-viable{background:#DDF3E1;color:#17612F;}
.kx-barra{position:relative;height:14px;border-radius:999px;background:#E9E1F8;margin:2.2rem 0 .3rem;}
.kx-barra i{position:absolute;left:0;top:0;bottom:0;border-radius:999px;}
.kx-marca{position:absolute;left:50%;top:-8px;bottom:-8px;width:2px;background:var(--txt);}
.kx-marca b{position:absolute;top:-22px;left:50%;transform:translateX(-50%);font-size:.78rem;white-space:nowrap;}
.kx-esc{display:flex;justify-content:space-between;color:var(--t4);font-size:.78rem;}
.kx-fila{display:flex;justify-content:space-between;gap:1rem;border-bottom:1px solid var(--b1);padding:.45rem 0;flex-wrap:wrap;}
.kx-fila:last-child{border-bottom:none;}
.kx-sube{color:#8E1F3A;font-weight:700;} .kx-baja{color:#17612F;font-weight:700;} .kx-sin{color:var(--t4);}
.kx-nota{color:var(--t3);font-size:.85rem;}
.stButton>button,.stDownloadButton>button{min-height:44px;border-radius:12px;font-weight:700;}
.stButton>button[kind="primary"]{background:var(--prim);border-color:var(--prim);}
.stButton>button[kind="primary"]:hover{background:var(--prim-h);border-color:var(--prim-h);}
.stButton>button:disabled{background:#CDBEF0;border-color:#CDBEF0;color:#4A4568;opacity:1;cursor:not-allowed;}
div[data-baseweb="input"] input,div[data-baseweb="base-input"] input{min-height:44px;}
div[data-baseweb="tab-list"] button{min-height:44px;}
*:focus-visible{outline:3px solid var(--acento)!important;outline-offset:2px;}
@media (max-width:640px){div[data-baseweb="tab-list"] button{padding-left:.5rem;padding-right:.5rem;}
div[data-baseweb="tab-list"] button p{font-size:.85rem;}.kx-cab h1{font-size:1.7rem;}.kx-anillo{margin:0 auto;}.block-container{padding-left:1rem;padding-right:1rem;}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def esc(texto):
    return html.escape(str(texto))


def fmt(valor):
    """Formato de una cifra o indicador; '—' si falta el dato."""
    if valor is None or (isinstance(valor, float) and np.isnan(valor)):
        return "—"
    v = float(valor)
    if v == 0:
        return "0"
    if abs(v) >= 100:
        return f"{v:,.1f}"
    if abs(v) >= 0.001:
        return f"{v:.3f}"
    return f"{v:.2e}"


# ----------------------------------------------------------------------------- estado
ESTADO = st.session_state
for clave, defecto in {"origen": "Ninguna", "caso": None, "base": None, "analizado": False,
                       "archivo_id": None, "mensajes_csv": []}.items():
    ESTADO.setdefault(clave, defecto)
for _k in CIFRAS_ENTRADA:
    ESTADO.setdefault(f"in_{_k}", None)


def _poner_cifras(cifras):
    for k in CIFRAS_ENTRADA:
        v = cifras.get(k)
        ESTADO[f"in_{k}"] = None if v is None or (isinstance(v, float) and np.isnan(v)) else float(v)


def cargar_ejemplo(indice):
    """Un clic: carga las 16 cifras del caso y lo analiza."""
    fila = ejemplos.cargar_ejemplos().iloc[indice]
    cifras = ejemplos.cifras_de(fila)
    _poner_cifras(cifras)
    ESTADO.update(origen=f"Empresa de ejemplo ({fila['tipo']})", base=dict(cifras), analizado=True,
                  caso={"tipo": fila["tipo"], "riesgo_real": int(fila["riesgo_real"]),
                        "empresa": fila["empresa"], "anio": int(fila["anio"])})


def limpiar():
    _poner_cifras({})
    ESTADO.update(origen="Ninguna", caso=None, base=None, analizado=False, mensajes_csv=[])


def pedir_analisis():
    ESTADO["analizado"] = True


# ----------------------------------------------------------------------------- cabecera
st.markdown('<div class="kx-cab"><h1>Kairox AI</h1>'
            '<p>Clasificación de viabilidad de inversión a partir de indicadores financieros.</p></div>',
            unsafe_allow_html=True)
st.markdown(
    '<div class="kx-alcance"><b>Para qué sirve y para qué no.</b> Responde una sola pregunta: si la empresa '
    'es un destino viable para el capital o presenta riesgo crítico. Requiere cifras de al menos un ejercicio '
    'contable completo, en millones de dólares, y supone que la información es veraz (no detecta manipulación '
    'contable). No define el monto, el momento de entrada ni el tipo de instrumento, y no reemplaza el análisis '
    'financiero ni el criterio de quien decide.</div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------------- paso 1
st.markdown('<div class="kx-paso"><span>1</span>Datos de la empresa</div>', unsafe_allow_html=True)
tab_ej, tab_arch, tab_man = st.tabs(["Empresa de ejemplo", "Subir archivo", "Ingresar manualmente"])

with tab_ej:
    st.caption("Un clic, sin escribir nada: tres casos reales del conjunto de prueba.")
    casos = ejemplos.cargar_ejemplos()
    for i, fila in casos.iterrows():
        st.button(f"{fila['tipo'].capitalize()} — {fila['empresa']}, {int(fila['anio'])}",
                  key=f"ej_{i + 1}", on_click=cargar_ejemplo, args=(i,), use_container_width=True)

with tab_arch:
    st.caption("CSV con las 16 cifras de la empresa, en millones de dólares (solo se usa la primera fila).")
    st.download_button("Descargar plantilla CSV", data=ejemplos.contenido_plantilla(),
                       file_name="plantilla_empresa.csv", mime="text/csv", key="descarga_plantilla")
    archivo = st.file_uploader("Archivo CSV", type=["csv"], key="subida")
    if archivo is not None and ESTADO["archivo_id"] != archivo.file_id:
        cifras_csv, mensajes = leer_csv(archivo)
        _poner_cifras(cifras_csv)
        ESTADO.update(origen=f"Archivo ({archivo.name})", base=None, caso=None, analizado=False,
                      archivo_id=archivo.file_id, mensajes_csv=mensajes)
    for m in ESTADO["mensajes_csv"]:
        st.markdown(f'<div class="kx-aviso">{esc(m)}</div>', unsafe_allow_html=True)

with tab_man:
    st.caption("Cifras del balance y de resultados, en millones de dólares. Un campo vacío es un dato faltante.")
    for titulo, claves in (("Balance general", CIFRAS_BALANCE), ("Estado de resultados", CIFRAS_RESULTADOS)):
        st.markdown(f"**{titulo}**")
        c1, c2 = st.columns(2)
        for n, clave in enumerate(claves):
            with (c1 if n % 2 == 0 else c2):
                etiqueta = ETIQUETAS_CIFRAS[clave]
                if clave == "ingresos_totales":
                    etiqueta += " (equivale a ventas netas)"
                st.number_input(etiqueta, value=None, format="%.4f", key=f"in_{clave}")
    st.button("Limpiar cifras", key="limpiar", on_click=limpiar)

# Cifras activas = campos manuales (fuente única de verdad)
cifras = {k: ESTADO.get(f"in_{k}") for k in CIFRAS_ENTRADA}
editado = ESTADO["base"] is not None and any(cifras[k] != ESTADO["base"][k] for k in CIFRAS_ENTRADA)
st.markdown(f'<p class="kx-nota">Origen de las cifras: <b>{esc(ESTADO["origen"])}</b>'
            f'{" (modificadas)" if editado else ""}</p>', unsafe_allow_html=True)

variables = calcular_variables(cifras)
st.markdown("#### Indicadores calculados")
tarjetas = "".join(
    f'<div class="kx-ind"><small>{esc(INDICADORES[v][0])}</small>'
    f'<b class="kx-num">{fmt(variables.iloc[0][v])}</b></div>' for v in VARIABLES_MODELO)
st.markdown(f'<div class="kx-grid">{tarjetas}</div>', unsafe_allow_html=True)
st.markdown('<p class="kx-nota">Un indicador sin dato (—) se reemplaza con la mediana del entrenamiento. '
            'Los valores extremos se recortan a los percentiles 1 % y 99 % observados al entrenar. '
            'Si es el primer año, el crecimiento de ingresos queda sin dato.</p>', unsafe_allow_html=True)

validacion = validar_cifras(cifras)
for b in validacion["bloqueos"]:
    st.markdown(f'<div class="kx-bloqueo">{esc(b)}</div>', unsafe_allow_html=True)
for a in validacion["avisos"]:
    st.markdown(f'<div class="kx-aviso">{esc(a)}</div>', unsafe_allow_html=True)

st.button("Analizar empresa", key="analizar", type="primary", on_click=pedir_analisis,
          disabled=bool(validacion["bloqueos"]), use_container_width=True)

# ----------------------------------------------------------------------------- paso 2
if ESTADO["analizado"] and not validacion["bloqueos"]:
    st.markdown('<div class="kx-paso"><span>2</span>Resultado</div>', unsafe_allow_html=True)
    pipeline, metadatos, parametros = modelo_cargado()
    t0 = time.perf_counter()
    expl = explicar(variables, pipeline, metadatos, parametros)  # incluye el puntaje de la empresa
    puntaje = expl["puntaje"]
    umbral = metadatos["umbral_decision"]
    imp = modelo.importancias(pipeline, metadatos)
    tiempo = time.perf_counter() - t0
    riesgo = bool(modelo.clasificar(puntaje, umbral))
    color = "#A12A47" if riesgo else "#17612F"
    etiqueta, clase = ("Riesgo crítico", "kx-riesgo") if riesgo else ("Inversión viable", "kx-viable")
    texto = (f"El puntaje supera el umbral de {umbral:.2f}. Conviene revisar con detalle la situación "
             "financiera antes de invertir." if riesgo else
             f"El puntaje se ubica por debajo del umbral de {umbral:.2f}. Esto no garantiza que la "
             "inversión sea segura.")
    ancho = min(max(puntaje, 0), 1) * 100
    st.markdown(
        f'<div class="kx-card"><div class="kx-res">'
        f'<div class="kx-anillo" style="--p:{ancho:.1f}%;--c:{color}"><div class="kx-anillo-i">'
        f'<span class="kx-puntaje kx-num">{puntaje:.2f}</span><small>Puntaje de riesgo</small></div></div>'
        f'<div style="flex:1;min-width:220px"><span class="kx-etq {clase}">{etiqueta}</span>'
        f'<p style="margin:.7rem 0 0">{esc(texto)}</p></div></div>'
        f'<div class="kx-barra"><i style="width:{ancho:.1f}%;background:{color}"></i>'
        f'<div class="kx-marca"><b>Umbral {umbral:.2f}</b></div></div>'
        f'<div class="kx-esc kx-num"><span>0.00</span><span>1.00</span></div></div>',
        unsafe_allow_html=True)

    caso = ESTADO["caso"]
    if caso is not None and not editado:
        st.markdown(f'<div class="kx-card"><p class="kx-nota" style="margin:0">{esc(ejemplos.rotulo(caso["tipo"]))}</p>'
                    f'<p style="margin:.3rem 0 0"><b>{esc(ejemplos.lo_que_ocurrio(caso["riesgo_real"]))}</b> '
                    f'({esc(caso["empresa"])}, {caso["anio"]}).</p></div>', unsafe_allow_html=True)
    elif caso is not None and editado:
        st.markdown('<p class="kx-nota">Las cifras fueron modificadas: el resultado ya no corresponde al '
                    'caso de ejemplo.</p>', unsafe_allow_html=True)

    st.markdown("#### Explicación individual")
    filas = ""
    for e in expl["efectos"]:
        if e["sin_dato"]:
            efecto = '<span class="kx-sin">sin dato</span>'
        elif e["direccion"] == "sin efecto":
            efecto = '<span class="kx-sin">sin efecto</span>'
        else:
            clase_e = "kx-sube" if e["efecto"] > 0 else "kx-baja"
            efecto = f'<span class="{clase_e} kx-num">{e["direccion"]} ({e["efecto"]:+.2f})</span>'
        filas += (f'<div class="kx-fila"><span>{esc(e["etiqueta"])} · valor de la empresa: '
                  f'<b class="kx-num">{fmt(e["valor"])}</b></span>{efecto}</div>')
    st.markdown(f'<div class="kx-card">{filas}<p class="kx-nota" style="margin:.6rem 0 0">'
                f'{esc(expl["nota"])}</p></div>', unsafe_allow_html=True)

    st.markdown("#### Variables que más usa el modelo")
    filas = "".join(
        f'<div class="kx-fila"><span>{esc(INDICADORES[v][0])} · valor de la empresa: '
        f'<b class="kx-num">{fmt(variables.iloc[0][v])}</b></span>'
        f'<span class="kx-num">{imp[v]:.1f} %</span></div>' for v in list(imp.index[:5]))
    st.markdown(f'<div class="kx-card">{filas}<p class="kx-nota" style="margin:.6rem 0 0">'
                'Importancia global del modelo (no es específica de esta empresa).</p></div>',
                unsafe_allow_html=True)

    st.markdown("#### Cómo leer este resultado")
    st.markdown(
        '<div class="kx-card"><ol style="margin:0;padding-left:1.2rem;line-height:1.55">'
        '<li>El puntaje indica riesgo relativo; no es la probabilidad real de que la empresa quiebre, porque '
        'SMOTE equilibra las clases y la probabilidad no está calibrada.</li>'
        '<li>Una clasificación de riesgo crítico es una alerta para revisar la empresa, no una conclusión.</li>'
        '<li>En la prueba con empresas que no vio al entrenar, el modelo detectó 4 de cada 10 observaciones de '
        'riesgo y solo una de cada siete alertas fue real (F1 0.205, lejos de la aspiración de 0.80).</li>'
        '<li>Las cifras que se ingresan se suponen veraces y completas; si faltan datos, se imputan con la '
        'mediana y el resultado es menos confiable.</li>'
        '<li>El análisis no define cuánto ni cuándo invertir, y no sustituye el criterio profesional.</li>'
        '</ol></div>', unsafe_allow_html=True)
    st.markdown(f'<p class="kx-nota">Tiempo de cálculo de la última predicción: '
                f'<b class="kx-num">{tiempo:.3f} s</b></p>', unsafe_allow_html=True)

# ----------------------------------------------------------------------------- glosario y modelo
with st.expander("Glosario de los 17 indicadores"):
    filas = "".join(
        f'<div class="kx-fila"><span><b>{esc(INDICADORES[v][0])}</b><br>'
        f'<span class="kx-mono kx-nota">{esc(INDICADORES[v][1])}</span></span>'
        f'<span style="flex:1;min-width:240px">{esc(INDICADORES[v][2])}</span></div>' for v in VARIABLES_MODELO)
    st.markdown(filas, unsafe_allow_html=True)

with st.expander("Modelo"):
    st.markdown(
        "Random Forest entrenado con 78,682 observaciones anuales de 8,971 empresas estadounidenses "
        "(1999–2018). Evaluación sobre empresas que no vio al entrenar (15,742 observaciones de 1,794 empresas), "
        "con umbral de decisión 0.50:\n\n"
        "- **F1:** 0.205 (IC 95 %: 0.170–0.238)\n"
        "- **Recall:** 0.388 (IC 95 %: 0.334–0.443)\n"
        "- **Precisión:** 0.139\n"
        "- **PR-AUC:** 0.135 (referencia sin capacidad predictiva: 0.067)\n\n"
        "La meta de F1 0.80 es una aspiración no alcanzada. El puntaje no es una probabilidad.")

st.markdown('<p class="kx-nota" style="text-align:center;margin-top:2rem">Kairox AI · Proyecto universitario '
            '(UPAO, Inteligencia Artificial: Principios y Técnicas, 2026-20)</p>', unsafe_allow_html=True)
