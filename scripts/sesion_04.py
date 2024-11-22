# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 17:15:21 2024

@author: Usuario
"""

import pandas as pd
import numpy as np

data_1 = pd.DataFrame({
    "W": [0.896766, 0.624211, 0.228907, 0.633909, 0.841789],
    "X": [0.881690, 0.955746, 0.510997, 0.367079, 0.535549],
    "Y": [0.033998, 0.858047, 0.827106, 0.404721, 0.942269],
    "Z": [0.254148, 0.170809, 0.957140, 0.715977, 0.525564]
})
data_1.index = ["A", "B", "C", "D", "E"]

data_1["SUMA_W_Y"] = data_1["W"] + data_1["Y"]

##### Filtremos las filas donde los valores de la columna Z sean
##### mayores que 0.5
data_1[data_1["Z"]>0.5]

##### Filtremos las filas donde los valores de la columna Z sean
##### mayores que 0.5 o los valore de la columna X sean menores
##### que 0.9

data_1[(data_1["Z"] > 0.5) | (data_1["X"] < 0.9)]

##### Filtremos las filas donde los valores de la columna W sean
##### menores que 0.7 y los valore de la columna Y sean mayores
##### que 0.6

data_1[(data_1["W"] < 0.7) & (data_1["Y"] > 0.6)]

##### Manejo de valores faltantes

df = pd.DataFrame({
    'A': [1, 2, np.nan],
    'B': [5, np.nan, np.nan],
    'C': [1, 2, 3]}
)
df

# crea un nuevo dataframe sin las filas con valores faltantes
df_na_filas = df.dropna(axis=0)  #axis=0 significa filas

# crea un nuevo dataframe sin las columnas con valores faltantes
df_na_columnas = df.dropna(axis=1)  #axis=1 significa columnas


############# Rellenando con 0
df_na_rellenos_0 = df.fillna(value=0)
df_na_rellenos_0

############# Rellenando con promedios
df_na_rellenos_media = df.fillna(df.mean())

####### Agrupamiento de tablas

ventas_vendedor = pd.DataFrame({
    'compania': ['GOOG', 'GOOG', 'FB', 'MSFT', 'FB', 'MSFT'],
    'vendedor': ['Sam', 'Carlos', 'Vanessa', 'Carla', 'Sara', 'Luis'],
    'ventas': [182, 199, 157, 181, 174, 152]
})

ventas_vendedor

####### calcular el total de ventas por compañía
ventas_totales = ventas_vendedor.groupby("compania").sum("ventas")
ventas_totales





