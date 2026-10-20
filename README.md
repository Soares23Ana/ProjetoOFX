# Projeto OFX

Leitura de extrato bancário (OFX) com Python e carga em PostgreSQL (ETL simplificado).

## Como executar
1. `python -m venv venv` e ative o ambiente (`venv\Scripts\activate` no Windows)
2. `pip install -r requirements.txt`
3. Copie `.env.example` para `.env` e preencha os dados do banco
4. Crie a tabela `movimentacoes` (SQL abaixo)
5. `python main.py` (exibe o extrato e os totais)
6. `python carga.py` (grava no PostgreSQL, ignorando duplicadas)

## Tabela
```sql
CREATE TABLE movimentacoes (
    id SERIAL PRIMARY KEY,
    data_movimentacao DATE,
    valor NUMERIC(15,2),
    descricao VARCHAR(255)
);
```
