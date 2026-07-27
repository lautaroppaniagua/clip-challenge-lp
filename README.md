# Merchant Risk Scoring — Clip

Modelo de riesgo de fraude a nivel merchant para Clip

Dos outputs de modelo: **segmentación de riesgo** para entregar a los procesadores de
tarjeta, y **pérdida esperada** para priorización interna.

---

## 🎥 Explicación y presentación del proyecto


[![Ver el video](https://img.youtube.com/vi/mzosDtNB2WY/maxresdefault.jpg)](https://youtu.be/mzosDtNB2WY)

---

## El problema

Clip necesita identificar merchants fraudulentos por dos motivos princiaples
1. Clip afronta los pagos directamente por lo que una transaccion de fraude impacta en el negocio
2. Clip agrupa en affiliations merchants segun su nivel de riesgo y los card issuers los validan. Si la asertividad de los modelos cae, la credibilidad en Clip tambien

El dataset trae `is_suspended` como candidato obvio al target aunque explicitado en las instrucciones como NO usar en crudo.
44% de
nulos, patrón intermitente (los comercios oscilan entre suspendido y habilitado)
y solo 26 casos positivos nos da la pauta que es una metrica muy compleja de usar para la creacion de la variable objetivo es por eso que 

Se construyó un target sintético: **ratio de fraude ponderado por monto**,
binarizado en el percentil 97.

```
target = fraud_rate_tpv > P97       →  693 positivos de 23.083  (3,00%)
```

El corte por percentil no es arbitrario. Con el corte natural (`> 0`) el target
mide **exposición, no riesgo**: la prevalencia va de 1,3% en los comercios chicos
a 17,2% en los grandes, y ordenar por facturación sola alcanza AUC 0,79. El
percentil 97 corta ese sesgo.

## Resultados

| | PR-AUC | ROC-AUC |
|---|---|---|
| Modelo nulo (prevalencia) | 0,030 | 0,500 |
| Ordenar por facturación | 0,089 | 0,712 |
| Regresión logística L2 | 0,136 | 0,760 |
| **LGBM + Optuna** | **0,170** | **0,784** |

**1,9× el baseline de volumen. 5,7× el modelo nulo.** El modelo sale calibrado sin
necesidad de capa de calibración (ECE 0,0014).

### Segmentación

| segmento | merchants | tasa real de fraude | lift | % de la pérdida |
|---|---|---|---|---|
| **A · muy alto** | 4.617 | **8,73%** | 2,91× | **81,4%** |
| B · alto | 4.616 | 3,16% | 1,05× | 7,9% |
| C · medio | 4.617 | 1,65% | 0,55× | 8,7% |
| D · bajo | 4.616 | 1,02% | 0,34× | 1,6% |
| E · muy bajo | 4.617 | 0,45% | 0,15× | 0,4% |

La tasa **real** de fraude es monótona de E a A — esa es la validación de que los
tramos ordenan riesgo y no tamaño.

### Pérdida esperada

`P(riesgo) × TPV × tasa de pérdida de un positivo (4,08%)`

---

## Estructura

```
.
├── eda.ipynb              Exploración, construcción del target y features
├── model.ipynb            Modelado, evaluación y generación de entregables
├── src/
│   └── clip_palette.py    Paleta corporativa para los gráficos
├── data/                  (Ausente en el repositorio por el tamaño de los archivos)
│   ├── txn_sample.parquet                     7M transacciones
│   ├── merchant_rating_featureset_sample.parquet   panel diario 10,2M × 71
│   ├── features_v2.parquet                    ← generado por eda.ipynb
│   └── merchant_risk.parquet                  ← panel de merchants con su catalogación de riesgo
├── data/
├── ├── PROMPTS_EDA.md              Algunos modelos de prompts usados para las creaciones de los notebooks
│   ├── PROMPTS_MODEL.md
```

### El entregable

`data/merchant_risk.parquet` — una fila por comercio, 40.265 × 10:

| columna | |
|---|---|
| `merchant_id` | |
| `score_riesgo` | probabilidad (out-of-fold para el universo modelable) |
| `segmento_riesgo` | A–E |
| `perdida_esperada` | en pesos, ordenado descendente |
| `en_universo_modelo` | `false` para los que están bajo el piso de actividad |
| `industry_mcc`, `tenure_days`, `n_txn`, `tpv_total`, `tpv_fraud` | contexto |

---

## Cómo correrlo

Los parquets de entrada no están versionados por peso. Colocarlos en `data/` y:

```bash
pip install -r requirements.txt'
```

Después `eda.ipynb` (genera `features_v2.parquet`) y `model.ipynb` (genera el
entregable). El EDA usa **polars lazy** en todo el pipeline: el panel de merchants
nunca se materializa entero.

---

## Decisiones que vale la pena mirar

**Anti-leakage.** Se excluyen chargebacks, disputas y reclamos. Incluirlos lleva
el PR-AUC de 0,170 a 0,417 — y ahí el bloque se come el 61% del modelo. Un
contracargo es *consecuencia* del fraude y llega 30-120 días después: para cuando
aparece, la pérdida ya ocurrió.

**Features probadas y descartadas.** La normalización contra pares de la misma
industria (`z_peer_*`) se implementó y se sacó: 38% de nulos y decimoquinta en
importancia. El ciclo semanal daba 1,00 para todos los comercios, porque se
calculaba sobre una ventana móvil de 30 días que siempre contiene la misma
cantidad de fines de semana.


**Sin clustering.** La segmentación corta el score por percentiles. Un k-means
agruparía por parecido entre features —o sea, por tamaño— ignorando la etiqueta,
y devolvería grupos sin orden entre sí.

## Limitaciones

**`txn_sample.parquet` no tiene columna de tiempo.** No se puede alinear
temporalmente features y target, ni hacer un split train/test temporal, que es el
único válido para fraude. El modelo describe qué comercios tuvieron fraude en la
muestra; presentarlo como predicción excedería lo que los datos permiten afirmar.


**Cold start sin resolver.** Un comercio creado hoy sin transacciones recibe score
0,012 — por debajo del promedio de la cartera (3,0%), cuando los comercios de
menos de 3 meses tienen la tasa real más alta (4,17%). Requiere un modelo aparte
con atributos de alta, Por otro lado, se puede evaluar reglas heuristicas de negocio para un filtrado
mayor 


# Uso de AI

## Uso de herramientas de inteligencia artificial

Durante el desarrollo de este proyecto se utilizaron herramientas basadas en modelos de lenguaje como asistentes para acelerar distintas etapas del trabajo.

Se utilizaron principalmente para:

- Estructurar y documentar el análisis exploratorio y el pipeline de modelado.
- Generar borradores iniciales de código y refactorizar secciones repetitivas
- Proponer visualizaciones y ayudar a organizar la presentación final.
- Revisar explicaciones sobre métricas, feature engineering y reglas de negocio.
- Traducir resultados técnicos a una narrativa más clara para negocio.

Utilice en varias instancias de contexto Claude Code con skills de estadística y ciencia de datos como GPT Sol 5.6 para interpretabilidad y redacción de documentación. Por ultimo Claude Design para el desarrollo de ppts adaptadas a la imagen de Clip

No se conservaron todos los prompts exactos utilizados durante el desarrollo. Los siguientes son ejemplos reconstruidos que representan el tipo de instrucciones, contexto y restricciones proporcionadas a las herramientas:

> Analizá este dataset a nivel merchant y proponé un EDA enfocado en desbalance de clases, valores faltantes, concentración del fraude, comportamiento temporal y posibles fuentes de target leakage. NO presentes conclusiones que no estén respaldadas por evidencia calculada sobre los datos.

> Refactorizá este pipeline de feature engineering para crear únicamente variables disponibles antes de la fecha de predicción. Agrupalas en comparación contra comercios similares, comparación contra el historial propio del merchant y estabilidad o temporalidad operativa.

> Construí un modelo de clasificación con LightGBM y validación temporal. Optimizá los hiperparámetros con Optuna y compará el resultado contra una baseline  y una regresión logística utilizando curvas de PR-AUC y ROC-AUC. Todo el procesamiento y evaluacion debe realizarse con CV estratificado. Luego evalua curvas de optimizacion para calibrar la salida del modelo

> Tomando como entrada los archivos adjuntos interpreta la imagen de marca de Clip y genera un set de configuraciones que respete el patron visual para realizar plots y visualizaciones en matplotlib

Las herramientas de IA generaron propuestas, borradores y alternativas iniciales. Sin embargo, las siguientes decisiones y validaciones fueron realizadas manualmente:

- Definición y validación de la variable objetivo.
- Identificación y exclusión de variables con riesgo de leakage.
- Selección de features, baselines, métricas y estrategia de validación.
- Ejecución, revisión y verificación del código generado.
- Interpretación de los resultados.
- Definición de reglas y acciones de negocio.
- Revisión final de la documentación, las visualizaciones y las conclusiones.

Los resultados generados por IA fueron tratados como propuestas y no como evidencia. Todo el código incluido en la solución final fue ejecutado y revisado, y la responsabilidad sobre las decisiones metodológicas e intepretación de los resultados es mia