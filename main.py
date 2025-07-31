import streamlit as st
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
import re

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

def analisar_spin(texto):
    prompt = f"""
    Abaixo está uma conversa entre um vendedor e um cliente. Analise a atuação do vendedor segundo a metodologia SPIN Selling.

    Classifique as falas do vendedor como pertencentes a:
    - Situação
    - Problema
    - Implicação
    - Necessidade de Solução
    - Nenhuma (caso não se encaixe em nenhuma etapa)

    No final, diga se alguma etapa do SPIN foi ignorada ou mal executada, e sugira como o vendedor poderia melhorar.

    **Formato da resposta (JSON):**
    {{
      "Situação": ["fala 1", "fala 2"],
      "Problema": ["fala 3"],
      "Implicação": ["fala 4"],
      "Necessidade de Solução": ["fala 5"],
      "Nenhuma": ["fala 6"],
      "Resumo": "Texto explicativo com erros detectados e sugestões de melhoria."
    }}

    Conversa:
    {texto}
    """
    try:
        response = model.generate_content(prompt)
        resposta_bruta = response.text.strip()

        resposta_bruta = re.sub(r"```(?:json)?\s*([\s\S]*?)\s*```", r"\1", resposta_bruta).strip()

        match = re.search(r"\{.*\}", resposta_bruta, re.DOTALL)
        if match:
            json_data = match.group(0)
            return json.loads(json_data)
        else:
            raise ValueError("JSON não encontrado na resposta.")

    except Exception as e:
        return {
            "Erro": f"Erro ao interpretar a resposta como JSON. Verifique a formatação.",
            "Resposta da IA": resposta_bruta
        }

st.title("🧩 Análise de Vendas com SPIN Selling")

texto_conversa = st.text_area("📋 Digite a conversa entre vendedor e cliente:")

if st.button("Analisar SPIN Selling"):
    if texto_conversa.strip() == "":
        st.warning("Por favor, insira a conversa.")
    else:
        resultado = analisar_spin(texto_conversa)
        if "Erro" in resultado:
            st.error(resultado["Erro"])
            st.code(resultado.get("Resposta da IA", ""), language="markdown")
        else:
            for categoria in ["Situação", "Problema", "Implicação", "Necessidade de Solução", "Nenhuma"]:
                if resultado.get(categoria):
                    st.markdown(f"### 🔍 {categoria}")
                    for frase in resultado[categoria]:
                        st.info(f"💬 {frase}")

            st.markdown("### 📌 Resumo e Sugestões")
            st.write(resultado["Resumo"])

st.write("OU")
uploaded_file = st.file_uploader("📂 Envie um arquivo de conversa (.txt)", type=["txt"])

if uploaded_file is not None:
    conteudo = uploaded_file.read().decode("utf-8")
    st.text_area("📄 Conteúdo carregado", value=conteudo, height=200)
    if st.button("Analisar Arquivo SPIN Selling"):
        resultado = analisar_spin(conteudo)
        if "Erro" in resultado:
            st.error(resultado["Erro"])
            st.code(resultado.get("Resposta da IA", ""), language="markdown")
        else:
            for categoria in ["Situação", "Problema", "Implicação", "Necessidade de Solução", "Nenhuma"]:
                if resultado.get(categoria):
                    st.markdown(f"### 🔍 {categoria}")
                    for frase in resultado[categoria]:
                        st.info(f"💬 {frase}")

            st.markdown("### 📌 Resumo e Sugestões")
            st.write(resultado["Resumo"])