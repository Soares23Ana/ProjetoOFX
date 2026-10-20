import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)


def conectar():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode="require",
    )


@app.route("/api/movimentacoes")
def listar():
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, data_movimentacao, valor, descricao, classificacao
        FROM movimentacoes
        ORDER BY data_movimentacao, id
        """
    )
    dados = [
        {
            "id": r[0],
            "data": r[1].strftime("%Y-%m-%d"),
            "valor": float(r[2]),
            "descricao": r[3],
            "classificacao": r[4] or "Sem classificação",
        }
        for r in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return jsonify(dados)


if __name__ == "__main__":
    app.run(port=5000, debug=True)