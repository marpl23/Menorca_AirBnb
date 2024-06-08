import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import seaborn as sns
import streamlit as st
import folium
from folium.plugins import FastMarkerCluster
from streamlit_folium import st_folium

# --------------------CONFIGURACIÓN DE LA PÁGINA----------------------------#
# layout="centered" or "wide".
st.set_page_config(page_title='Análisis: AirBnbs de Menorca', layout='wide', page_icon='👋')
image_path = r'C:\Users\maarp\OneDrive\Escritorio\bootcamp_data\14_Data_Storytelling\MENORCA HEAD.png'

# Mostrar la imagen de cabecera
st.image(image_path, use_column_width=True)

# Cargar los datos
@st.cache_data
def load_data():
    listings = pd.read_csv(r'C:\Users\maarp\OneDrive\Escritorio\bootcamp_data\14_Data_Storytelling\data\listings.csv')
    listings_data = pd.read_csv(r'C:\Users\maarp\OneDrive\Escritorio\bootcamp_data\14_Data_Storytelling\data\listings_data.csv')
    target_columns = ["id", "property_type", "accommodates", "first_review", "review_scores_value", "review_scores_cleanliness", "review_scores_location", "review_scores_accuracy", "review_scores_communication", "review_scores_checkin", "review_scores_rating", "maximum_nights", "host_is_superhost", "host_about", "host_response_time", "host_response_rate", "amenities"]
    nuevo_listings = pd.merge(listings, listings_data[target_columns], on='id', how='left')
    return nuevo_listings

# Cargar los datos
nuevo_listings = load_data()

# Crear un menú lateral
st.sidebar.title("Menú")
option = st.sidebar.selectbox(
    "¿Qué quieres ver?",
    ["Inicio", "Análisis de las Propiedades", "Análisis de los Hosts", "Conclusión"]
)

# Importar datos y eliminar outliers
nuevo_listings.dropna(axis=1, how='all')

nuevo_listings.drop('last_review', axis=1, inplace=True)
nuevo_listings.drop('reviews_per_month', axis=1, inplace=True)

nuevo_listings.drop(columns=["neighbourhood"])


Q1 = nuevo_listings['price'].quantile(0.25)
Q3 = nuevo_listings['price'].quantile(0.75)

IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

nuevo_listings['price'] = nuevo_listings['price'].apply(lambda x: lower_bound if x < lower_bound else upper_bound if x > upper_bound else x)

nuevo_listings['price'].fillna(nuevo_listings['price'].mean(), inplace=True)


# Mostrar Inicio
if option == "Inicio":
    st.title('Análisis exploratorio: AirBnbs de Menorca')
    st.subheader('Indagando en datos sobre distribución geográfica, los huéspedes y los hosts')

    st.header('Introducción')
    st.markdown("""
        Vamos a realizar la visualización y análisis de los datos de Menorca extraídos de 
        Insideairbnb.com, un sitio web en el que se publican conjuntos de datos extraídos de la 
        web de "instantáneas" de diferentes ciudades
        """)
    st.markdown("""
        Este análisis tiene como objetivo comprender la oferta de Airbnb en Menorca, identificar 
        patrones de precios y disponibilidad, y evaluar el impacto del turismo en la isla.
        """)
    st.markdown('---')
    
    st.markdown("""
        En esta aplicación podrás explorar diversos aspectos relacionados con las propiedades y los hosts en Menorca.
        Utiliza el menú lateral y superior para navegar entre las diferentes secciones del análisis. Los archivos con los que vamos a trabajar son los siguientes:
        """)
    st.markdown("""
                
                `listings.csv.gz`: Detailed Listings data
                
                `calendar.csv.gz`: Detailed Calendar Data
                
                `reviews.csv.gz`: Detailed Review Data
                
                `listings.csv`: Summary information and metrics for listings in Menorca (good for visualisations)
                
                `reviews.csv`: Summary Review data and Listing ID (to facilitate time based analytics and visualisations linked to a listing)
                
                `neighbourhoods.csv`: Neighbourhood list for geo filter. Sourced from city or open source GIS files
                
                `neighbourhoods.geojson`: GeoJSON file of neighbourhoods of the city
                """)

