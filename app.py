import os
import base64

import numpy as np
import streamlit as st
from openai import OpenAI
from PIL import Image
from streamlit_drawable_canvas import st_canvas

Expert = " "
profile_imgenh = " "


def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."


# ---------------- Configuración de la página ----------------
st.set_page_config(page_title="Tablero Inteligente")

# Título fucsia con CSS
st.markdown(
    """
    <style>
    h1.titulo-fucsia { color: #FF00FF !important; }
    </style>
    <h1 class="titulo-fucsia">Tablero para dibujo</h1>
    """,
    unsafe_allow_html=True,
)

# Imagen debajo del título + texto
if os.path.exists("gatodibujon.jpg"):
    st.image("gatodibujon.jpg", width=300)
st.write("Ahora dibuja abajo 👇")

# ---------------- Barra lateral ----------------
with st.sidebar:
    st.subheader("Acerca de:")
    st.write(
        "En esta aplicación veremos cómo una máquina puede interpretar "
        "un boceto y convertirlo en un poema."
    )

    st.subheader("Propiedades del Tablero")

    st.subheader("Dimensiones del Tablero")
    canvas_width = st.slider("Ancho del tablero", 300, 700, 500, 50)
    canvas_height = st.slider("Alto del tablero", 200, 600, 300, 50)

    drawing_mode = st.selectbox(
        "Herramienta de Dibujo:",
        ("freedraw", "line", "rect", "circle", "transform", "polygon", "point"),
    )

    stroke_width = st.slider("Selecciona el ancho de línea", 1, 30, 15)

    stroke_color = st.color_picker("Color de trazo", "#FF00FF", key="color_trazo_fucsia")

    bg_color = st.color_picker("Color de fondo", "#000000")

# ---------------- Tablero ----------------
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=canvas_height,
    width=canvas_width,
    drawing_mode=drawing_mode,
    key=f"canvas_{canvas_width}_{canvas_height}_{stroke_color}",
)

# ---------------- API Key y poema ----------------
ke = st.text_input("Ingresa tu Clave", type="password")
api_key = ke
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key

analyze_button = st.button("Crear poema", type="secondary")

if canvas_result.image_data is not None and api_key and analyze_button:
    client = OpenAI(api_key=api_key)

    with st.spinner("Creando poema ..."):
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype("uint8"), "RGBA")
        input_image.save("img.png")

        base64_image = encode_image_to_base64("img.png")
        prompt_text = (
            "Observa la imagen y escribe un poema corto en español "
            "(entre 4 y 8 versos) inspirado en lo que ves. "
            "Responde solo con el poema y un título breve."
        )

        try:
            full_response = ""
            message_placeholder = st.empty()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=500,
            )
            if response.choices[0].message.content is not None:
                full_response += response.choices[0].message.content
            message_placeholder.markdown(full_response)

            if Expert == profile_imgenh:
                st.session_state.mi_respuesta = response.choices[0].message.content
        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    if not api_key:
        st.warning("Por favor ingresa tu API key.")
