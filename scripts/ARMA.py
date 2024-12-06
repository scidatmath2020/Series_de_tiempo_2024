# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 13:22:48 2024

@author: Usuario
"""

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

# Entrenar un modelo ARMA(1,0,1) manualmente
ARMA_1_0_1 = ARIMA(entrenamiento["delitos_cometidos"], order=(1, 0, 1))  # (p=0, d=0, q=1)
ARMA_1_0_1_ajustado = ARMA_1_0_1.fit()
print(ARMA_1_0_1_ajustado.summary())

# Predicciones sobre los datos de prueba
start = len(entrenamiento)
end = len(entrenamiento) + len(prueba) - 1
predicciones_prueba_ARMA_1_0_1 = ARMA_1_0_1_ajustado.predict(start=start, end=end)

resultados["Prediccion_prueba_ARMA_1_0_1"] = predicciones_prueba_ARMA_1_0_1

resultados.plot(figsize=(12,6))

#%%


# Entrenar el modelo MA con el orden óptimo seleccionado
def informacion_arma(a,b,columna_entrenamiento):
    mi_ARMA = ARIMA(columna_entrenamiento, order=(a,0,b))
    mi_ARMA_ajustado = mi_ARMA.fit()
    akaike = mi_ARMA_ajustado.aic
    limite_ar = "ar.L" + str(a)
    limite_ma = "ma.L" + str(b)
    significativo_ar = limite_ar in mi_ARMA_ajustado.params[mi_ARMA_ajustado.pvalues <0.05].index
    significativo_ma = limite_ma in mi_ARMA_ajustado.params[mi_ARMA_ajustado.pvalues <0.05].index
    limites_significativos = significativo_ar + significativo_ma
    total_significativos = len(mi_ARMA_ajustado.params[mi_ARMA_ajustado.pvalues <0.05])-1
    return pd.DataFrame({"AIC":akaike,
                         "limites_significativos":limites_significativos,
                         "total_significativos":total_significativos},index=[f"ARMA_{a}_0_{b}"])

#%%
max_ar = 6
max_ma = 6

armas = [informacion_arma(a,b,entrenamiento["delitos_cometidos"]) for a in range(1,max_ar+1) for b in range(1,max_ma+1)]

resultados_armas = pd.concat(armas)

resultados_armas_ordenados = resultados_armas.sort_values(
    by=['limites_significativos', 'AIC', 'total_significativos'], 
    ascending=[False, True, True]
)

resultados_armas_ordenados

#%%

mi_ARMA = ARIMA(entrenamiento["delitos_cometidos"], order=(4,0,6))
mi_ARMA_ajustado = mi_ARMA.fit()
print(mi_ARMA_ajustado.summary())

start = len(entrenamiento)
end = len(entrenamiento) + len(prueba) - 1
predicciones_prueba_mi_ARMA = mi_ARMA_ajustado.predict(start=start, end=end)


resultados["Prediccion_prueba_mi_ARMA"] = predicciones_prueba_mi_ARMA
resultados.plot(figsize=(12,6))

