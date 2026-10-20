import os
import psycopg2
from dotenv import load_dotenv
from ofxparse import OfxParser

load_dotenv()

# 1. Extração: ler o OFX
with open("extrato.ofx", "rb") as arquivo:
    ofx = OfxParser.parse(arquivo)

transacoes = ofx.account.statement.transactions

# 2. Conexão com o Neon
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    sslmode="require"
)
cur = conn.cursor()

# 3. Carga: inserir cada transação, ignorando duplicadas
inseridas = 0

for t in transacoes:
    cur.execute(
        """
        INSERT INTO movimentacoes (data_movimentacao, valor, descricao)
        SELECT %s, %s, %s
        WHERE NOT EXISTS (
            SELECT 1 FROM movimentacoes
            WHERE data_movimentacao = %s AND valor = %s AND descricao = %s
        )
        """,
        (t.date.date(), t.amount, t.memo or t.payee,
         t.date.date(), t.amount, t.memo or t.payee)
    )
    inseridas += cur.rowcount

conn.commit()
cur.close()
conn.close()

print(f"{inseridas} novas movimentações gravadas; "
      f"{len(transacoes) - inseridas} duplicadas ignoradas.")