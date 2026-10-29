import io
import math

import streamlit as st
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates

# ---------------- Configuración ----------------
st.set_page_config(page_title="Tablero para pintar")

W, H = 500, 400          # tamaño del lienzo
LW = 4                   # grosor de las líneas
LINEA = (0, 0, 0)        # color de las líneas (no se pinta encima)

PALETA = [
    ("Rojo", "#E53935"),
    ("Naranja", "#FB8C00"),
    ("Amarillo", "#FDD835"),
    ("Verde", "#43A047"),
    ("Azul", "#1565C0"),
    ("Celeste", "#81D4FA"),
    ("Morado", "#8E24AA"),
    ("Rosado", "#F48FB1"),
    ("Café", "#795548"),
    ("Negro", "#212121"),
]


def hex_a_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


# ---------------- Utilidades de dibujo ----------------
def nuevo_lienzo():
    img = Image.new("RGB", (W, H), "white")
    return img, ImageDraw.Draw(img)


def elipse(d, caja, relleno="white"):
    d.ellipse(caja, fill=relleno, outline="black", width=LW)


def rect(d, caja):
    d.rectangle(caja, fill="white", outline="black", width=LW)


def poligono(d, puntos, ancho=LW):
    d.polygon(puntos, fill="white")
    d.line(puntos + [puntos[0]], fill="black", width=ancho, joint="curve")


def estrella(d, cx, cy, r):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    poligono(d, pts, ancho=2)


def nube(d, cajas):
    """Une varias elipses en una sola silueta con contorno."""
    for c in cajas:
        d.ellipse(c, fill="black")
    for x0, y0, x1, y1 in cajas:
        d.ellipse((x0 + LW, y0 + LW, x1 - LW, y1 - LW), fill="white")


# ---------------- Los tres dibujos ----------------
def dibujo_casa():
    img, d = nuevo_lienzo()
    rect(d, (0, 300, W, H))                                   # pasto
    elipse(d, (25, 25, 95, 95))                               # sol
    rect(d, (400, 230, 420, 320))                             # tronco
    elipse(d, (370, 150, 450, 245))                           # copa
    rect(d, (300, 95, 330, 150))                              # chimenea
    rect(d, (150, 180, 350, 320))                             # casa
    poligono(d, [(130, 182), (250, 90), (370, 182)])          # techo
    rect(d, (225, 235, 275, 320))                             # puerta
    rect(d, (170, 215, 210, 255))                             # ventana 1
    rect(d, (290, 215, 330, 255))                             # ventana 2
    d.line((190, 215, 190, 255), fill="black", width=3)
    d.line((170, 235, 210, 235), fill="black", width=3)
    d.line((310, 215, 310, 255), fill="black", width=3)
    d.line((290, 235, 330, 235), fill="black", width=3)
    return img


def dibujo_noche():
    img, d = nuevo_lienzo()
    elipse(d, (320, 30, 440, 150))                            # luna
    elipse(d, (345, 55, 375, 85))                             # cráteres
    elipse(d, (390, 95, 420, 125))
    elipse(d, (350, 105, 370, 125))
    for cx, cy, r in [(60, 60, 20), (170, 100, 18), (250, 40, 18),
                      (110, 180, 18), (400, 195, 18), (470, 60, 16)]:
        estrella(d, cx, cy, r)
    nube(d, [(190, 175, 250, 220), (225, 160, 295, 220), (275, 180, 335, 220)])
    poligono(d, [(0, 300), (100, 240), (200, 300), (320, 230),
                 (430, 300), (500, 260), (500, H), (0, H)])   # montañas
    poligono(d, [(0, 355), (500, 335), (500, H), (0, H)])     # suelo
    rect(d, (60, 300, 80, 365))                               # tronco
    elipse(d, (25, 245, 115, 320))                            # árbol
    return img


