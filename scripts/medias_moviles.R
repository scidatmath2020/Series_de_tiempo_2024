library(tidyverse)
library(zoo)
library(forecast)
library(TTR)

################################################################################
################################################################################

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

#############################################################################

#Preprocesamiento de datos: convertir a Serie de tiempo

#################   COLUMNAS TS


delitos_mensuales_ts <- ts(
  delitos_mensuales$delitos_cometidos,
  start = c(2012, 1),  # Año 2012, mes 1 (enero)
  frequency = 12       # Mensual
)


tipo_cambio_ts <- ts(
  tipo_cambio$Cambio,
  start = c(1954, 4 + 19 / 30),  # Año y mes aproximado con día fraccional
  frequency = 252               # Frecuencia laboral
)


climas_nyc_ts <- zoo(
  climas_nyc$temp_c,
  order.by = seq(
    from = as.POSIXct("2013-01-01 01:00"),
    to = as.POSIXct("2013-12-30 18:00"),
    by = "hour"
  )
)

ruidos_ts <- ts(
  ruidos$wn,
  start = c(2024, as.numeric(format(as.Date("2024-11-29"), "%j")) / 365),  # Año y día fraccional
  frequency = 365                  # Frecuencia diaria
)


################################################################################
################################################################################


SMA(delitos_mensuales_ts,n=12)
plot(SMA(delitos_mensuales_ts,n=12))

delitos_ets = ets(delitos_mensuales_ts)
plot(delitos_mensuales_ts)
lines(delitos_ets$fitted,col="red")

?ets

delitos_ets_exp_simple = ets(delitos_mensuales_ts,model="ANN")
plot(delitos_mensuales_ts)
lines(delitos_ets_exp_simple$fitted,col="red")


delitos_ets_HW_doub = ets(delitos_mensuales_ts,model="AAN")
plot(delitos_mensuales_ts)
lines(delitos_ets_HW$fitted,col="red")

delitos_ets_HW_trip = ets(delitos_mensuales_ts,model="AAA")
plot(delitos_mensuales_ts)
lines(delitos_ets_HW_trip$fitted,col="red")