# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 17:02:51 2024

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

### pip install pmdarima
#### Para ARIMA automático
from pmdarima import auto_arima

#### Para revisar error promedio cometido
from statsmodels.tools.eval_measures import rmse

import warnings 
warnings.filterwarnings("ignore")

#%%

# Establecer el directorio de trabajo (ajustar según tu sistema)
os.chdir("C:\\Users\\Usuario\\Documents\\scidata\\24_st\\data")

#delitos_mensuales = pd.read_csv("delitos_mensuales\\delitos_mensuales.csv",encoding='latin1')

indices = pd.read_csv("index_2018\\Index2018.csv")





#%%

############ Preprocesamiento

delitos_mensuales["fecha_num"] = pd.to_datetime(delitos_mensuales["fecha_num"], format='%m/%Y')
delitos_mensuales.index = delitos_mensuales["fecha_num"]
delitos_mensuales = delitos_mensuales.asfreq("MS")

#%%

############ Preprocesamiento

indices.columns

indices["date"] = pd.to_datetime(indices["date"], dayfirst=True)
indices.index = indices["date"]
indices = indices.asfreq("b")
indices = indices.fillna(method="ffill")


#%%

tabla = indices
columna_datos = "ftse"
columna_fecha = "date"

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

#%%

resultados = pd.DataFrame({"Real": prueba[columna_datos].values},
                          index = prueba.index)

#%%

# Entrenar un modelo ARIMA(1,1,1) manualmente
ARIMA_1_1_1 = ARIMA(entrenamiento[columna_datos], order=(1, 1, 1))  
ARIMA_1_1_1_ajustado = ARIMA_1_1_1.fit()
ARIMA_1_1_1_ajustado.summary()

# Predicciones sobre los datos de prueba
start = len(entrenamiento)
end = len(entrenamiento) + len(prueba) - 1
predicciones_prueba_ARIMA_1_1_1 = ARIMA_1_1_1_ajustado.predict(start=start, end=end)

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

# Entrenar el modelo ARIMA con el orden óptimo seleccionado
def informacion_arima(p,d,q,columna_entrenamiento):
    mi_ARMA = ARIMA(columna_entrenamiento, order=(p,d,q))
    mi_ARMA_ajustado = mi_ARMA.fit()
    akaike = mi_ARMA_ajustado.aic
    limite_ar = "ar.L" + str(p)
    limite_ma = "ma.L" + str(q)
    significativo_ar = limite_ar in mi_ARMA_ajustado.params[mi_ARMA_ajustado.pvalues <0.05].index
    significativo_ma = limite_ma in mi_ARMA_ajustado.params[mi_ARMA_ajustado.pvalues <0.05].index
    limites_significativos = significativo_ar + significativo_ma
    total_significativos = len(mi_ARMA_ajustado.params[mi_ARMA_ajustado.pvalues <0.05])-1
    return pd.DataFrame({"AIC":akaike,
                         "limites_significativos":limites_significativos,
                         "total_significativos":total_significativos},index=[f"ARIMA_{p}_{d}_{q}"])

#%%

max_ar = 7
max_ma = 6
d = 1

arimas = [informacion_arima(p,d,q,entrenamiento[columna_datos]) for p in range(1,max_ar+1) for q in range(1,max_ma+1)]

resultados_arimas = pd.concat(arimas)

resultados_arimas_ordenados = resultados_arimas.sort_values(
    by=['limites_significativos', 'AIC', 'total_significativos'], 
    ascending=[False, True, True]
)

resultados_arimas_ordenados

#%%

ARIMA_2_1_5 = ARIMA(entrenamiento[columna_datos], order=(2, 1, 5))  
ARIMA_2_1_5_ajustado = ARIMA_2_1_5.fit()
ARIMA_2_1_5_ajustado.summary()

# Predicciones sobre los datos de prueba
start = len(entrenamiento)
end = len(entrenamiento) + len(prueba) - 1
predicciones_prueba_ARIMA_2_1_5 = ARIMA_2_1_5_ajustado.predict(start=start, end=end)

resultados["Prediccion_prueba_ARIMA_2_1_5"] = predicciones_prueba_ARIMA_2_1_5

resultados.plot(figsize=(12,6))
plt.show()



#%%

ARIMA_10_2_3 = ARIMA(entrenamiento[columna_datos], order=(10, 2, 3))  
ARIMA_10_2_3_ajustado = ARIMA_10_2_3.fit()
ARIMA_10_2_3_ajustado.summary()

# Predicciones sobre los datos de prueba
start = len(entrenamiento)
end = len(entrenamiento) + len(prueba) - 1
predicciones_prueba_ARIMA_10_2_3 = ARIMA_10_2_3_ajustado.predict(start=start, end=end)

resultados["Prediccion_prueba_ARIMA_10_2_3"] = predicciones_prueba_ARIMA_10_2_3

resultados.plot(figsize=(12,6))
plt.show()


#%%
# from pmdarima import auto_arima

# Optimizar parámetros ARIMA automáticamente
modelo_auto = auto_arima(entrenamiento[columna_datos], 
                         seasonal=False, 
                         stepwise=True, 
                         suppress_warnings=True, 
                         trace=True)

# Resumen del modelo optimizado
print(modelo_auto.summary())

# Ajustar el modelo con los parámetros sugeridos
modelo_ajustado = ARIMA(entrenamiento[columna_datos], 
                        order=modelo_auto.order).fit()

# Predicción
predicciones = modelo_ajustado.predict(start=start, end=end)

resultados["auto_arima"] = predicciones

resultados.plot(figsize=(12, 6))
plt.show()

#%%

## Error cometido
error_1_1_1 = rmse(resultados["Real"], resultados["Prediccion_prueba_ARIMA_1_1_1"])
#error_su_arima = rmse(resultados["Real"], resultados["Prediccion_prueba_ARIMA_4_2_5"])
error_mi_arima = rmse(resultados["Real"], resultados["Prediccion_prueba_ARIMA_2_1_5"])
error_auto_arima = rmse(resultados["Real"], resultados["auto_arima"])

print(f"RMSE del modelo ARIMA(1, 1, 1): {error_1_1_1:.4f}")
#print(f"RMSE del modelo ARIMA(4, 2, 5): {error_su_arima:.4f}")
print(f"RMSE del modelo mi_arima: {error_mi_arima:.4f}")
print(f"RMSE del modelo auto_arima: {error_auto_arima:.4f}")