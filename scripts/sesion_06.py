# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 12:14:48 2024

@author: Usuario
"""

import pandas as pd
import numpy as np
from plotnine import *
from mizani.formatters import date_format
from mizani.breaks import date_breaks

import os

# Establecer el directorio de trabajo (ajustar según tu sistema)
os.chdir("C:\\Users\\Usuario\\Documents\\scidata\\24_st\\data\\sismos")

# Leer el archivo CSV
procesado_sismos = pd.read_csv("sismos_procesado.csv",encoding='latin1')

#%%

# Observamos el tipo de datos de la columna Mes_Año
procesado_sismos["Mes_Año"].dtype

# La convertimos en tipo Fecha
procesado_sismos["Mes_Año"] = pd.to_datetime(procesado_sismos["Mes_Año"], format='%d/%m/%Y')
procesado_sismos["Mes_Año"].dtype

# Colocamos la columna de fecha como índices de la tabla
procesado_sismos.index = procesado_sismos["Mes_Año"]
procesado_sismos

# Establecemos la frecuencia de la serie de tiempo. En este caso es MS: month start
procesado_sismos = procesado_sismos.asfreq("MS")
procesado_sismos.index.freq


# Visualizamos la serie únicamente para Guerrero
(
ggplot(data=procesado_sismos) + geom_line(mapping=aes(x="Mes_Año",y="Guerrero"),color="red") +
    labs(
        x="Mes/Año",                    # Título del eje X
        y="Magnitud promedio",          # Título del eje Y
        title="Magnitud promedio por región"  # (Opcional) Título del gráfico
    ) +
    theme(
        axis_text_x=element_text(rotation=45, hjust=1)  # Rotar etiquetas del eje X
    )
)

# Rellenamos los huecos
procesado_sismos["Guerrero_sinna"] = procesado_sismos["Guerrero"].interpolate(method="linear")

# Visualizamos la serie únicamente para Guerrero sin na
(
ggplot(data=procesado_sismos) + geom_line(mapping=aes(x="Mes_Año",y="Guerrero_sinna"),color="red") +
    labs(
        x="Mes/Año",                    # Título del eje X
        y="Magnitud promedio",          # Título del eje Y
        title="Magnitud promedio por región"  # (Opcional) Título del gráfico
    ) +
    scale_x_datetime(
        labels=date_format("%b %Y"),  # Formato Mes Año
        breaks=date_breaks("1 years")  # Etiquetas cada 1 año
    ) +
    theme(
        axis_text_x=element_text(rotation=45, hjust=1,size=5)  # Rotar etiquetas del eje X
    )
)

#%%

###############################################
###########      RUÍDO BLANCO       ###########
###############################################

procesado_sismos["ruido_blanco"] = np.random.normal(loc = procesado_sismos["Guerrero_sinna"].mean(),
                                                    scale = procesado_sismos["Guerrero_sinna"].std(),
                                                    size = len(procesado_sismos["Guerrero_sinna"])
                                                    )

procesado_sismos

(
ggplot(data=procesado_sismos) + 
    geom_line(mapping=aes(x="Mes_Año", y="Guerrero_sinna"), color="red") +
    geom_line(mapping=aes(x="Mes_Año", y="ruido_blanco"), color="blue") +
    labs(
        x="Mes/Año",                    # Título del eje X
        y="Magnitud promedio",          # Título del eje Y
        title="Magnitud promedio por región"  # (Opcional) Título del gráfico
    ) +
    scale_x_datetime(
        labels=date_format("%b %Y"),  # Formato Mes Año
        breaks=date_breaks("1 years")  # Etiquetas cada 1 año
    ) +
    theme(
        axis_text_x=element_text(rotation=45, hjust=1,size=5)  # Rotar etiquetas del eje X
    )
)

#%%

###############################################
########      CAMINATA ALEATORIA       ########
###############################################


## Generamos los pasos:
    
pasos = np.random.normal(loc = 0,
                         scale = 1,
                         size = len(procesado_sismos["Guerrero_sinna"])
                         )

# Calcular la suma acumulada para obtener la caminata aleatoria
CA = np.cumsum(pasos)

# Añadir la columna 'CA' al dataframe
procesado_sismos["CA"] = CA
procesado_sismos

(
ggplot(data=procesado_sismos) + 
 #   geom_line(mapping=aes(x="Mes_Año", y="Guerrero_sinna"), color="red") +
    geom_line(mapping=aes(x="Mes_Año", y="CA"), color="blue") +
    labs(
        x="Mes/Año",                    # Título del eje X
        y="Magnitud promedio",          # Título del eje Y
        title="Magnitud promedio por región"  # (Opcional) Título del gráfico
    ) +
    scale_x_datetime(
        labels=date_format("%b %Y"),  # Formato Mes Año
        breaks=date_breaks("1 years")  # Etiquetas cada 1 año
    ) +
    theme(
        axis_text_x=element_text(rotation=45, hjust=1,size=5)  # Rotar etiquetas del eje X
    )
)
