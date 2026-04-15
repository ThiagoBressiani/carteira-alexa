from flask import Flask, jsonify
import requests
import json
import os

app = Flask(__name__)

# =========================
# CARREGA PORTFÓLIO
# =========================
def carregar_portfolio():
    try:
        with open("portfolio.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("Erro portfolio.json:", e)
        return []

# =========================
# BUSCA NA BRAPI (COM FALLBACK SE FALHAR)
# =========================
def buscar_precos(tickers):
    try:
        url = f"https://brapi.dev/api/quote/{','.join(tickers)}"
        r = requests.get(url, timeout=10)

        if r.status_code != 200:
            print("BRAPI erro status:", r.status_code)
            return []

        data = r.json()
        return data.get("results", [])

    except Exception as e:
        print("Erro BRAPI:", e)
        return []

# =========================
# RESUMO SEGURO (NUNCA QUEBRA)
# =========================
def gerar_resumo():
    ativos = carregar_portfolio()

    if not ativos:
        return "Não foi possível carregar sua carteira."

    tickers = [a["ticker"] for a in ativos]
    nomes = {a["ticker"]: a["nome"] for a in ativos}

    dados = buscar_precos(tickers)

    # 🔴 fallback se API falhar
    if not dados:
        return "No momento não foi possível acessar os dados do mercado."

    falas = []

    for item in dados:
        try:
            ticker = item.get("symbol")
            nome = nomes.get(ticker, ticker)

            preco = item.get("regularMarketPrice")
            variacao = item.get("regularMarketChangePercent")

            if preco is None or variacao is None:
                continue

            status = "em alta" if variacao > 0 else "em queda"

            falas.append(
                f"{nome} a {float(preco):.2f}, {status} de {abs(float(variacao)):.2f}%"
            )

        except Exception as e:
            print("Erro ativo:", e)
            continue

    if not falas:
        return "Não foi possível calcular sua carteira hoje."

    return "Resumo da sua carteira: " + ". ".join(falas)

# =========================
# ENDPOINTS
# =========================
@app.route("/")
def home():
    return "API da carteira ativa"

@app.route("/carteira")
def carteira():
    return jsonify({"resumo": gerar_resumo()})

# =========================
# RENDER FIX
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
