
data_1 <- data.frame(
  W = c(0.896766, 0.624211, 0.228907, 0.633909, 0.841789),
  X = c(0.881690, 0.955746, 0.510997, 0.367079, 0.535549),
  Y = c(0.033998, 0.858047, 0.827106, 0.404721, 0.942269),
  Z = c(0.254148, 0.170809, 0.957140, 0.715977, 0.525564)
)
rownames(data_1) = c("A", "B", "C", "D", "E")

data_1["SUMA_W_Y"] = data_1["W"] + data_1["Y"]


##### Filtremos las filas donde los valores de la columna Z sean
##### mayores que 0.5
data_1[data_1["Z"] > 0.5,]

##### Filtremos las filas donde los valores de la columna Z sean
##### mayores que 0.5 o los valore de la columna X sean menores
##### que 0.9

data_1[data_1["Z"] > 0.5 | data_1["X"] < 0.9,]


##### Filtremos las filas donde los valores de la columna W sean
##### menores que 0.7 y los valore de la columna Y sean mayores
##### que 0.6

data_1[data_1["W"] < 0.7 & data_1["Y"] > 0.6,]

##### Manejo de valores faltantes

df <- data.frame(
  A = c(1, 2, NA),
  B = c(5, NA, NA),
  C = c(1, 2, 3)
)
df

View(df)

#### Eliminación de filas con valores faltantes

# crea un nuevo dataframe sin las filas con valores faltantes
df_na_filas = na.omit(df) 
df_na_filas

# crea un nuevo dataframe sin las columnas con valores faltantes
df_na_columnas = df[   , colSums(is.na(df)) == 0] 
df_na_columnas

#######################################################
library(tidyverse)
#######################################################

############# Rellenando con 0
df_na_rellenos_0 = df %>% mutate_all(~ ifelse(is.na(.), 0, .))
df_na_rellenos_0

############# Rellenando con promedios
df_na_rellenos_media = df %>%
  mutate(across(everything(), ~ ifelse(is.na(.), mean(., na.rm = TRUE), .)))

df_na_rellenos_media

####### Agrupamiento de tablas

ventas_vendedor = data.frame(
  compania = c("GOOG", "GOOG", "FB", "MSFT", "FB", "MSFT"),
  vendedor = c("Sam", "Carlos", "Vanessa", "Carla", "Sara", "Luis"),
  ventas = c(182, 199, 157, 181, 174, 152)
)

ventas_vendedor

####### calcular el total de ventas por compañía

ventas_totales = ventas_vendedor %>% 
  group_by(compania) %>% 
  summarize(sum(ventas))

ventas_totales

