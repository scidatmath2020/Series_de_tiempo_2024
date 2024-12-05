# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 15:01:42 2024

@author: Usuario
"""

import pandas as pd
import numpy as np
from plotnine import *
from mizani.formatters import date_format
from mizani.breaks import date_breaks

import os

#### Para hacer la prueba DF
import statsmodels.tsa.stattools as sts

#### Para analizar la estacionalidad
from statsmodels.tsa.seasonal import seasonal_decompose

#### Para analizar autocorrelación
import statsmodels.graphics.tsaplots as sgt  
from statsmodels.tsa.stattools import acf, pacf

#### Para medias móviles
from statsmodels.tsa.holtwinters import SimpleExpSmoothing, ExponentialSmoothing


#### Para modelos autorregresivos
from statsmodels.tsa.ar_model import AutoReg, ar_select_order

import warnings 
warnings.filterwarnings("ignore")


#%%

# Establecer el directorio de trabajo (ajustar según tu sistema)
os.chdir("C:\\Users\\Usuario\\Documents\\scidata\\24_st\\data")

# Leer los archivos CSV
delitos_mensuales = pd.read_csv("delitos_mensuales\\delitos_mensuales.csv",encoding='latin1')
tipo_cambio = pd.read_csv("tipo_de_cambio\\tipo_cambio.csv",encoding='latin1')
climas_nyc = pd.read_csv("climas_nyc\\climas_procesado.csv")
ruidos = pd.read_csv("ruidos\\ruidos.csv")

#%%

############ Preprocesamiento

delitos_mensuales["fecha_num"] = pd.to_datetime(delitos_mensuales["fecha_num"], format='%m/%Y')
delitos_mensuales.index = delitos_mensuales["fecha_num"]

tipo_cambio["Fecha"] = pd.to_datetime(tipo_cambio["Fecha"], format='%d/%m/%Y')
tipo_cambio.index = tipo_cambio["Fecha"]


climas_nyc["datetime"] = pd.to_datetime(climas_nyc['datetime'], format='%d/%m/%Y %H:%M')
climas_nyc.index = climas_nyc["datetime"]

ruidos["fecha"] = pd.to_datetime(ruidos['fecha'], format='%d/%m/%Y')
ruidos.index = ruidos["fecha"]


# Establecemos la frecuencia de la serie de tiempo. En este caso es MS: month start
delitos_mensuales = delitos_mensuales.asfreq("MS")

tipo_cambio = tipo_cambio.asfreq("b")  #bussines 
tipo_cambio['Cambio'] = tipo_cambio['Cambio'].fillna(method='ffill')

climas_nyc = climas_nyc.asfreq("h")

ruidos = ruidos.asfreq("d")

#%%

############### Entrenamiento y prueba

## len(tabla)
n = len(delitos_mensuales)
total_datos_entrenamiento = int(0.8*n)

## tabla.iloc
entrenamiento = delitos_mensuales.iloc[:total_datos_entrenamiento]
prueba = delitos_mensuales.iloc[total_datos_entrenamiento:]

#%%

resultados = pd.DataFrame({"Real": prueba["delitos_cometidos"].values},
                          index = prueba.index)

#%%

############## Modelo AR(1)

AR1 = AutoReg(entrenamiento["delitos_cometidos"], lags=1, seasonal=False)
AR1_ajustado = AR1.fit()
print(AR1_ajustado.summary())


AR1_ajustado.params

# Predicción sobre los datos de prueba
start = len(entrenamiento)
end = len(entrenamiento) + len(prueba) - 1
predicciones_prueba_AR1 = AR1_ajustado.predict(start=start, end=end)


resultados["predicciones_prueba_AR1"] = predicciones_prueba_AR1
resultados.plot(figsize=(12,6))

#%%

############## Modelo AR(2)

AR2 = AutoReg(entrenamiento["delitos_cometidos"], lags=2, seasonal=False)
AR2_ajustado = AR2.fit()
print(AR2_ajustado.summary())

AR2_ajustado.params

# Predicción sobre los datos de prueba
start = len(entrenamiento)
end = len(entrenamiento) + len(prueba) - 1
predicciones_prueba_AR2 = AR2_ajustado.predict(start=start, end=end)

resultados["Prediccion_prueba_AR2"] = predicciones_prueba_AR2 
resultados.plot(figsize=(12,6))

#%%

# Selección del orden óptimo de lags con el criterio de información de Akaike (AIC)

max_lags = 12  # Define el máximo número de lags a probar.
selection = ar_select_order(entrenamiento["delitos_cometidos"], maxlag=max_lags, ic="aic", seasonal=False)
optimal_lags = selection.ar_lags  # Lags seleccionados.

print(f"Lags seleccionados: {optimal_lags}")

# Entrenamiento del modelo autorregresivo con los datos de entrenamiento y el número óptimo de lags
ARautomatico = AutoReg(entrenamiento["delitos_cometidos"], lags=optimal_lags, seasonal=False)
ARautomatico_ajustado = ARautomatico.fit()

# Resumen del modelo entrenado
print(ARautomatico_ajustado.summary())

ARautomatico_ajustado.params

# Predicción sobre los datos de prueba
start = len(entrenamiento)
end = len(entrenamiento) + len(prueba) - 1
predicciones_prueba_ARautomatico = ARautomatico_ajustado.predict(start=start, end=end)

# Comparación de predicciones con los datos reales
resultados["Prediccion_prueba_ARautomatico"] = predicciones_prueba_ARautomatico 

resultados.plot(figsize=(12,6))

#%%

AR1_ajustado.aic
AR2_ajustado.aic
ARautomatico_ajustado.aic

#%%

# Predicción de valores futuros
n_pred = 12  # Número de predicciones futuras (e.g., 12 meses).
futuras_predicciones = ARautomatico_ajustado.predict(start=len(delitos_mensuales), end=len(delitos_mensuales) + n_pred - 1)

delitos_mensuales["delitos_cometidos"].plot()
futuras_predicciones.plot(figsize=(12,6))


