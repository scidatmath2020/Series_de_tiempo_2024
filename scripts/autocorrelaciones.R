library(tidyverse)
library(lubridate)
library(stats)
library(forecast)
library(scales)


###########################################################################
###########################################################################
###########################################################################

setwd("C:\\Users\\Usuario\\Documents\\scidata\\24_st\\data\\")

###################      Cargar y preprocesar datos

# Ajustar la ruta de los archivos según tu sistema
ruta = "C:\\Users\\Usuario\\Documents\\scidata\\24_st\\data"


# Cargar tablas
delitos_mensuales = read.csv(paste0(ruta,"\\delitos_mensuales\\delitos_mensuales.csv"),
                             fileEncoding = "latin1")

tipo_cambio = read.csv(paste0(ruta,"\\tipo_de_cambio\\tipo_cambio.csv"),
                       fileEncoding = "latin1")

climas_nyc = read.csv(paste0(ruta,"\\climas_nyc\\climas_procesado.csv"))

ruidos = read.csv(paste0(ruta,"\\ruidos\\ruidos.csv"))

#############################################################################
#Preprocesamiento de datos (conversión de fechas y frecuencia)

delitos_mensuales$fecha_num = my(delitos_mensuales$fecha_num)

tipo_cambio$Fecha = dmy(tipo_cambio$Fecha)

climas_nyc$datetime = as.POSIXct(climas_nyc$datetime, format = "%d/%m/%Y %H:%M")

ruidos$fecha = dmy(ruidos$fecha)

#Visualizar las gráficas
ggplot(delitos_mensuales) + 
  geom_line(aes(x = fecha_num, y = delitos_cometidos, color = factor(Año))) + 
  labs(x = "Año", y = "Delitos Cometidos")

ggplot(tipo_cambio) + 
  geom_line(aes(x = Fecha, y = Cambio))

ggplot(climas_nyc) + 
  geom_line(aes(x = datetime, y = temp_c))

ggplot(ruidos) + 
  geom_line(aes(x = fecha, y = wn))

ggplot(ruidos) + 
  geom_line(aes(x = fecha, y = ca))

###########################################################################
###########################################################################
###########################################################################

#########   Autocorrelación


#####################################################
# acf(columna, lag.max = nlags, plot = TRUE, ci.type="ma")

acf(delitos_mensuales$delitos_cometidos,24, plot=TRUE, ci.type="ma")
acf(climas_nyc$temp_c,24*7, plot=TRUE, ci.type="ma")


#########   Autocorrelación parcial

pacf(delitos_mensuales$delitos_cometidos,36, plot=TRUE)

pacf(ruidos$ca,36, plot=TRUE)




delitos_mensuales$fecha_num[1:5]
