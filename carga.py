import os
import psycopg2
from dotenv import load_dotenv
from ofxparse import OfxParser

load_dotenv()


def classificar(descricao, valor):
    if valor > 0:
        return "Receita"
    d = (descricao or "").upper()
    regras = [
        ("Despesa fixa", ["ALUGUEL", "ENERGIA", "INTERNET", "ASSINATURA"]),
        ("Pessoal", ["FOLHA"]),
        ("Material e equipamentos", ["MATERIAL", "EQUIPAMENTOS"]),
        ("Veículos", ["ESTACIONAMENTO", "VEICULO"]),
    ]
    for categoria, palavras in regras:
        if any(p in d for p in palavras):
            return categoria
    return "Outros"


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

# 3. Carga: inserir cada transação classificada, ignorando duplicadas
inseridas = 0

for t in transacoes:
    descricao = t.memo or t.payee
    classificacao = classificar(descricao, t.amount)
    cur.execute(
        """
        INSERT INTO movimentacoes (data_movimentacao, valor, descricao, classificacao)
        SELECT %s, %s, %s, %s
        WHERE NOT EXISTS (
            SELECT 1 FROM movimentacoes
            WHERE data_movimentacao = %s AND valor = %s AND descricao = %s
        )
        """,
        (t.date.date(), t.amount, descricao, classificacao,
         t.date.date(), t.amount, descricao)
    )
    inseridas += cur.rowcount

conn.commit()
cur.close()
conn.close()

print(f"{inseridas} novas movimentações gravadas; "
      f"{len(transacoes) - inseridas} duplicadas ignoradas.")