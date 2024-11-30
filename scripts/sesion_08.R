#install.packages("forecast")

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

tail(climas_nyc)


ggplot(ruidos) + 
  geom_line(aes(x = fecha, y = wn))

ggplot(ruidos) + 
  geom_line(aes(x = fecha, y = ca))

###########################################################################
###########################################################################
###########################################################################


################################################################
################################################################
##############   FUNCIÓN DE ESTACIONALIDAD    ##################
################################################################
################################################################

estacionalidad = function(tabla, columna_datos, columna_tiempo, modelo, titulo, frecuencia) {
  
  auxiliar = decompose(ts(tabla[,columna_datos],
                          frequency = frecuencia), type = modelo)
  
  componentes_df <- data.frame(
    fecha = tabla[,columna_tiempo],
    Observado = as.numeric(auxiliar$x),
    Tendencia = as.numeric(auxiliar$trend),
    Estacionalidad = as.numeric(auxiliar$seasonal),
    Errores = as.numeric(auxiliar$random)
  )
  
  componentes_largo <- pivot_longer(
    componentes_df,
    cols = c("Observado", "Tendencia", "Estacionalidad", "Errores"),
    names_to = "Componente",
    values_to = "Valor"
  )
  
  componentes_largo$Componente <- factor(componentes_largo$Componente,
                                         levels = c("Observado", "Tendencia", "Estacionalidad", "Errores"))
  
  desestacionalizado <- tibble(
    fecha = tabla[,columna_tiempo],
    valor = componentes_df$Observado - componentes_df$Estacionalidad
  )
  
  traductor_modelo = c("additive" = "Aditiva",
                       "multiplicative" = "Multiplicativa")
  
  grafica <- ggplot(componentes_largo) +
    geom_line(aes(x = fecha, y = Valor, color = Componente)) +
    facet_wrap(~Componente, ncol = 1, scales = "free_y") +
    scale_y_continuous(labels = comma) +
    labs(x = "Fecha", y = "Valor", 
         title = paste("Componentes de la Descomposición", 
                       traductor_modelo[modelo], "para", titulo)) +
    theme(legend.position = "none")
  
  grafica_desestacional <- ggplot(desestacionalizado, aes(x = fecha, y = valor)) +
    geom_line()
  
  return(list(componentes_largo, grafica, grafica_desestacional))
}

##################################################################################

### estacionalidad(tabla, columna_datos, columna_tiempo, modelo, titulo, frecuencia)
### Develve tres objetos: una tabla, una gráfica de estacionalidad, y gráfica desestacionalizada

estacion_delitos = estacionalidad(delitos_mensuales,
                                  "delitos_cometidos",
                                  "fecha_num",
                                  "multiplicative",
                                  "Delitos cometidos mensualmente",
                                  12)

estacion_delitos[[2]]
estacion_delitos[[1]]
estacion_delitos[[3]]

#####################################################
# acf(columna, lag.max = nlags, plot = TRUE, ci.type="ma")

acf(delitos_mensuales$delitos_cometidos,24,plot=TRUE,ci.type="ma")

s = decompose(ts(delitos_mensuales$delitos_cometidos,
             frequency = 12), type = "additive")

plot(s)




