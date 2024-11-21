vector = c(1,2,23,4,5,2,5,6)

cuadrados = vector**2

subvector = vector[c(1,3)]

subvector

personas = c("Alicia","Juan","Rodrigo","Raúl","Ricardo","José")

matriz_nombres = matrix(personas,nrow=3)
matriz_nombres


tabla = data.frame("Name" = c("Alice", "Bob", "Charlie", "David", "Eve"),
                    "Age" = c(24, 27, 22, 32, 29),
                    "City" = c("New York", "Los Angeles", "Chicago", "Houston", "Phoenix"),
                    "Score" = c(88, 92, 85, 95, 90))

tabla

tabla["Age"]

tabla[c("Name","Score")]

tabla[c("Score","Name")]

rownames(tabla) = c("stu01","stu02","stu03","stu04","stu05")
tabla

colnames(tabla) = c("Alumno","Edad","Ciudad","Puntaje")
tabla

data_1 <- data.frame(
  W = c(0.896766, 0.624211, 0.228907, 0.633909, 0.841789),
  X = c(0.881690, 0.955746, 0.510997, 0.367079, 0.535549),
  Y = c(0.033998, 0.858047, 0.827106, 0.404721, 0.942269),
  Z = c(0.254148, 0.170809, 0.957140, 0.715977, 0.525564)
)
rownames(data_1) = c("A", "B", "C", "D", "E")

data_1

data_1["W"] + data_1["Y"]

data_1

data_1["Suma_W_Y"] = data_1["W"] + data_1["Y"]
data_1

suma = data_1["W"] + data_1["Y"]
suma

data_1

data_1[c("A","B","D"),  ]

data_1[c(1,2,4),  ]

data_1[c("B","C","E"),c("W","Y")]

data_1 > 0.5

data_1_condicion = data_1
data_1_condicion[data_1_condicion <= 0.5] = NA
data_1_condicion




