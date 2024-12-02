# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 12:26:41 2024

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

'''
################################################################
################################################################
##############   FUNCIÓN DE AUTOCORRELACIÓN   ##################
################################################################
################################################################
'''

def autocorrelacion(columna,nlags,confianza,titulo):
    acf_values, confint = acf(columna, nlags=nlags, alpha=1-confianza)
    lags = np.arange(len(acf_values))
    conf_lower = confint[:, 0] - acf_values
    conf_upper = confint[:, 1] - acf_values


    acf_data = pd.DataFrame({
        "lag": lags,
        "acf": acf_values,
        "conf_lower": conf_lower,
        "conf_upper": conf_upper
    })

    acf_data = acf_data[acf_data["lag"] > 0]


    grafica = (
        ggplot(acf_data, aes(x="lag", y="acf")) +
        geom_segment(aes(xend="lag", yend=0), color="blue") +
        geom_point(color="blue") +
        geom_hline(yintercept=0, color="black", linetype="dashed") +
        geom_ribbon(aes(x="lag", ymin="conf_lower", ymax="conf_upper"), fill="red", alpha=0.2) +
        geom_line(aes(y="conf_lower"), color="red", size=1) +
        geom_line(aes(y="conf_upper"), color="red", size=1) +
        scale_x_continuous(breaks=range(0, max(acf_data["lag"]) + 1, 5)) +  # Etiquetas de X de 5 en 5
        scale_y_continuous(breaks=np.arange(-1, 1.1, 0.1)) +
        labs(title=f"Función de autocorrelación de {titulo}\npara {nlags} retrasos con {int(100*confianza)}% de confianza", x="Lag", y="ACF")
    )
    
    return [acf_data, grafica]

#%%
'''
################################################################
################################################################
###########  FUNCIÓN DE AUTOCORRELACIÓN PARCIAL  ###############
################################################################
################################################################
'''

def autocorrelacion_parcial(columna, nlags, confianza, titulo):
    # Calcular la PACF y los intervalos de confianza
    pacf_values, confint = pacf(columna, nlags=nlags, alpha=1-confianza,method=("ols"))
    lags = np.arange(len(pacf_values))
    conf_lower = confint[:, 0] - pacf_values
    conf_upper = confint[:, 1] - pacf_values

    # Crear un DataFrame con los resultados
    pacf_data = pd.DataFrame({
        "lag": lags,
        "pacf": pacf_values,
        "conf_lower": conf_lower,
        "conf_upper": conf_upper
    })

    # Eliminar la fila de lag 0 (que no es necesaria para la gráfica)
    pacf_data = pacf_data[pacf_data["lag"] > 0]

    # Crear la gráfica con plotnine
    grafica = (
        ggplot(pacf_data, aes(x="lag", y="pacf")) +
        geom_segment(aes(xend="lag", yend=0), color="blue") +
        geom_point(color="blue") +
        geom_hline(yintercept=0, color="black", linetype="dashed") +
        geom_ribbon(aes(x="lag", ymin="conf_lower", ymax="conf_upper"), fill="red", alpha=0.2) +
        geom_line(aes(y="conf_lower"), color="red", size=1) +
        geom_line(aes(y="conf_upper"), color="red", size=1) +
        scale_x_continuous(breaks=range(0, max(pacf_data["lag"]) + 1, 5)) +  # Etiquetas de X de 5 en 5
        scale_y_continuous(breaks=np.arange(-1, 1.1, 0.1)) +
        labs(title=f"Función de autocorrelación parcial de {titulo}\npara {nlags} retrasos con {int(100*confianza)}% de confianza", x="Lag", y="PACF")
    )
    
    return [pacf_data, grafica]




#%%

'''Autocorrelación'''

##### autocorrelacion(columna,nlags,confianza,titulo)


autocor_delitos = autocorrelacion(delitos_mensuales["delitos_cometidos"],
                                  36,
                                  0.95,
                                  "Delitos cometidos mensualmente")
autocor_delitos[0]
autocor_delitos[1]

pautocor_delitos = autocorrelacion_parcial(delitos_mensuales["delitos_cometidos"],36,0.99,"Delitos cometidos mensualmente")
pautocor_delitos[1]

auto_delitos = acf(delitos_mensuales["delitos_cometidos"], nlags=36, alpha=0.05)






