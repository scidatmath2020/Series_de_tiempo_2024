# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 17:17:13 2024

@author: Usuario
"""
import numpy as np
import pandas as pd

tabla = pd.DataFrame({"Name": ["Alice", "Bob", "Charlie", "David", "Eve"],
                      "Age": [24, 27, 22, 32, 29],
                      "City": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"],
                      "Score": [88, 92, 85, 95, 90]})
tabla

tabla["Age"]


tabla[["Name","Score"]]
tabla[["Score","Name"]]

tabla[["Name","Score","Age"]]


tabla["Score"]

tabla.index = ["estudiante01","estudiante02","estudiante03",
               "estudiante04","estudiante05"]
tabla

tabla.columns = ["Alumno","Edad","Ciudad","Puntaje"]
tabla

data_1 = pd.DataFrame({
    "W": [0.896766, 0.624211, 0.228907, 0.633909, 0.841789],
    "X": [0.881690, 0.955746, 0.510997, 0.367079, 0.535549],
    "Y": [0.033998, 0.858047, 0.827106, 0.404721, 0.942269],
    "Z": [0.254148, 0.170809, 0.957140, 0.715977, 0.525564]
})
data_1.index = ["A", "B", "C", "D", "E"]

data_1["W"] + data_1["Y"]

data_1

data_1["Suma_W_Y"] = data_1["W"] + data_1["Y"]
data_1

suma = data_1["W"] + data_1["Y"]
suma

data_1.loc[["A","B","D"]]
data_1.iloc[[0,1,3]]

data_1[["W","Y"]].loc[["A","B","D"]]

data_1.loc[["A","B","C"]][["W","Y"]]

data_1.loc[["A","B","D"],["W","Y"]]

data_1[data_1 > 0.5]

data_condicion = data_1[data_1>0.5]