# Mostrar Propiedades
elif option == "Análisis de las Propiedades":
    st.title("Análisis Exploratorio de los AirBnb de Menorca")
    
    sub_menu = ["Mapa", "Vecindario", "Precios", "Propiedades", "Huéspedes", "Puntuaciones", "Estancia mínima"]
    sub_choice = st.selectbox("Sé más concreto", sub_menu)
    
# Menú VECINDARIO EN PROPIERDADES
    if sub_choice   == "Mapa":
        st.title("Mapa de los AirBnb de Menorca")
        
        # Mapa folium
        lats2023 = nuevo_listings['latitude'].tolist()
        lons2023 = nuevo_listings['longitude'].tolist()
        locations = list(zip(lats2023, lons2023))

        # Crear el mapa de Folium
        map1 = folium.Map(location=[39.980566, 4.081079], zoom_start=9.5)
        FastMarkerCluster(data=locations).add_to(map1)

        # Mostrar el mapa en Streamlit
        st_folium(map1, width=1000, height=500)
    
    elif sub_choice == "Vecindario":
        st.title("Vecindario")
        st.markdown("La isla de Menorca cuenta con ocho municipios: Maó, Ciutadella, Alaior, Es Castell, Sant Lluís, Es Mercadal, Ferreries y Es Migjorn Gran, aunque cerca de un 65% de la población se concentra en las ciudades de Maó y Ciutadella. ")

        neighbourhood = nuevo_listings['neighbourhood'].value_counts().sort_values(ascending=True)

        # Crear el gráfico de quesito con Plotly
        fig = px.pie(neighbourhood, 
                    values=neighbourhood.values, 
                    names=neighbourhood.index, 
                    title='Número de AirBnbs por zona', 
                    width=800, height=600,
                    color_discrete_sequence=px.colors.qualitative.Set3)

        fig.update_layout(
            title_font_size=20
        )

        # Mostrar la gráfica en Streamlit
        st.plotly_chart(fig)
        
        st.markdown("""
        Podemos observar que la zona con más apartamentos turísticos es Ciudadella de Menorca, 
        seguido por Mercadal y Alaior (que cuentan con menos de la mitad que Ciudadella). 
        A continuación se muestra un mapa con la consecuente distribución de estos AirBnbs
        """)        
    
    elif sub_choice == "Precios":
        st.title("Precio por vecindario")
        st.markdown("A continuación vamos a observar el precio medio para una habitación de dos personas en diferentes localizaciones de la isla. Comenzamos arreglando los datos de la columna `price` con el fin de no obtener ningún error.")
        
        precio_vecindario = nuevo_listings[nuevo_listings['accommodates'] == 2]
        precio_vecindario = precio_vecindario.groupby('neighbourhood')['price'].mean().sort_values(ascending=True)

        # Crear la gráfica con Plotly
        fig = px.bar(precio_vecindario, 
             orientation='h', 
             title='Precio medio de alojamientio para dos huéspedes', 
             labels={'valor': 'Precio medio por día (Euro)', 'índice': ''},
             width=800, height=600)

        fig.update_layout(
            xaxis_title='Precio medio por día(Euro)',
            yaxis_title='',
            title_font_size=20,
            xaxis_title_font_size=12,
            yaxis_title_font_size=12
        )

        # Mostrar la gráfica en Streamlit
        st.title("Análisis de Precios por Vecindario")
        st.plotly_chart(fig)
        
        st.markdown("""
                    Observamos que Ferreries es el municipio con los hospedajes más caros, con un precio medio superior a los 550 dólares 
                    por noche para dos personas, seguido de Es Castell, con un precio cercano a los 350 dólares. Por el lado contrario, 
                    el municipio más asequible es Es Migjorn Gran, con un precio medio inferior a los 100 dólares, seguido de Alaior, 
                    con un precio medio algo superior a los 100 dólares. 
                    
                    Cabe resaltar que los precios en este dataset no varían a lo largo del año, por lo que se toman unos datos estáticos 
                    que suponemos que serán una media de los precios de todo el año.
                    """)
        
    elif sub_choice == "Propiedades":
        st.title("Tipos de propiedades")
        st.markdown("""
                    El tipo de propiedad que se alquila es muy importante, ya que en esta plataforma podemos encontrar desde alojamientos 
                    enteros como casas, hasta habitaciones privadas, habitaciones compartidas o habitaciones de hotel.
                    """)
        
        freq = nuevo_listings['room_type'].value_counts().sort_values(ascending=True)

        # Crear el gráfico de quesito con Plotly
        fig = px.pie(freq, 
                    values=freq.values, 
                    names=freq.index, 
                    title='Frecuencia de tipos de habitación', 
                    width=800, height=400,
                    color_discrete_sequence=px.colors.qualitative.Set3)

        fig.update_layout(
            title_font_size=20
        )

        # Mostrar la gráfica en Streamlit
        st.title("Frecuencia de tipos de habitación")
        st.plotly_chart(fig)
        
        st.markdown("""
                    Como efectivamente hemos observado, las casas/apartamentos enteros son los que más se alquilan en esta aplicación, seguido 
                    de las habitaciones privadas y con un porcentaje muy bajo de habitaciones compartidas y habitaciones de hotel
                    """)
        
        prop = nuevo_listings.groupby(['property_type', 'room_type']).room_type.count()
        prop = prop.unstack()
        prop['total'] = prop.sum(axis=1)
        prop = prop.sort_values(by='total')
        prop = prop[prop['total'] >= 200]
        prop = prop.drop(columns=['total'])

        # Convertir los datos para Plotly
        prop = prop.reset_index()
        prop = prop.melt(id_vars=['property_type'], var_name='room_type', value_name='count')

        # Crear la gráfica con Plotly
        fig = px.bar(prop, 
                    x='count', 
                    y='property_type', 
                    color='room_type', 
                    title='Tipos de propiedades en Menorca', 
                    labels={'count': 'Number of listings', 'property_type': '', 'room_type': 'Room Type'},
                    orientation='h', 
                    width=900, height=600)

        fig.update_layout(
            xaxis_title='Número de propiedades listadas',
            yaxis_title='',
            title_font_size=18,
            xaxis_title_font_size=14,
            yaxis_title_font_size=14,
            legend=dict(title='Room Type', font=dict(size=13)),
            yaxis=dict(tickfont=dict(size=13))
        )

        # Mostrar la gráfica en Streamlit
        st.title("Tipos de propiedades en Menorca")
        st.plotly_chart(fig)

        st.markdown("""
                    En esta gráfica se puede observar con más claridad cómo los tipos de propiedades más comunes son casas/apartamentos completos, 
                    al no encontrar ni una pizca de otro color que no sea el rojo.
                    """)
        
    elif sub_choice == "Huéspedes":
        st.title("Huéspedes por alojamiento")
        st.markdown("""
                    En este apartado mostraremos la cantidad de huéspedes que se admiten en estos alquileres vacacionales, 
                    además analizaremos estos en contraste con los precios
                    """)
        
        feq = nuevo_listings['accommodates'].value_counts().sort_index()

        # Crear la gráfica con Plotly
        fig = px.bar(feq, 
                    x=feq.index, 
                    y=feq.values, 
                    labels={'x': 'Accommodates', 'y': 'Number of listings'},
                    title='Accommodates (number of people)', 
                    width=800, height=600)

        fig.update_layout(
            xaxis_title='Accommodates',
            yaxis_title='Number of listings',
            title_font_size=20,
            xaxis_title_font_size=12,
            yaxis_title_font_size=12
        )

        # Mostrar la gráfica en Streamlit
        st.title("Distribución de número de personas que pueden ser acomodadas")
        st.plotly_chart(fig)
        
        st.markdown("""
                    Como suele ocurrir, la mayor parte de alojamientos listados en AirBnb son para dos huéspedes, seguidos de los 
                    de 4 y los de 6. Podemos observar que hay alojamientos de hasta 16 personas, el máximo permitido por AirBnb
                    """)
        
        fig = px.scatter(nuevo_listings, 
                 x='accommodates', 
                 y='price', 
                 color='accommodates', 
                 title='Relación entre Número de Huéspedes y Precio', 
                 labels={'accommodates': 'Número de Huéspedes', 'price': 'Precio (USD)'}, 
                 opacity=0.6,
                 color_continuous_scale='viridis',
                 width=800, height=600)

        fig.update_layout(
            xaxis_title='Número de Huéspedes',
            yaxis_title='Precio (USD)',
            title_font_size=16,
            xaxis_title_font_size=14,
            yaxis_title_font_size=14
        )

        # Mostrar la gráfica en Streamlit
        st.title("Relación entre Número de Huéspedes y Precio")
        st.plotly_chart(fig)
        
        st.markdown("""
                    Este diagrama de dispersión muestra la relación entre el número de huéspedes y el precio por noche de la vivienda. En ella 
                    podemos observar que el precio es proporcional al número de huéspedes con una sola excepción.
                    """)
        
        mean_price = nuevo_listings.groupby('accommodates')['price'].mean().reset_index()

        # Crear la gráfica de barras con Plotly
        fig = px.bar(mean_price, 
                    x='accommodates', 
                    y='price', 
                    title='Precio Medio por Número de Huéspedes', 
                    labels={'accommodates': 'Número de Huéspedes', 'price': 'Precio Medio (USD)'}, 
                    color='price', 
                    color_continuous_scale='viridis',
                    width=800, height=600)

        fig.update_layout(
            xaxis_title='Número de Huéspedes',
            yaxis_title='Precio Medio (USD)',
            title_font_size=16,
            xaxis_title_font_size=14,
            yaxis_title_font_size=14
        )

        # Mostrar la gráfica en Streamlit
        st.title("Precio Medio por Número de Huéspedes")
        st.plotly_chart(fig)
        
        st.markdown("""
                    Aquí podemos observar la excepción con más claridad. El alojamiento apto para 13 personas no es proporcional al tratarse de 
                    una excepción, seguramente debido a que solo hay una propiedad para ese número de personas y con un precio bastante aceptable.
                    """)
        
    elif sub_choice == "Puntuaciones":
        st.title("Puntuación de los alojamientos")
        st.markdown("""
                    Los huéspedes han puntuado los alojamientos en los que han estado de la siguiente manera:
                    """)
            
            
        fig = px.histogram(nuevo_listings, x='review_scores_rating', nbins=20, marginal='rug',
                        title='Distribución y Densidad de los Puntajes de Reseñas',
                        labels={'review_scores_rating': 'Puntaje de Reseñas', 'count': 'Frecuencia'})

        # Actualizar el diseño y mostrar la gráfica en Streamlit
        fig.update_layout(showlegend=False, xaxis_title_font_size=14, yaxis_title_font_size=14)
        st.plotly_chart(fig)
        
    elif sub_choice == "Estancia mínima":
        st.title("Estancia mínima")
        st.markdown("""
                    Algunos alojamientos cuentan con un número mínimo de noches que han ser reservadas, estas suelen darse a causa de las tasas que requieren los servicios de limpieza o el propio translado para la entrega de llaves. 
                    """)
        
        filtered_listings = nuevo_listings[nuevo_listings['minimum_nights'] <= 50]

        # Crear el histograma con Plotly
        fig = px.histogram(filtered_listings, x='minimum_nights', nbins=50,
                        title='Distribución del Número Mínimo de Días para Alquilar un Airbnb (Máximo 50 Días)',
                        labels={'minimum_nights': 'Número Mínimo de Días', 'count': 'Frecuencia'})

        # Actualizar el diseño y mostrar la gráfica en Streamlit
        fig.update_layout(xaxis_title_font_size=14, yaxis_title_font_size=14)
        st.plotly_chart(fig)
                
        
