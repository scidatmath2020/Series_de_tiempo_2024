# Cargar las librerías necesarias
library(tidyverse)
library(lubridate)

# Establecer el directorio de trabajo (ajustar según tu sistema)
setwd("C:/Users/Usuario/Documents/scidata/24_st/data/sismos")

# Leer el archivo CSV
procesado_sismos <- read_csv("sismos_procesado.csv", locale = locale(encoding = "latin1"))

# Ver las primeras filas
head(procesado_sismos)

# Resumen descriptivo
summary(procesado_sismos)

# Conteo de valores faltantes por columna
colSums(is.na(procesado_sismos))

# Conteo de valores faltantes en la columna Guerrero
sum(is.na(procesado_sismos$Guerrero))

# Convertir la columna Mes_Año a tipo fecha
procesado_sismos <- procesado_sismos %>%
  mutate(Mes_Año = dmy(Mes_Año))  # Suponiendo formato día/mes/año

# Graficar las series de tiempo
ggplot(data = procesado_sismos) +
  geom_line(aes(x = Mes_Año, y = Guerrero), color = "red") +
  geom_line(aes(x = Mes_Año, y = Oaxaca), color = "blue") +
  geom_line(aes(x = Mes_Año, y = Puebla), color = "purple") +
  labs(
    x = "Mes/Año",                      # Título del eje X
    y = "Magnitud promedio",            # Título del eje Y
    title = "Magnitud promedio por región"  # (Opcional) Título del gráfico
  ) +
  theme_minimal() +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1)  # Rotar etiquetas del eje X
  )
