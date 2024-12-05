# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 09:21:13 2024

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


#### Para modelos autorregresivos: AR
from statsmodels.tsa.ar_model import AutoReg, ar_select_order

#### Para modelos de medias móviles: MA
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import arma_order_select_ic


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

# Entrenar un modelo MA(1) manualmente
MA1 = ARIMA(entrenamiento["delitos_cometidos"], order=(0, 0, 1))  # (p=0, d=0, q=1)
MA1_ajustado = MA1.fit()
print(MA1_ajustado.summary())

# Predicciones sobre los datos de prueba
start = len(entrenamiento)
end = len(entrenamiento) + len(prueba) - 1
predicciones_prueba_MA1 = MA1_ajustado.predict(start=start, end=end)

resultados["Prediccion_prueba_MA1"] = predicciones_prueba_MA1

resultados.plot(figsize=(12,6))


#%%

# Selección automática del mejor orden MA usando criterio AIC/BIC con 12 retrasos
max_order = 12  # Máximo número de lags
selection = arma_order_select_ic(entrenamiento["delitos_cometidos"], 
                                 max_ar=0, 
                                 max_ma=max_order, ic="aic")

optimal_ma_order = selection.aic_min_order[1]  # Escoge el orden óptimo basado en BIC

print(f"Orden óptimo para MA: {optimal_ma_order}")

# Entrenar el modelo MA con el orden óptimo seleccionado
MAautomatico_12 = ARIMA(entrenamiento["delitos_cometidos"], order=(0, 0, optimal_ma_order))
MAautomatico_ajustado_12 = MAautomatico_12.fit()
print(MAautomatico_ajustado_12.summary())

# Predicciones sobre los datos de prueba
start = len(entrenamiento)
end = len(entrenamiento) + len(prueba) - 1
predicciones_prueba_MAautomatico_12 = MAautomatico_ajustado_12.predict(start=start, end=end)

resultados["Prediccion_prueba_MAautomatico_12"] = predicciones_prueba_MAautomatico_12

# Mostrar las primeras filas de resultados
print(resultados.head())

resultados.plot(figsize=(12,6))


#%%

# Selección automática del mejor orden MA usando criterio AIC/BIC con 24 retrasos
max_order = 24  # Máximo número de lags
selection = arma_order_select_ic(entrenamiento["delitos_cometidos"], 
                                 max_ar=0, 
                                 max_ma=max_order, ic="aic")

optimal_ma_order = selection.aic_min_order[1]  # Escoge el orden óptimo basado en BIC

print(f"Orden óptimo para MA: {optimal_ma_order}")

# Entrenar el modelo MA con el orden óptimo seleccionado
MAautomatico_24 = ARIMA(entrenamiento["delitos_cometidos"], order=(0, 0, optimal_ma_order))
MAautomatico_ajustado_24 = MAautomatico_24.fit()
print(MAautomatico_ajustado_24.summary())

# Predicciones sobre los datos de prueba
start = len(entrenamiento)
end = len(entrenamiento) + len(prueba) - 1
predicciones_prueba_MAautomatico_24 = MAautomatico_ajustado_24.predict(start=start, end=end)

resultados["Prediccion_prueba_MAautomatico_24"] = predicciones_prueba_MAautomatico_24

# Mostrar las primeras filas de resultados
print(resultados.head())

resultados.plot(figsize=(12,6))

#%%

# Predicción de valores futuros
n_pred = 12  # Número de predicciones futuras (e.g., 12 meses).
futuras_predicciones = MAautomatico_ajustado_24.predict(start=len(delitos_mensuales), end=len(delitos_mensuales) + n_pred - 1)

delitos_mensuales["delitos_cometidos"].plot()
futuras_predicciones.plot(figsize=(12,6))