elif option == "Análisis de los Hosts":
    st.title("Análisis Exploratorio de los Hosts")
    # Añadir el contenido del análisis exploratorio de los hosts aquí
    st.header("Distribución de Hosts")
    
    sub_menu = ["Vista general", "Primera review", "Tiempo de respuesta", "Superhosts"]
    sub_choice = st.selectbox("Sé más concreto", sub_menu)

    
    # Menú VECINDARIO EN PROPIERDADES
    if sub_choice == "Vista general":
        st.title("Vista general")
        st.markdown("""
            Estos son los hosts que cuentan con un mayor número de reviews, y su correspondiente nota media a partir de las valoraciones de los usuarios.
            Aquí observamos que Villa Plus encabeza la lista con 199 reviews y un 4.6 de puntuación media, seguido de Solmar con 98 reviews una media de 4.45 y 3Villas con 96 y una nota media de 4.61.
            """)
        host_reviews = nuevo_listings.groupby(['host_id', 'host_name']).size().sort_values(ascending=False).to_frame(name='number_of_reviews')

        # Calcular el promedio de 'review_scores_rating' para cada host
        host_avg_rating = nuevo_listings.groupby(['host_id', 'host_name'])['review_scores_rating'].mean().to_frame(name='average_review_score')

        # Unir los dataframes
        host_reviews = host_reviews.join(host_avg_rating)

        # Mostrar el título y la tabla en Streamlit
        st.title("Número de Reviews y nota media")
        st.dataframe(host_reviews)  
        
        
    elif sub_choice == "Primera review":
        st.title("Primera review")
        nuevo_listings['first_review'] = pd.to_datetime(nuevo_listings['first_review'])

        # Crear el histograma con Plotly
        fig = px.histogram(nuevo_listings, x='first_review', nbins=30,
                        title='Distribución de la Fecha de la Primera Review',
                        labels={'first_review': 'Fecha de la primera review', 'count': 'Frecuencia'})

        # Actualizar el diseño y mostrar la gráfica en Streamlit
        fig.update_layout(xaxis_title_font_size=14, yaxis_title_font_size=14, xaxis_tickangle=-45)
        st.plotly_chart(fig)
        
        st.markdown("""
                    Algunos de los propietarios reciben sus primeras reseñas en 2012, que desde entonces han crecido progresivamente durante los meses de más turismo del año (concretamente en verano). 
                    Justo tras el COVID se muestra un repunte de nuevas propiedades en la plataforma con sus correspodientes nuevas reseñas.
                    """)
        
    elif sub_choice == "Tiempo de respuesta":
        st.title("Tiempo de respuesta")
        
        order = ['within an hour', 'within a few hours', 'within a day', 'a few days or more']

        # Crear el gráfico de barras con Plotly
        fig = px.histogram(nuevo_listings, x='host_response_time', category_orders={'host_response_time': order},
                        title='Distribución del Tiempo de Respuesta del Anfitrión',
                        labels={'host_response_time': 'Tiempo de Respuesta del Anfitrión', 'count': 'Número de Propiedades'})

        # Actualizar el diseño y mostrar la gráfica en Streamlit
        fig.update_layout(xaxis_title_font_size=14, yaxis_title_font_size=14, xaxis_tickangle=-45)
        st.plotly_chart(fig)
        
        st.markdown("""
                    Observamos que por lo general los anfitriones contestan en una hora o menos, y muy pocos tardan más de un día. Esto es algo muy positovo a la hora de evaluar un alojamiento, haciendo que los huespedes se sientan acompañados desde el principio.
                    """)
        
    elif sub_choice == "Superhosts":
        st.title("Superhosts")
        
        total_count = nuevo_listings.shape[0]
        superhost_count = nuevo_listings[nuevo_listings['host_is_superhost'] == 't'].shape[0]
        non_superhost_count = total_count - superhost_count

        # Crear un DataFrame con los resultados
        data = {'Estado': ['Superanfitrión', 'No Superanfitrión'], 'Conteo': [superhost_count, non_superhost_count]}
        count_df = pd.DataFrame(data)

        # Crear el gráfico de barras con Plotly
        fig = px.bar(count_df, x='Estado', y='Conteo', title='Número de Propiedades por Estado de Superanfitrión',
                    labels={'Estado': 'Estado de Superanfitrión', 'Conteo': 'Número de Propiedades'},
                    color_discrete_sequence=['#636EFA'])

        # Actualizar el diseño y mostrar la gráfica en Streamlit
        fig.update_layout(xaxis_title_font_size=14, yaxis_title_font_size=14)
        st.plotly_chart(fig)
        
        st.markdown("""
                    Cerca de 700 anfitriones cuentan con la distinción de Superhost, lo que significa que tanto el anfitrion como el alojamiento cuenta con unas condiciones óptimas de respuesta, cuidado y limpieza. Esto es cerca de 1/6 del número total de anfitriones, siendo más de 2500 los que NO Superhosts.
                    """)
        
        total_count = nuevo_listings['license'].shape[0]
        non_null_count = nuevo_listings['license'].count()
        null_count = total_count - non_null_count

        # Crear un DataFrame con los resultados
        data = {'Estado': ['Datos', 'NaN'], 'Conteo': [non_null_count, null_count]}
        count_df = pd.DataFrame(data)

        # Crear el gráfico de barras con Plotly
        fig = px.bar(count_df, x='Estado', y='Conteo', title='Conteo de Valores para la Licencia',
                    labels={'Estado': 'Estado', 'Conteo': 'Cantidad'},
                    color_discrete_sequence=['#636EFA', '#EF553B'])

        # Actualizar el diseño y mostrar la gráfica en Streamlit
        fig.update_layout(xaxis_title_font_size=14, yaxis_title_font_size=14)
        st.plotly_chart(fig)
        
        st.markdown("""
                    Podemos observar que cerca de 2000 de los más de los 3100 alojamientos listados en AirBnb cuentan con la pertinente licencia turística, mientras que casi 1300 no la tienen en vigor o no la tienen correctamente subida a la página.

                    Según Menorca.com, en el mes de Mayo de 2024 más de 400 propietarios 'corrigieron' sus anuncios para mostrar el número de la preceptiva licencia turística aumentando estos en un 32%, después de que el gobierno insular decidiese tomar medidas en cuanto a los pisos turísticos ilegales.

                    Podemos observar que cuando se trata de los superhosts, el número de casas sin licencia disminuye, como podemos observar a continuación.
                    """)
        
        total_count = nuevo_listings.shape[0]
        superhost_count_with_license = nuevo_listings[(nuevo_listings['host_is_superhost'] == 't') & nuevo_listings['license'].notnull()].shape[0]
        superhost_count_no_license = nuevo_listings[(nuevo_listings['host_is_superhost'] == 't') & nuevo_listings['license'].isnull()].shape[0]
        non_superhost_count_with_license = nuevo_listings[(nuevo_listings['host_is_superhost'] == 'f') & nuevo_listings['license'].notnull()].shape[0]
        non_superhost_count_no_license = nuevo_listings[(nuevo_listings['host_is_superhost'] == 'f') & nuevo_listings['license'].isnull()].shape[0]

        # Crear un DataFrame con los resultados
        data = {
            'Estado': ['Superhost con Licencia', 'Superhost sin Licencia', 'Regular Host con Licencia', 'Regular Host sin Licencia'], 
            'Conteo': [superhost_count_with_license, superhost_count_no_license, non_superhost_count_with_license, non_superhost_count_no_license]
        }
        count_df = pd.DataFrame(data)

        # Crear el gráfico de barras con Plotly
        fig = px.bar(count_df, x='Estado', y='Conteo', title='Distribución de Propiedades por Estado del Host y Licencia',
                    labels={'Estado': 'Estado del Host y Licencia', 'Conteo': 'Número de Propiedades'},
                    color_discrete_sequence=['#636EFA', '#EF553B', '#00CC96', '#AB63FA'])

        # Actualizar el diseño y mostrar la gráfica en Streamlit
        fig.update_layout(xaxis_title_font_size=14, yaxis_title_font_size=14, xaxis_tickangle=-45)
        st.plotly_chart(fig)
        
        st.markdown("""
                    En esta gráfica observamos que no hay una correlación entre la licencia y los superhosts, sindo la diferencia en términos proporcionales igual entre los superhosts con y sin licencia y los no superhosts con y sin licencia.
                    """)

elif option == "Conclusión":
    st.title("Conclusión")
    st.markdown("""
                Tras examinar los datos que nos ofrece InsideAirbnb.com podemos observar una gran variedad de precios, habitaciones y posibles huéspedes, además de disponer de casas en alquiler vacacional en todos los pueblos de la región. Además, factores como los puntajes de reseñas, los requisitos de estadía mínima, el tiempo de respuesta del anfitrión y el estado de superanfitrión y licencia proporcionan información valiosa sobre la calidad, la legalidad y la experiencia general de los alojamientos. 
                
                Esta combinación de factores permite a los viajeros encontrar la opción que mejor se adapte a sus necesidades y preferencias, mientras que los propietarios pueden tomar decisiones informadas para mejorar sus servicios y maximizar su éxito en el competitivo mercado de alquiler vacacional en Menorca.
                
                """)
    st.image("https://cdn.sanity.io/images/cr01fuv8/production/7531eb89542101694f897c90a3d094676a508de4-2000x1127.jpg")