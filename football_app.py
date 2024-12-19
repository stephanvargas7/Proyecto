import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from io import BytesIO

# Título de la app
st.title("Resultados de Fútbol - API Football Data")

# Token de autenticación (reemplázalo con tu token real)
API_TOKEN = "4b2aff117b894989bfb9d085cfce9cc4"  # Coloca aquí tu token

# URL base de la API de football-data.org
BASE_URL = "https://api.football-data.org/v4/competitions/PL/matches"  # Ejemplo: Premier League

# Función para obtener datos desde la API
@st.cache_data  # Cache para optimizar rendimiento
def fetch_football_data(url, token):
    headers = {"X-Auth-Token": token}  # Token en los headers
    try:
        # Realizar la solicitud a la API
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lanza error si algo falla
        data = response.json()  # Convertir respuesta a JSON
        
        # Extraer datos relevantes para el DataFrame
        matches = data.get("matches", [])  # Extraer la lista de partidos
        match_data = []
        for match in matches:
            match_info = {
                "Fecha": pd.to_datetime(match["utcDate"]).strftime('%Y-%m-%d'),  # Formatear fecha
                "Equipo Local": match["homeTeam"]["name"],
                "Equipo Visitante": match["awayTeam"]["name"],
                "Marcador Local": match["score"]["fullTime"]["home"] if match["score"]["fullTime"]["home"] is not None else 0,
                "Marcador Visitante": match["score"]["fullTime"]["away"] if match["score"]["fullTime"]["away"] is not None else 0,
            }
            match_data.append(match_info)
        
        return pd.DataFrame(match_data)  # Convertir a DataFrame
    except Exception as e:
        st.error(f"Error al obtener datos: {e}")
        return pd.DataFrame()

# Función para convertir el DataFrame a Excel
def convert_df_to_excel(df):
    output = BytesIO()  # Crear un buffer en memoria
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Partidos")  # Exportar DataFrame a Excel
    processed_data = output.getvalue()  # Obtener el contenido del archivo
    return processed_data

# Llamar a la función de consumo de datos
st.subheader("Datos de Partidos de la UEFA CAHMPIONS LEAGUE")
data = fetch_football_data(BASE_URL, API_TOKEN)

# Mostrar datos si no está vacío
if not data.empty:
    st.write("Vista previa de los datos:")
    st.dataframe(data.head())  # Mostrar primeras filas

    # Botón para descargar el DataFrame como archivo Excel
    st.download_button(
        label="Descargar datos como Excel",
        data=convert_df_to_excel(data),
        file_name="partidos_premier_league.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Gráfica 1: Marcadores apilados
    st.subheader("Visualización de Marcadores")
    fig, ax = plt.subplots()
    
    # Graficar los marcadores de manera apilada
    data.plot(kind="bar", x="Fecha", y=["Marcador Local", "Marcador Visitante"], ax=ax, stacked=True)

    # Configurar eje X para que no se vea amontonado
    ax.xaxis.set_major_locator(MaxNLocator(10))  # Mostrar máximo 10 etiquetas en el eje X
    plt.xticks(rotation=45, ha="right")  # Rotar las etiquetas

    # Agregar título y etiquetas
    plt.title("Resultados de Partidos")
    plt.xlabel("Fecha")
    plt.ylabel("Goles")

    # Mostrar gráfica en Streamlit
    st.pyplot(fig)

    # Gráfica 4: Torta (Pie Chart)
    st.subheader("Distribución de Resultados (Local/Visitante/Empate)")

    # Calcular victorias locales, visitantes y empates
    local_wins = data[data["Marcador Local"] > data["Marcador Visitante"]].shape[0]
    visitor_wins = data[data["Marcador Visitante"] > data["Marcador Local"]].shape[0]
    draws = data[data["Marcador Local"] == data["Marcador Visitante"]].shape[0]

    # Crear gráfica
    fig4, ax4 = plt.subplots()
    ax4.pie(
        [local_wins, visitor_wins, draws],
        labels=["Victorias Locales", "Victorias Visitantes", "Empates"],
        autopct="%1.1f%%",
        startangle=90,
        colors=["#1f77b4", "#ff7f0e", "#2ca02c"]
    )
    plt.title("Distribución de Resultados")
    st.pyplot(fig4)

    # Gráfica 6: Histograma
    st.subheader("Distribución de Goles Locales y Visitantes")
    fig6, ax6 = plt.subplots()
    ax6.hist(data["Marcador Local"], bins=5, alpha=0.7, label="Marcador Local", color="#1f77b4")
    ax6.hist(data["Marcador Visitante"], bins=5, alpha=0.7, label="Marcador Visitante", color="#ff7f0e")
    plt.title("Distribución de Goles")
    plt.xlabel("Goles")
    plt.ylabel("Frecuencia")
    plt.legend()
    st.pyplot(fig6)

else:
    st.warning("No se encontraron datos. Verifica el token o la API.")



