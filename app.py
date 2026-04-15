from flask import Flask, jsonify
import yfinance as yf

app = Flask(__name__)

ativos = {
    "BBAS3.SA": "Banco do Brasil",
    "EGIE3.SA": "Engie Brasil",
    "ITSA4.SA": "Itaúsa",
    "VALE3.SA": "Vale",
    "WEGE3.SA": "WEG",
    "GOOGL": "Google",
    "IVV": "ETF S&P500"
}

def resumo():
    textos = []

    for t, nome in ativos.items():
        try:
            data = yf.Ticker(t).history(period="2d")
            if data.empty:
                continue

            atual = data["Close"].iloc[-1]
            anterior = data["Close"].iloc[-2]

            var = ((atual - anterior) / anterior) * 100

            status = "em alta" if var > 0 else "em queda"

            moeda = "reais" if ".SA" in t else "dólares"

            textos.append(
                f"{nome} a {atual:.2f} {moeda}, {status} de {abs(var):.2f}%"
            )

        except:
            continue

    return "Resumo da carteira: " + ". ".join(textos)


@app.route("/")
def home():
    return "API ativa"

@app.route("/carteira")
def carteira():
    return jsonify({"resumo": resumo()})
