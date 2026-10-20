import { useEffect, useState } from "react";
import "./App.css";

const moeda = (v) =>
  v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

const dataBR = (iso) => iso.split("-").reverse().join("/");

export default function App() {
  const [dados, setDados] = useState([]);
  const [filtro, setFiltro] = useState("Todas");
  const [erro, setErro] = useState("");

  useEffect(() => {
    fetch("http://localhost:5000/api/movimentacoes")
      .then((r) => r.json())
      .then(setDados)
      .catch(() => setErro("Não foi possível carregar os dados. A API está rodando?"));
  }, []);

  const categorias = ["Todas", ...new Set(dados.map((d) => d.classificacao))];
  const visiveis = filtro === "Todas" ? dados : dados.filter((d) => d.classificacao === filtro);

  const entradas = visiveis.filter((d) => d.valor > 0).reduce((s, d) => s + d.valor, 0);
  const saidas = visiveis.filter((d) => d.valor < 0).reduce((s, d) => s + d.valor, 0);
  const saldo = entradas + saidas;

  return (
    <main className="container">
      <h1>Extrato Bancário</h1>
      {erro && <p className="erro">{erro}</p>}

      <section className="cards">
        <div className="card entrada"><span>Entradas</span><strong>{moeda(entradas)}</strong></div>
        <div className="card saida"><span>Saídas</span><strong>{moeda(saidas)}</strong></div>
        <div className="card saldo"><span>Saldo</span><strong>{moeda(saldo)}</strong></div>
      </section>

      <label className="filtro">
        Classificação:{" "}
        <select value={filtro} onChange={(e) => setFiltro(e.target.value)}>
          {categorias.map((c) => <option key={c}>{c}</option>)}
        </select>
        <span> — {visiveis.length} movimentações</span>
      </label>

      <table>
        <thead>
          <tr><th>Data</th><th>Descrição</th><th>Classificação</th><th className="num">Valor</th></tr>
        </thead>
        <tbody>
          {visiveis.map((d) => (
            <tr key={d.id}>
              <td>{dataBR(d.data)}</td>
              <td>{d.descricao}</td>
              <td>{d.classificacao}</td>
              <td className={"num " + (d.valor >= 0 ? "pos" : "neg")}>{moeda(d.valor)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}