def dibujo_perro():
    img, d = nuevo_lienzo()
    rect(d, (0, 330, W, H))                                   # pasto
    elipse(d, (25, 25, 95, 95))                               # sol
    elipse(d, (30, 295, 90, 355))                             # pelota
    d.line((30, 325, 90, 325), fill="black", width=LW)
    elipse(d, (95, 200, 165, 245))                            # cola
    elipse(d, (130, 190, 330, 340))                           # cuerpo
    elipse(d, (140, 270, 230, 350))                           # pata trasera
    elipse(d, (270, 260, 330, 352))                           # pata delantera
    elipse(d, (170, 215, 225, 258))                           # mancha
    elipse(d, (290, 100, 410, 220))                           # cabeza
    elipse(d, (278, 110, 320, 200))                           # oreja izq.
    elipse(d, (380, 110, 422, 200))                           # oreja der.
    elipse(d, (325, 160, 375, 202))                           # hocico
    elipse(d, (341, 188, 359, 215), relleno="white")          # lengua
    elipse(d, (322, 135, 336, 149), relleno="black")          # ojos
    elipse(d, (364, 135, 378, 149), relleno="black")
    elipse(d, (339, 163, 361, 178), relleno="black")          # nariz
    return img


DIBUJOS = {
    "🏠 Casa": dibujo_casa,
    "🌙 Noche con luna": dibujo_noche,
    "🐶 Perro": dibujo_perro,
}


# ---------------- Relleno ----------------
def rellenar(img, x, y, color_hex):
    """Rellena la zona donde se hizo clic (si cae sobre una línea,
    busca un píxel vecino que no sea línea)."""
    x, y = int(x), int(y)
    vecinos = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
               (2, 2), (-2, 2), (2, -2), (-2, -2)]
    for dx, dy in vecinos:
        px, py = x + dx, y + dy
        if 0 <= px < img.width and 0 <= py < img.height:
            if img.getpixel((px, py)) != LINEA:
                ImageDraw.floodfill(img, (px, py), hex_a_rgb(color_hex))
                return


# ---------------- Estado ----------------
if "obras" not in st.session_state:
    st.session_state.obras = {n: f() for n, f in DIBUJOS.items()}
    st.session_state.color = PALETA[0][1]
    st.session_state.version = 0

# ---------------- Estilos ----------------
css = """
<style>
h1.titulo-fucsia { color: #FF00FF !important; }
</style>
"""
for i, (_, hexa) in enumerate(PALETA):
    borde = "#000" if hexa == st.session_state.color else "#ddd"
    grosor = "4px" if hexa == st.session_state.color else "2px"
    css += f"""
<style>
.st-key-color_{i} button,
.st-key-color_{i} button:hover,
.st-key-color_{i} button:focus,
.st-key-color_{i} button:active {{
    background-color: {hexa} !important;
    border: {grosor} solid {borde} !important;
    color: white !important;
    font-weight: 900;
    font-size: 1.3rem;
    text-shadow: 0 0 3px #000;
    height: 3rem;
}}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# ---------------- Encabezado ----------------
st.markdown('<h1 class="titulo-fucsia">Tablero para pintar 🎨</h1>', unsafe_allow_html=True)

with st.sidebar:
    st.subheader("Acerca de:")
    st.write(
        "Elige un dibujo, selecciona un color de la paleta y haz clic "
        "en la zona del dibujo que quieras pintar."
    )

# Selector del dibujo (arriba del lienzo)
nombre = st.radio("Elige tu dibujo", list(DIBUJOS), horizontal=True)
img = st.session_state.obras[nombre]

col_paleta, col_lienzo = st.columns([1, 3])

# ---------------- Paleta (al lado) ----------------
with col_paleta:
    st.write("**Colores**")
    cols = st.columns(2)
    for i, (nom_color, hexa) in enumerate(PALETA):
        with cols[i % 2]:
            elegido = hexa == st.session_state.color
            if st.button("✓" if elegido else "\u00a0", key=f"color_{i}",
                         help=nom_color, use_container_width=True):
                st.session_state.color = hexa
                st.rerun()

# ---------------- Lienzo ----------------
with col_lienzo:
    clic = streamlit_image_coordinates(
        img, key=f"lienzo_{nombre}_{st.session_state.version}"
    )
    if clic is not None:
        x = clic["x"] * img.width / clic["width"]
        y = clic["y"] * img.height / clic["height"]
        rellenar(img, x, y, st.session_state.color)
        st.session_state.version += 1   # cambia la key para no repetir el clic
        st.rerun()

    b1, b2 = st.columns(2)
    with b1:
        if st.button("🧽 Empezar de nuevo", use_container_width=True):
            st.session_state.obras[nombre] = DIBUJOS[nombre]()
            st.session_state.version += 1
            st.rerun()
    with b2:
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        st.download_button(
            "💾 Descargar", buffer.getvalue(),
            file_name="mi_dibujo.png", mime="image/png",
            use_container_width=True,
        )
