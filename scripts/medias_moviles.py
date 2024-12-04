# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 08:54:14 2024

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
# Visualización
(ggplot(delitos_mensuales) +
     geom_line(aes(x='fecha_num', y='delitos_cometidos',color="factor(Año)")) +
     scale_x_date(date_breaks="1 year", date_labels="%Y") +
     labs(x="Año", y="Delitos Cometidos")
)

(ggplot(tipo_cambio) +
     geom_line(aes(x='Fecha', y='Cambio')) 
)

(ggplot(climas_nyc) +
     geom_line(aes(x='datetime', y='temp_c')) 
)

(ggplot(ruidos) +
     geom_line(aes(x='fecha', y='wn')) 
)

(ggplot(ruidos) +
     geom_line(aes(x='fecha', y='ca')) 
)

#%%

delitos_mensuales["6_meses_SMA"] = delitos_mensuales["delitos_cometidos"].rolling(window=6).mean()


#%%

'''
################################################################
################################################################
##############   FUNCIÓN DE MEDIAS MÓVILES    ##################
################################################################
################################################################
'''

def medias_moviles(tabla,columna_datos,columna_fecha,lista_tipos_MA,lista_parametros_MA,escala,titulo):
    tabla["tipo"] = "original"
    tablas = [tabla[[columna_fecha,columna_datos,"tipo"]]]
    ######### medias móviles simples
    if "SMA" in lista_tipos_MA:
        indices_SMA = [i for i, valor in enumerate(lista_tipos_MA) if valor == "SMA"]
        aux_SMA = [pd.DataFrame({columna_fecha:tabla[columna_fecha],
                                 columna_datos:tabla[columna_datos].rolling(window=lista_parametros_MA[x]).mean(),
                                 "tipo":f"{lista_parametros_MA[x]}_{escala}_SMA"}) for x in indices_SMA]
        aux_SMA = pd.concat(aux_SMA,axis=0)
        tablas.append(aux_SMA)
    
    ######### medias móviles exponenciales
    if "EWMA" in lista_tipos_MA:
        indices_EWMA = [i for i, valor in enumerate(lista_tipos_MA) if valor == "EWMA"]
        aux_EWMA = [pd.DataFrame({columna_fecha:tabla[columna_fecha],
                                  columna_datos:tabla[columna_datos].ewm(span=lista_parametros_MA[x],adjust=False).mean(),
                                  "tipo":f"{lista_parametros_MA[x]}_{escala}_EWMA"}) for x in indices_EWMA]    
        aux_EWMA = pd.concat(aux_EWMA,axis=0)
        tablas.append(aux_EWMA)
    
    ######### medias móviles dobles
    if "DoubHW" in lista_tipos_MA:
        indices_DoubHW = [i for i, valor in enumerate(lista_tipos_MA) if valor == "DoubHW"]
        aux_DoubHW = [pd.DataFrame({columna_fecha:tabla[columna_fecha],
                                    columna_datos:ExponentialSmoothing(tabla[columna_datos],trend=lista_parametros_MA[x]).fit().fittedvalues.shift(-1),
                                    "tipo":f"{lista_parametros_MA[x]}_{escala}_DoubHW"}) for x in indices_DoubHW]    
        aux_DoubHW = pd.concat(aux_DoubHW,axis=0)
        tablas.append(aux_DoubHW)
        
    ######### medias móviles triples
    if "TripHW" in lista_tipos_MA:
        indices_TripHW = [i for i, valor in enumerate(lista_tipos_MA) if valor == "TripHW"]
        aux_TripHW = [pd.DataFrame({columna_fecha:tabla[columna_fecha],
                                    columna_datos:ExponentialSmoothing(tabla[columna_datos],
                                                                       trend=lista_parametros_MA[x][0],
                                                                       seasonal=lista_parametros_MA[x][0],
                                                                       seasonal_periods=lista_parametros_MA[x][1]).fit().fittedvalues.shift(-1),
                                    "tipo":f"{lista_parametros_MA[x][0]}{lista_parametros_MA[x][1]}_{escala}_TripHW"}) for x in indices_TripHW]    
        aux_TripHW = pd.concat(aux_TripHW,axis=0)
        tablas.append(aux_TripHW)
    
    #########
    auxiliares = pd.concat(tablas,axis=0)
    
    #########
    grafica = (ggplot(data=auxiliares) +
               geom_line(mapping=aes(x=columna_fecha,y=columna_datos,color="tipo")) +
               labs(title="Diferentes Medias móviles para "+titulo, x="Tiempo", y="Valor", color="Tipo de MA") +
#               scale_color_cmap(cmap_name="viridis") +
               theme_bw() +
               theme(
                   legend_position='top',  # Ubicar la leyenda arriba
                   axis_text_x=element_text(rotation=90, hjust=1),  # Rotar etiquetas del eje X
                   plot_title=element_text(size=14, weight='bold', ha='center')  # Estilo del título
                   )
               )
    
    return [auxiliares,grafica]

#%%
'''
#medias_moviles(tabla,columna_datos,columna_fecha,lista_tipos_MA,lista_parametros_MA,escala,titulo)

# lista_tipos_MA: "SMA", "EWMA", "DoubHW", "TripHW"
# lista_parámetros_MA: 
##    "SMA": entero
##    "EWMA": entero
##    "DoubHW": "add" o "mul"
##    "TripHW": ["add",periodo de estacionalidad] o ["mult",periodo de estacionalidad]
'''

medias_moviles(delitos_mensuales,
               "delitos_cometidos",
               "fecha_num",
               ["SMA","SMA","SMA"],
               [12,6,24],
               "meses",
               "Delitos mensuales")[1]


medias_moviles(delitos_mensuales,
               "delitos_cometidos",
               "fecha_num",
               ["SMA","EWMA","DoubHW"],
               [3,6,"mul"],
               "meses",
               "Delitos mensuales")[1]

medias_moviles(delitos_mensuales,
               "delitos_cometidos",
               "fecha_num",
               ["EWMA","DoubHW","TripHW"],
               [12,"add", ["add",12]],
               "meses",
               "Delitos mensuales")[1]

medias_moviles(delitos_mensuales,
               "delitos_cometidos",
               "fecha_num",
               ["DoubHW","DoubHW","TripHW"],
               ["add","mul",["add",12]],
               "meses",
               "Delitos mensuales")[1]

medias_moviles(delitos_mensuales,
               "delitos_cometidos",
               "fecha_num",
               ["TripHW"],
               [["add",12]],
               "meses",
               "Delitos mensuales")[1]


medias_moviles(ruidos,
               "ca",
               "fecha",
               ["SMA","SMA","EWMA"],
               [50,100,20],
               "meses",
               "Caminata aleatoria")[1]

