# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 12:28:46 2024

@author: Usuario
"""

import pandas as pd
import numpy as np
from plotnine import *
import matplotlib.pyplot as plt

import os

#### Escalador de datos
from sklearn.preprocessing import MinMaxScaler

#### Para crear un generador de series de tiempo
from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator

#### Para crear la red neuronal
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM

from tensorflow.keras.models import load_model

# Cargar el modelo desde el archivo



#%%

# Establecer el directorio de trabajo (ajustar según tu sistema)
os.chdir("C:\\Users\\Usuario\\Documents\\scidata\\24_st\\data")

ventas = pd.read_csv("ventas_alcohol\\S4248SM144NCEN.csv")

#%%
ventas.rename(columns={"observation_date":"Fecha","S4248SM144NCEN":"total"},inplace=True) 

#%%

ventas["Fecha"] = pd.to_datetime(ventas["Fecha"], infer_datetime_format=True)
ventas.index = ventas["Fecha"]

ventas = ventas.asfreq("MS")
del ventas["Fecha"]

#%%

ventas.plot()
plt.show()

#%%

tabla = ventas

#%%
############## Entrenamiento y prueba

## len(tabla)
n = len(tabla)
total_datos_entrenamiento = int(0.8*n)

## tabla.iloc
entrenamiento = tabla.iloc[:total_datos_entrenamiento]
prueba = tabla.iloc[total_datos_entrenamiento:]


#%%

escalador = MinMaxScaler()
escalador.fit(entrenamiento)

entrenamiento_escalado = escalador.transform(entrenamiento)
prueba_escalado = escalador.transform(prueba)

#%%

n_entradas = 2
n_caracteristicas = 1

generador = TimeseriesGenerator(entrenamiento_escalado,
                                entrenamiento_escalado,
                                length = n_entradas,
                                batch_size = 1)

#%%

n_entradas = 12
n_caracteristicas = 1

generador = TimeseriesGenerator(entrenamiento_escalado,
                                entrenamiento_escalado,
                                length = n_entradas,
                                batch_size = 1)

#%%

mi_modelo = Sequential()
mi_modelo.add(LSTM(100,activation="relu",input_shape=(n_entradas,n_caracteristicas)))
mi_modelo.add(Dense(1))
mi_modelo.compile(optimizer="adam",loss="mse")

mi_modelo.summary()

#%%

mi_modelo.fit(generador,epochs=50)

mi_modelo.history.history.keys()

perdida_por_epoca = mi_modelo.history.history["loss"]
plt.plot(range(len(perdida_por_epoca)),perdida_por_epoca)
plt.show()

#%%

################ Evaluar los datos de prueba

eval_batch_1 = entrenamiento_escalado[-12:]
eval_batch_1

eval_batch_1 = eval_batch_1.reshape((1,n_entradas,n_caracteristicas))

mi_modelo.predict(eval_batch_1)
prueba_escalado[0]

#%%

############### Predicciones en toda la prueba

predicciones_prueba = []
eval_batch_1 = entrenamiento_escalado[-n_entradas:]
batch_actualizado = eval_batch_1.reshape((1,n_entradas,n_caracteristicas))

for i in range(len(prueba_escalado)):
    
    pred_actual = mi_modelo.predict(batch_actualizado)[0]
    predicciones_prueba.append(pred_actual)
    batch_actualizado = np.append(batch_actualizado[:,1:,:],[[pred_actual]],axis=1)
    
predicciones_prueba

#%%

############## Deshacer la normalización

predicciones_originales = escalador.inverse_transform(predicciones_prueba)
prueba["predicciones"] = predicciones_originales

prueba.plot()
plt.show()

#%%

############## Guardar el modelo

mi_modelo.save("C:\\Users\\Usuario\\Documents\\scidata\\24_st\\data\\ventas_alcohol\\mi_red_neuronal.keras")

############## Cargar modelo

modelo_guardado = load_model("C:\\Users\\Usuario\\Documents\\scidata\\24_st\\data\\ventas_alcohol\\mi_red_neuronal.keras",
                             compile=False)


modelo_guardado

#%%

############### Predecir el futuro

n_predicciones = 12

# Datos de entrada para hacer predicciones (últimos 12 meses de la serie de prueba)
eval_batch_1 = prueba_escalado[-n_entradas:]  # Últimos 12 meses de la serie de prueba
batch_actualizado = eval_batch_1.reshape((1, n_entradas, n_caracteristicas))  # Ajustar la forma del batch

# Lista para almacenar las predicciones
predicciones_futuras = []

# Hacer predicciones iterativas
for i in range(n_predicciones):
    # Hacer una predicción
    pred_actual = modelo_guardado.predict(batch_actualizado)[0]
    predicciones_futuras.append(pred_actual)
    
    # Actualizar el batch con la predicción para la siguiente iteración
    batch_actualizado = np.append(batch_actualizado[:, 1:, :], [[pred_actual]], axis=1)

# Deshacer la normalización de las predicciones
predicciones_futuras_originales = escalador.inverse_transform(predicciones_futuras)

# Mostrar las predicciones
print(predicciones_futuras_originales)

# Agregar las predicciones a un DataFrame para visualizarlas
fechas_futuras = pd.date_range(ventas.index[-1] + pd.Timedelta(days=1), periods=n_predicciones, freq='MS')
predicciones_df = pd.DataFrame(predicciones_futuras_originales, index=fechas_futuras, columns=['Predicciones'])

# Mostrar las predicciones
print(predicciones_df)

# Graficar las predicciones junto con los datos reales
plt.figure(figsize=(10,6))
plt.plot(ventas.index, ventas['total'], label='Datos Reales')
plt.plot(predicciones_df.index, predicciones_df['Predicciones'], label='Predicciones', color='red')
plt.legend()
plt.show()



















