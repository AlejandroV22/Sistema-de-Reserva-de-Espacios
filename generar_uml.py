import pydotplus

# Cargar el archivo .dot
with open("sistema.dot") as f:
    dot_data = f.read()

# Crear gráfico desde el DOT
graph = pydotplus.graph_from_dot_data(dot_data)

# Guardar como imagen
graph.write_png("uml_diagrama.png")

print("¡Diagrama generado correctamente!")