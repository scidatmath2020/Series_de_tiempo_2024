library(forecast)
library(lubridate)
library(tseries)
library(lmtest)

# Leer y preprocesar los datos
delitos_mensuales = read.csv("delitos_mensuales/delitos_mensuales.csv", encoding = "latin1")
delitos_mensuales$fecha_num = my(delitos_mensuales$fecha_num)

# Crear la serie temporal
ts_delitos <- ts(delitos_mensuales$delitos_cometidos, 
                 start = c(year(min(delitos_mensuales$fecha_num)), month(min(delitos_mensuales$fecha_num))), 
                 frequency = 12)

# Dividir en datos de entrenamiento y prueba (80%-20%)
n <- length(ts_delitos)
train_size <- floor(0.8 * n)
ts_train <- window(ts_delitos, start = c(2012, 1), end = c(2012 + (train_size - 1) %/% 12, (train_size - 1) %% 12 + 1))
ts_test <- window(ts_delitos, start = c(2012 + train_size %/% 12, train_size %% 12 + 1))

########################################################################

ARMA <- Arima(ts_train, order = c(12, 0, 2), include.mean = TRUE,method="ML")
predicciones_prueba_ARMA <- forecast(ARMA, h = length(ts_test))

resultados <- data.frame(
  Fecha = time(ts_test),
  Real = as.numeric(ts_test),
  predicciones_prueba_ARMA = as.numeric(predicciones_prueba_ARMA$mean)
)

ggplot(resultados, aes(x = Fecha)) +
  geom_line(aes(y = Real, color = "blue")) +
  geom_line(aes(y = predicciones_prueba_ARMA, color = "red")) +
  labs(title = "Comparación de modelos ARMA",
       y = "Delitos Cometidos",
       x = "Fecha") +
  theme_minimal()


########################################################################

informacion_arma = function(a,b,columna_entrenamiento){
  mi_ARMA = Arima(columna_entrenamiento, order=c(a,0,b), 
                  include.mean = TRUE, 
                  method="ML")
  pvalores = coeftest(mi_ARMA)[,4]
  akaike = mi_ARMA$aic
  limite_ar = paste0("ar",a)
  limite_ma = paste0("ma",b)
  significativo_ar = limite_ar %in% names(pvalores<0.05)
  significativo_ma = limite_ma %in% names(pvalores<0.05)
  limites_significativos = significativo_ar + significativo_ma
  total_significativos = length(mi_ARMA$coef[pvalores <0.05])
  salida = data.frame("AIC"=akaike,
                      "limites_significativos"=limites_significativos,
                      "total_significativos"=total_significativos)
  rownames(salida)[1] = paste0("ARMA_",a,"_0_",b)
  return(salida)  
}

################################################################################

max_ar <- 12
max_ma <- 12

armas <- list()  # Lista para almacenar los resultados

for (a in 1:max_ar) {
  for (b in 1:max_ma) {
    # Usar tryCatch para manejar errores
    resultado <- tryCatch(
      {
        informacion_arma(a, b, ts_train)  # Intentar ejecutar la función
      },
      error = function(e) {
        # Capturar el error y mostrar en qué paso ocurrió
        cat("Error en a =", a, ", b =", b, ":", conditionMessage(e), "\n")
        return(NULL)  # Devolver NULL para que no agregue nada en caso de error
      }
    )
    # Agregar el resultado a la lista si no es NULL
    if (!is.null(resultado)) {
      armas <- append(armas, list(resultado))
    }
  }
}

resultados_armas = do.call(rbind,armas)

resultados_armas_ordenados = resultados_armas %>%
  arrange(desc(limites_significativos), AIC, total_significativos)


####################################################################


mi_ARMA <- Arima(ts_train, order = c(12, 0, 6), include.mean = TRUE,method="ML")
predicciones_prueba_mi_ARMA <- forecast(mi_ARMA, h = length(ts_test))



resultados <- data.frame(
  Fecha = time(ts_test),
  Real = as.numeric(ts_test),
  predicciones_prueba_mi_ARMA = as.numeric(predicciones_prueba_mi_ARMA$mean)
)


ggplot(resultados, aes(x = Fecha)) +
  geom_line(aes(y = Real, color = "Real")) +
  geom_line(aes(y = predicciones_prueba_mi_ARMA, color = "Predicciones ARMA")) +
  labs(title = "Comparación de modelos ARMA",
       y = "Delitos Cometidos",
       x = "Fecha") +
  scale_color_manual(name = "Modelos", 
                     values = c("Real" = "blue", 
                                "Predicciones ARMA" = "orange")) +
  theme_minimal()

