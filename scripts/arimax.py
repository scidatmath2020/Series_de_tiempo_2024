# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 10:07:53 2024

@author: Usuario
"""

import pandas as pd
import numpy as np
from plotnine import *
from mizani.formatters import date_format
from mizani.breaks import date_breaks
import matplotlib.pyplot as plt

import os

#### Para hacer la prueba DF
import statsmodels.tsa.stattools as sts
from statsmodels.tsa.stattools import adfuller

#### Para analizar la estacionalidad
from statsmodels.tsa.seasonal import seasonal_decompose

#### Para analizar autocorrelación
import statsmodels.graphics.tsaplots as sgt  
from statsmodels.tsa.stattools import acf, pacf

#### Para medias móviles
from statsmodels.tsa.holtwinters import SimpleExpSmoothing, ExponentialSmoothing


#### Para modelos autorregresivos: AR
from statsmodels.tsa.ar_model import AutoReg, ar_select_order

#### Para modelos de medias móviles: MA
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import arma_order_select_ic

#### Para ARIMA automático
from pmdarima import auto_arima

#### Para revisar error promedio cometido
from statsmodels.tools.eval_measures import rmse

import warnings 
warnings.filterwarnings("ignore")

#%%

# Establecer el directorio de trabajo (ajustar según tu sistema)
os.chdir("C:\\Users\\Usuario\\Documents\\scidata\\24_st\\data")

retrasos = pd.read_csv("climas_nyc\\retrasos.csv")

#%%

retrasos["date"] = pd.to_datetime(retrasos["date"], dayfirst=True)
retrasos.index = retrasos["date"]
retrasos = retrasos.asfreq("d")

#%%

tabla = retrasos
columna_datos = "avg_dep_delay"
columna_fecha = "date"

columna_exogena = "avg_visib"

#%%
############## Entrenamiento y prueba

## len(tabla)
n = len(tabla)
total_datos_entrenamiento = int(0.8*n)

## tabla.iloc
entrenamiento = tabla.iloc[:total_datos_entrenamiento]
prueba = tabla.iloc[total_datos_entrenamiento:]

#%%

tabla['Conjunto'] = ['Entrenamiento' if i < total_datos_entrenamiento else 'Prueba' for i in range(n)]

(
ggplot(data=tabla) + 
    geom_line(mapping=aes(x=columna_fecha,y=columna_datos,color="Conjunto"))
)

(
ggplot(data=tabla) + 
    geom_line(mapping=aes(x=columna_fecha,y=columna_datos,linetype="Conjunto",color=columna_exogena))
)


#%%

resultados = pd.DataFrame({"Real": prueba[columna_datos].values},
                          index = prueba.index)

#%%

ARIMA_1_1_1 = ARIMA(entrenamiento[columna_datos],exog=entrenamiento[columna_exogena], order=(1, 1, 1))  
ARIMA_1_1_1_ajustado = ARIMA_1_1_1.fit()
ARIMA_1_1_1_ajustado.summary()

# Predicciones sobre los datos de prueba
start = len(entrenamiento)
end = len(entrenamiento) + len(prueba) - 1
predicciones_prueba_ARIMA_1_1_1 = ARIMA_1_1_1_ajustado.forecast(steps=len(prueba),
                                                                exog=prueba[columna_exogena])

resultados["Prediccion_prueba_ARIMA_1_1_1"] = predicciones_prueba_ARIMA_1_1_1

resultados.plot(figsize=(12,6))
plt.show()

#%%

# Función para verificar estacionariedad usando la prueba ADF
def es_estacionaria(serie, nivel_significancia=0.05):
    resultado_adf = adfuller(serie, autolag='AIC')
    p_valor = resultado_adf[1]
    return p_valor < nivel_significancia  # True si es estacionaria

# Función para diferenciar hasta estacionariedad
def diferenciar_hasta_estacionariedad(serie, nivel_significancia=0.05):
    serie_diferenciada = serie.copy()
    d = 0  # Contador de diferenciaciones

    while not es_estacionaria(serie_diferenciada, nivel_significancia):
        serie_diferenciada = serie_diferenciada.diff().dropna()
        d += 1
        print(f"Diferenciación {d}: ADF p-valor = {adfuller(serie_diferenciada, autolag='AIC')[1]:.4f}")

    print(f"Serie estacionaria después de {d} diferenciaciones.")
    return [serie_diferenciada, d]

#%%

diferenciar_hasta_estacionariedad(tabla[columna_datos])


#%%
# Entrenar el modelo ARIMAX con el orden óptimo seleccionado
def informacion_arimax(p,d,q,columna_entrenamiento,columna_exogena):
    mi_ARMA = ARIMA(columna_entrenamiento,
                    exog=entrenamiento[columna_exogena], order=(p,d,q))
    mi_ARMA_ajustado = mi_ARMA.fit()
    akaike = mi_ARMA_ajustado.aic
    limite_ar = "ar.L" + str(p)
    limite_ma = "ma.L" + str(q)
    significativo_ar = limite_ar in mi_ARMA_ajustado.params[mi_ARMA_ajustado.pvalues <0.05].index
    significativo_ma = limite_ma in mi_ARMA_ajustado.params[mi_ARMA_ajustado.pvalues <0.05].index
    significativo_exog = columna_exogena in mi_ARMA_ajustado.params[mi_ARMA_ajustado.pvalues <0.05].index
    limites_significativos = significativo_ar + significativo_ma
    total_significativos = len(mi_ARMA_ajustado.params[mi_ARMA_ajustado.pvalues <0.05])-1
    return pd.DataFrame({"AIC":akaike,
                         "limites_significativos":limites_significativos,
                         "total_significativos":total_significativos,
                         "exog_significativo":significativo_exog},index=[f"ARIMAX_{p}_{d}_{q}, endog={columna_exogena}"])

#%%

max_ar = 7
max_ma = 7
d = 0

arimas = [informacion_arimax(p,d,q,entrenamiento[columna_datos],columna_exogena) for p in range(1,max_ar+1) for q in range(1,max_ma+1)]

resultados_arimas = pd.concat(arimas)




resultados_arimas_ordenados = resultados_arimas.sort_values(
    by=['limites_significativos', 'AIC', 'total_significativos'], 
    ascending=[False, True, True]
)

resultados_arimas_ordenados

#%%

ARIMA_1_0_2 = ARIMA(entrenamiento[columna_datos],exog=entrenamiento[columna_exogena],
                    order=(1, 0, 2))  
ARIMA_1_0_2_ajustado = ARIMA_1_0_2.fit()
ARIMA_1_0_2_ajustado.summary()

# Predicciones sobre los datos de prueba
start = len(entrenamiento)
end = len(entrenamiento) + len(prueba) - 1
predicciones_prueba_ARIMA_1_0_2 = ARIMA_1_0_2_ajustado.forecast(steps=len(prueba),
                                                                exog=prueba[columna_exogena])

resultados["Prediccion_prueba_ARIMA_1_0_2"] = predicciones_prueba_ARIMA_1_0_2

resultados.plot(figsize=(12,6))
plt.show()

#%%

ARIMA_7_0_7 = ARIMA(entrenamiento[columna_datos],exog=entrenamiento[columna_exogena],
                    order=(7, 0, 7))  
ARIMA_7_0_7_ajustado = ARIMA_7_0_7.fit()
ARIMA_7_0_7_ajustado.summary()

# Predicciones sobre los datos de prueba
start = len(entrenamiento)
end = len(entrenamiento) + len(prueba) - 1
predicciones_prueba_ARIMA_7_0_7 = ARIMA_7_0_7_ajustado.forecast(steps=len(prueba),
                                                                exog=prueba[columna_exogena])

resultados["Prediccion_prueba_ARIMA_7_0_7"] = predicciones_prueba_ARIMA_7_0_7

resultados.plot(figsize=(12,6))
plt.show()

#%%