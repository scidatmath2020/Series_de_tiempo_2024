# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 13:25:22 2024

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

pasajeros = pd.read_csv("airline_passengers.csv")

#%%
pasajeros.rename(columns={"mes":"Fecha","pasajeros(miles)":"total"},inplace=True) 

#%%
pasajeros["Fecha"] = pd.to_datetime(pasajeros["Fecha"], infer_datetime_format=True)
pasajeros.index = pasajeros["Fecha"]
pasajeros = pasajeros.asfreq("MS")

#%%

pasajeros["mes"] = pasajeros["Fecha"].dt.month


#%%

tabla = pasajeros
columna_datos = "total"
columna_fecha = "Fecha"

columna_exogena = "mes"

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

SARIMA_model = auto_arima(entrenamiento[columna_datos], start_p=1, start_q=1,
                         test='adf',
                         max_p=3, max_q=3, 
                         m=12, #12 es la frecuencia del ciclo
                         start_P=0, 
                         seasonal=True, #desestacionalizar
                         d=None, 
                         D=None, #Orden de la diferenciacion estacional
                         trace=False,
                         error_action='ignore',  
                         suppress_warnings=True, 
                         stepwise=True)

SARIMA_model.summary



#%%

mi_SARIMA = ARIMA(entrenamiento[columna_datos],
                  order=(1, 1, 0),
                  seasonal_order=(0,1,0,12))
mi_SARIMA_ajustado = mi_SARIMA.fit()
mi_SARIMA_ajustado.summary()

predicciones_SARIMA = mi_SARIMA_ajustado.forecast(steps=len(prueba))

resultados["predicciones_SARIMA"] = predicciones_SARIMA

resultados.plot(figsize=(12,6))
plt.show()

#%%
   
SARIMAX_model = auto_arima(entrenamiento[[columna_datos]],
                           entrenamiento[[columna_exogena]],
                           start_p=1, start_q=1,
                         test='adf',
                         max_p=3, max_q=3, 
                         m=12, #12 es la frecuencia del ciclo
                         start_P=0, 
                         seasonal=True, #desestacionalizar
                         d=None, 
                         D=None, #Orden de la diferenciacion estacional
                         trace=False,
                         error_action='ignore',  
                         suppress_warnings=True, 
                         stepwise=True)

SARIMAX_model.summary

#%%

mi_SARIMAX = ARIMA(entrenamiento[columna_datos],
                   exog = entrenamiento[columna_exogena],
                  order=(1, 0, 0),
                  seasonal_order=(1,0,1,12))
mi_SARIMAX_ajustado = mi_SARIMAX.fit()
mi_SARIMAX_ajustado.summary()

predicciones_SARIMAX = mi_SARIMAX_ajustado.forecast(steps=len(prueba),
                                                    exog=prueba[columna_exogena])

resultados["predicciones_SARIMAX"] = predicciones_SARIMAX

resultados.plot(figsize=(12,6))
plt.show()

#%%

mi_modelo_ajustado.aic
mi_SARIMAX_ajustado.aic
