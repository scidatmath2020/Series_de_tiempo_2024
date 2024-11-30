# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 17:40:57 2024

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
##############   FUNCIÓN DE ESTACIONALIDAD    ##################
################################################################
################################################################
'''
def estacionalidad(tabla,columna_datos,columna_tiempo,modelo,titulo):
    auxiliar = seasonal_decompose(tabla[columna_datos],model=modelo)
    # Convertir los componentes a un DataFrame
    componentes_df = pd.DataFrame({
        'fecha': tabla[columna_tiempo],
        'Observado': auxiliar.observed,
        'Tendencia': auxiliar.trend,
        'Estacionalidad': auxiliar.seasonal,
        'Errores': auxiliar.resid })
    
    componentes_largo = pd.melt(
        componentes_df,
        id_vars=['fecha'],     
        value_vars=['Observado', 'Tendencia', 'Estacionalidad', 'Errores'],
        var_name='Componente',     
        value_name='Valor') 
    
    componentes_largo['Componente'] = pd.Categorical(
        componentes_largo['Componente'],
        categories=['Observado', 'Tendencia', 'Estacionalidad', 'Errores'],
        ordered=True)
    
    desestacionalizado = pd.DataFrame({
        "fecha":tabla[columna_tiempo],
        "valor":componentes_df["Observado"]-componentes_df["Estacionalidad"]}) 
    
    traductor_modelo = {"additive":"Aditiva",
                        "multiplicative":"Multiplicactiva"}
    
    grafica = (ggplot(componentes_largo) +
             geom_line(aes(x='fecha', y='Valor',color='Componente')) +
             facet_wrap('~Componente',ncol=1,scales='free_y') +
             labs(x = "Fecha", 
             y = "Valor", 
             title = f"Componentes de la Descomposición {traductor_modelo[modelo]}\npara {titulo}") +
      theme(legend_position = "none")) 
    
    grafica_desestacional = (ggplot(desestacionalizado) +
                             geom_line(aes(x="fecha", y="valor")))
        
    return [componentes_largo,grafica,grafica_desestacional]

#%%

##### estacionalidad(tabla,columna_datos,columna_tiempo,modelo,titulo):
### Develve tres objetos: una tabla, una gráfica de estacionalidad, y gráfica desestacionalizada

estacion_delitos = estacionalidad(delitos_mensuales,
                                  "delitos_cometidos",
                                  "fecha_num",
                                  "multiplicative",
                                  "Delitos cometidos mensualmente")

estacion_delitos[2]



s = seasonal_decompose(delitos_mensuales.delitos_cometidos,model="additive")
s.plot()


