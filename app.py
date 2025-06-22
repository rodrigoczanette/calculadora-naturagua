
import streamlit as st
from PIL import Image
import math
import base64

st.set_page_config(page_title="Calculadora Naturágua", page_icon="💧", layout="centered")

background_image_path = "logo-naturagua_opaca_450x350_final.png"

@st.cache_data
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = f"""
    <style>
    .stApp {{
      background-image: url("data:image/png;base64,{bin_str}");
      background-repeat: no-repeat;
      background-position: center;
      background-size: 450px 350px;
      background-color: #e0f7fa;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

set_background(background_image_path)

st.markdown("<h3 style='color:#087d8d;'>CALCULE SUA TARIFA</h3>", unsafe_allow_html=True)

tipo_tarifa = st.selectbox("Tipo de Tarifa:", ["Residencial", "Comercial"])
leitura_anterior = st.text_input("Leitura Anterior (m³):", value="")
leitura_atual = st.text_input("Leitura Atual (m³):", value="")
consumo_manual = st.text_input("Consumo (m³):", value="")

TARIFAS = {
    "Residencial": [3.4288, 4.8762, 5.1881, 5.6297, 6.2477],
    "Comercial": [3.9358, 5.2886, 5.9509, 6.2827, 6.9579]
}

VALOR_MINIMO = {
    "Residencial": 34.29,
    "Comercial": 39.36
}

faixas = [(0, 10), (10, 20), (20, 30), (30, 40), (40, float('inf'))]

def calcular_consumo():
    try:
        if leitura_anterior and leitura_atual:
            consumo = float(leitura_atual.replace(',', '.')) - float(leitura_anterior.replace(',', '.'))
            return round(consumo)
        elif consumo_manual:
            return round(float(consumo_manual.replace(',', '.')))
    except:
        return None

consumo = calcular_consumo()

if st.button("Calcular"):
    if consumo is None or consumo < 0:
        st.error("Erro: Verifique os valores de entrada.")
    else:
        tarifas = TARIFAS[tipo_tarifa]
        valor_minimo = VALOR_MINIMO[tipo_tarifa]
        restante = consumo
        total = 0
        detalhes = []

        for i, (inicio, fim) in enumerate(faixas):
            if restante <= 0:
                break
            if i == 0:
                faixa_consumo = min(restante, 10)
                if faixa_consumo > 0:
                    detalhes.append(f"{int(faixa_consumo)} m³ × R$ {valor_minimo:,.2f} = R$ {valor_minimo:,.2f}".replace('.', ','))
                    total += valor_minimo
                restante -= faixa_consumo
            else:
                limite_faixa = fim - inicio if fim != float('inf') else restante
                faixa_consumo = min(restante, limite_faixa)
                valor = faixa_consumo * tarifas[i]
                valor_unitario_str = f"{tarifas[i]:.4f}".replace('.', ',')
                valor_faixa_trunc = math.floor(valor * 100) / 100
                valor_total_str = f"{valor_faixa_trunc:,.2f}".replace('.', ',').replace(',', 'v').replace('.', ',').replace('v', '.')
                detalhes.append(f"{int(faixa_consumo)} m³ × R$ {valor_unitario_str:<8} = R$ {valor_total_str}")
                total += valor
                restante -= faixa_consumo

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<b>Tarifas por Faixa:</b>", unsafe_allow_html=True)
            faixas_str = ["0–10", "11–20", "21–30", "31–40", "41+"]
            for i, tarifa in enumerate(tarifas):
                st.write(f"{faixas_str[i]} m³: R$ {tarifa:.4f}".replace('.', ','))

        with col2:
            st.markdown("<b>Forma do Cálculo:</b>", unsafe_allow_html=True)
            for linha in detalhes:
                st.text(linha)

        total_truncado = math.ceil(total * 100) / 100
        total_formatado = f"{total_truncado:,.2f}".replace('.', ',').replace(',', 'v').replace('.', ',').replace('v', '.')

        if consumo <= 10:
            st.success(f"Total: R$ {total_formatado} (Tarifa Mínima)")
        else:
            st.success(f"Total: R$ {total_formatado}")
