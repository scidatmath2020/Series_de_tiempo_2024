library(forecast)
library(lubridate)
library(tseries)

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

# Modelo AR(1)
ar1_model <- Arima(ts_train, order = c(1, 0, 0), include.mean = TRUE)
ar1_forecast <- forecast(ar1_model, h = length(ts_test))

# Modelo AR(2)
ar2_model <- Arima(ts_train, order = c(2, 0, 0), include.mean = TRUE)
ar2_forecast <- forecast(ar2_model, h = length(ts_test))


# Modelo AR(automático)

arautomatico_model <- ar.mle(ts_train, aic = TRUE)
arautomatico_model$order

arautomatico_forecast <- forecast(arautomatico_model, h = length(ts_test))



# Comparar los valores reales y predicciones
resultados <- data.frame(
  Fecha = time(ts_test),
  Real = as.numeric(ts_test),
  Predicciones_AR1 = as.numeric(ar1_forecast$mean),
  Predicciones_AR2 = as.numeric(ar2_forecast$mean),
  Predicciones_ARauto = as.numeric(arautomatico_forecast$mean)
)

ggplot(resultados, aes(x = Fecha)) +
  geom_line(aes(y = Real, color = "Real")) +
  geom_line(aes(y = Predicciones_AR1, color = "Predicciones AR(1)")) +
  geom_line(aes(y = Predicciones_AR2, color = "Predicciones AR(2)")) +
  geom_line(aes(y = Predicciones_ARauto, color = "Predicciones AR Auto")) +
  labs(title = "Comparación de modelos AR",
       y = "Delitos Cometidos",
       x = "Fecha") +
  scale_color_manual(name = "Modelos", 
                     values = c("Real" = "blue", 
                                "Predicciones AR(1)" = "orange", 
                                "Predicciones AR(2)" = "green", 
                                "Predicciones AR Auto" = "red")) +
  theme_minimal()
###################################################

# Ajustar el modelo AR
optimal_lags <- ar.mle(ts_train)$order  # Calcular los rezagos óptimos
arautomatico_model <- ar.mle(ts_train, order.max = optimal_lags)  # Ajustar el modelo AR

summary(arautomatico_model_2)


# Generar predicciones para 2024
n_pred <- 12
futuras_predicciones <- predict(arautomatico_model, n.ahead = 41)

# Crear la serie predicha como un ts (serie temporal)
predicciones_ts <- ts(futuras_predicciones$pred, 
                      start = c(2021, 8), 
                      frequency = 12)

# Combinar las series (original y predicción)
ts_completa <- ts(c(ts_delitos, predicciones_ts), 
                  start = start(ts_delitos), 
                  frequency = 12)

# Graficar con ggplot2
autoplot(ts_delitos, series = "Serie Original") +
  autolayer(predicciones_ts, series = "Predicciones", color = "orange") +
  labs(title = "Serie Original y Predicciones para 2024",
       x = "Año",
       y = "Delitos cometidos") +
  scale_color_manual(values = c("blue", "orange")) +
  theme_minimal()



###################################################

