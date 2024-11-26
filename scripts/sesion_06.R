#install.packages("zoo")

library(tidyverse)
library(lubridate)
library(zoo)

# Establecer el directorio de trabajo (ajustar según tu sistema)
setwd("C:/Users/Usuario/Documents/scidata/24_st/data/sismos")

# Leer el archivo CSV
procesado_sismos = read.csv("sismos_procesado.csv", encoding = "latin1")

# Convertir la columna 'Mes_Año' en formato de fecha
procesado_sismos$Mes_Año <- as.Date(procesado_sismos$Mes_Año, format = "%d/%m/%Y")
procesado_sismos

# Visualizar la serie únicamente para Guerrero
ggplot(data = procesado_sismos, aes(x = Mes_Año, y = Guerrero)) +
  geom_line(color = "red") +
  labs(
    x = "Mes/Año",                    # Título del eje X
    y = "Magnitud promedio",          # Título del eje Y
    title = "Magnitud promedio por región"  # (Opcional) Título del gráfico
  ) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

# Rellenar los huecos en la columna Guerrero usando interpolación lineal
procesado_sismos = procesado_sismos %>%
  mutate(Guerrero_sinna = na.approx(Guerrero, na.rm = FALSE))
procesado_sismos


# Visualizar la serie para Guerrero después de rellenar huecos
ggplot(data = procesado_sismos, 
       aes(x = Mes_Año, y = Guerrero_sinna)) +
  geom_line(color = "red") +
  labs(
    x = "Mes/Año",                    # Título del eje X
    y = "Magnitud promedio",          # Título del eje Y
    title = "Magnitud promedio por región"  # (Opcional) Título del gráfico
  ) +
  scale_x_date(date_labels = "%b %Y",
               breaks = seq.Date(from = min(procesado_sismos$Mes_Año), 
                                 to = max(procesado_sismos$Mes_Año), 
                                 by = "1 years")) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1,size=5))

###############################################
###########      RUÍDO BLANCO       ###########
###############################################


procesado_sismos$ruido_blanco = rnorm(length(procesado_sismos$Guerrero_sinna),
                      mean = mean(procesado_sismos$Guerrero_sinna, na.rm = TRUE),
                      sd = sd(procesado_sismos$Guerrero_sinna, na.rm = TRUE))

procesado_sismos

ggplot(data = procesado_sismos) +
  geom_line(mapping=aes(x = Mes_Año, y = Guerrero_sinna), color = "red") +
  geom_line(mapping=aes(x = Mes_Año, y = ruido_blanco), color = "blue") +
  labs(
    x = "Mes/Año",                    # Título del eje X
    y = "Magnitud promedio",          # Título del eje Y
    title = "Magnitud promedio por región"  # (Opcional) Título del gráfico
  ) +
  scale_x_date(date_labels = "%b %Y",
               breaks = seq.Date(from = min(procesado_sismos$Mes_Año), 
                                 to = max(procesado_sismos$Mes_Año), 
                                 by = "1 years")) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1,size=5))


###############################################
########      CAMINATA ALEATORIA       ########
###############################################

# Generamos los pasos

pasos <- rnorm(length(procesado_sismos$Guerrero_sinna),
               mean = 0,
               sd = 1)

# Calcular la suma acumulada para obtener la caminata aleatoria
CA <- cumsum(pasos)

# Añadir la columna 'CA' al dataframe
procesado_sismos$CA <- CA

ggplot(data = procesado_sismos) +
  #geom_line(mapping=aes(x = Mes_Año, y = Guerrero_sinna), color = "red") +
  geom_line(mapping=aes(x = Mes_Año, y = CA), color = "blue") +
  labs(
    x = "Mes/Año",                    # Título del eje X
    y = "Magnitud promedio",          # Título del eje Y
    title = "Magnitud promedio por región"  # (Opcional) Título del gráfico
  ) +
  scale_x_date(date_labels = "%b %Y",
               breaks = seq.Date(from = min(procesado_sismos$Mes_Año), 
                                 to = max(procesado_sismos$Mes_Año), 
                                 by = "1 years")) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1,size=5))
