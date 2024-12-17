library(tidyverse)
library(lubridate)
library(tseries)
library(forecast)
library(zoo)
library(xts)

#install.packages("dygraphs")

library(dygraphs)

##############################################


?autoplot

class(nottem)

plot(nottem)

autoplot(nottem)
plot(decompose(nottem))

autoplot(decompose(nottem))

##### ¿Es estacionaria?

##### Test de Dickey-Fuller para estacionariedad
### Si el p-valor es pequeño: rechazar H0 y la serie sí es estacionaria
### Si el p-valor es grande: No rechazar H0 y la serie NO es estacionaria

adf.test(nottem)

### Recordemos que p-valor pequeño significa p-valor < 0.05

### Por lo tanto la serie sí es estacionaria

##############################################

faltantes = read.csv("C:\\Users\\Usuario\\Documents\\scidata\\24_st\\data\\Rmissing.csv")


faltantes = ts(faltantes$mydata)
faltantes

class(faltantes)

######## Comprobar si hay NA:
summary(faltantes)

######## Graficar
autoplot(faltantes)
plot(faltantes)


##############################################
############# Rellenar faltantes #############
##############################################

##### rellenando con el vecino inmediato anterior: na.locf(serie)
faltantes_via = na.locf(faltantes)
autoplot(faltantes_via)

##### rellenando con el vecino inmediato superior: na.locf(serie,fromLast=TRUE)
faltantes_vis = na.locf(faltantes,fromLast = TRUE)
autoplot(faltantes_vis)

##### rellenando con un valor específico: na.fill(serie,valor)
faltantes_2024 = na.fill(faltantes,mean(faltantes,na.rm=TRUE))
autoplot(faltantes_2024)

##### rellenando con interpolación: na.interp(serie)
faltantes_interpolacion = na.interp(faltantes)
autoplot(faltantes_interpolacion)

##############################################
#############  Valores atípicos  #############
##############################################


##### Identificación de los outliers (valores atípicos)
faltantes_atipicos = tsoutliers(faltantes)

##### Mostrar valores atípicos
faltantes[faltantes_atipicos$index]


##### Limpieza de los outliers
autoplot(faltantes)
faltantes_limpio = tsclean(faltantes,replace.missing = FALSE)
autoplot(faltantes_limpio)

?tsclean

##############################################
########### Serie de tiempo COVID ############
##############################################

covid = read.csv("C:\\Users\\Usuario\\Documents\\scidata\\24_st\\data\\covid\\serie_covid.csv")

head(covid)  #tail(covid)

class(covid$Fecha)


covid$Fecha = as.Date(covid$Fecha, format="%d/%m/%Y")
class(covid$Fecha)

###### Creamos el xts (es una serie de tiempo "especial")


covid_ts = xts(covid[,2],order.by=covid$Fecha)

class(covid_ts)

View(covid_ts)

names(covid_ts) = "Total"

autoplot(covid_ts)

covid_ts = na.fill(covid_ts,0)

############# Estacionariedad

adf.test(covid_ts)

#############

mi_arima = auto.arima(covid_ts)



# 10, 3, 4
p_min = 1
p_max = 10
q_min = 5
q_max = 7
P_min = 2
P_max = 5

auto.arima(covid_ts,
           max.p = 12,
           start.p = 1)

#############

mi_arima
mi_arima_pred = forecast(mi_arima,h=396)

autoplot(mi_arima_pred)
dygraphs::dygraph(cbind(mi_arima_pred$x,mi_arima_pred$mean))









