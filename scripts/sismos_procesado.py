# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 16:56:04 2024

@author: Usuario
"""
# Cargar las librerías necesarias
import pandas as pd
import numpy as np
from siuba import *
from plotnine import *

import os

# Establecer el directorio de trabajo (ajustar según tu sistema)
os.chdir("C:\\Users\\Usuario\\Documents\\scidata\\24_st\\data\\sismos")

# Leer el archivo CSV
procesado_sismos = pd.read_csv("sismos_procesado.csv",encoding='latin1')

# Ver las primeras filas
procesado_sismos.head()

# Resumen descriptivo
procesado_sismos.describe()

# Conteo de valores faltantes por columna
procesado_sismos.isna().sum()

# Conteo de valores faltantes en la columna Guerrero
procesado_sismos.Guerrero.isna().sum()

# Convertir la columna Mes_Año a tipo fecha
procesado_sismos["Mes_Año"] = pd.to_datetime(procesado_sismos["Mes_Año"], format='%d/%m/%Y')

# Graficar las series de tiempo
(
ggplot(data=procesado_sismos) + geom_line(mapping=aes(x="Mes_Año",y="Guerrero"),color="red") +
    geom_line(mapping=aes(x="Mes_Año",y="Oaxaca"),color="blue") +
    geom_line(mapping=aes(x="Mes_Año",y="Puebla"),color="purple") +
    labs(
        x="Mes/Año",                    # Título del eje X
        y="Magnitud promedio",          # Título del eje Y
        title="Magnitud promedio por región"  # (Opcional) Título del gráfico
    ) +
    theme(
        axis_text_x=element_text(rotation=45, hjust=1)  # Rotar etiquetas del eje X
    )
)