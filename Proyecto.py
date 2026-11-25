import pandas as pd
import streamlit as st

TRES = ["Boyacá", "Casanare", "Bogotá, D.C."]

st.title("Del paramo al llano y a la capital ¿Que tan segura es el agua?")
st.write("El IRCA va de 0 a 100, entre mayor sea el numero es peor la calidad del agua")

# Leer los datos y limpiarlos quitar las filas que tienen #todos
df = pd.read_csv("AGUA.csv" , thousands=",")
df = df[df["Municipio"] != "#TODOS"] 
df = df[df["Departamento"].isin(TRES)] 

# Elejir que valores mostrar y quitar los municipios sin registros
departamentos = st.multiselect("Departamentos a comparar", TRES, default=TRES)
año_inicio, año_fin = st.slider("Años", 2019, 2025, (2019, 2025))
quitar_ceros = st.checkbox("Quitar municipios con IRCA = 0", value=True)

# que la persona eliga solo los 3 departamentos comparados
datos = df[df["Departamento"].isin(departamentos)]
datos = datos[datos["Año"].between(año_inicio, año_fin)]

if quitar_ceros:
    datos = datos[datos["IRCA"] != 0]

# si no se elige que datos poner no hay datos con esas opciones
if datos.empty:
    st.warning("No hay datos con esas opciones.")
    st.stop()

# Sacar el promedio por departamento
columnas = st.columns(len(departamentos))
for columna, depto in zip(columnas, departamentos):
    d = datos[datos["Departamento"] == depto]
    if d.empty:
        columna.metric(depto, "sin datos")
    else:
        columna.metric(depto, round(d["IRCA"].mean(), 2))

# Grafica lineal para mostrar en streamlit
st.subheader("IRCA promedio por año")
por_año = datos.pivot_table(index="Año", columns="Departamento", values="IRCA", aggfunc="mean")
st.line_chart(por_año)

# Tabla con las estadisticas promedio minimo mediana y maximo
st.subheader("Comparación de estadísticas")
resumen = datos.groupby("Departamento")["IRCA"].agg(["count", "mean", "median", "min", "max"])
resumen.columns = ["registros", "promedio", "mediana", "mínimo", "máximo"]
resumen = resumen.round(2)
st.dataframe(resumen)

st.subheader("Promedio general por departamento")
st.bar_chart(resumen["promedio"])

# tabla con los municipios con IRCA mas altos en cada año
st.subheader("Municipio con mayor IRCA en cada año")
filas_max = datos.loc[datos.groupby(["Departamento", "Año"])["IRCA"].idxmax()]
tabla_max = filas_max[["Departamento", "Año", "Municipio", "IRCA"]]
st.dataframe(tabla_max, hide_index=True)