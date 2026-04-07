# genial-darf-daytrade
Aplicativo Python/StreamLit que faz leitura de notas fiscais da Genial Investimentos para daytrade e faz cálculo de valores para DARF

# Calculadora DARF - Day Trade Genial

**Ferramenta para calcular automaticamente o DARF de operações de Day Trade** a partir das **Notas de Corretagem da Genial Investimentos** (mercado futuro - WIN, WDO, etc.).

---

## ✨ Funcionalidades

- Leitura automática de PDFs de Notas de Corretagem da Genial CCTVM
- Cálculo correto de **DARF mensal** para Day Trade (alíquota de 20%)
- Dedução automática do **IRRF retido na fonte (1%)**
- Tratamento de **prejuízos acumulados** entre meses
- Respeito à regra da **DARF mínima de R$ 10,00** (acúmulo para o mês seguinte)
- Cálculo da data de vencimento (último dia útil do mês seguinte)
- Gráfico interativo de resultado mensal
- Exportação para CSV
- Interface moderna e intuitiva com Streamlit

---

## Como usar

### 1. Instalação

```bash
git clone https://github.com/crincones/genial-darf-daytrade.git
cd genial-darf-daytrade

# Recomendado: criar ambiente virtual
python -m venv venv
source venv/bin/activate    # Linux/Mac
# venv\Scripts\activate     # Windows

pip install streamlit pdfplumber pandas plotly
````

### 2. Executar

```bash
streamlit run app.py
```

## 3. Como carregar as notas

1. Acesse o **Portal do Investidor** da Genial
2. Baixe as **Notas de Corretagem** do mês desejado (arquivo PDF)
3. Na ferramenta, clique em **"Selecione um ou mais arquivos PDF..."**
4. Carregue **todos os PDFs do mês** (é possível subir vários arquivos de uma vez)
5. Aguarde o processamento

> **Importante:** Para o cálculo estar correto, você **deve** carregar **todas** as notas de corretagem dos meses do ano corrente.

---

## ⚠️ Atenção Importante

- Esta ferramenta considera **prejuízos de meses anteriores** para compensar lucros futuros (dentro da mesma modalidade — Day Trade).
- Se você **não carregar todas as notas** de um mês, o prejuízo acumulado pode ser calculado de forma incorreta, gerando DARF errada.
- Sempre verifique se todas as notas do mês foram incluídas antes de confiar no resultado.

**Esta é uma ferramenta auxiliar.**  
O cálculo é feito com base na legislação vigente (IN RFB 1.585/2015), mas **não substitui** o trabalho de um contador ou consultor tributário.

---

## ⚖️ Responsabilidade e Uso

Este software é fornecido **"no estado em que se encontra" (AS IS)**.

- O uso desta ferramenta é de **total responsabilidade do usuário**.
- O desenvolvedor **não se responsabiliza** por eventuais erros de cálculo, multas, juros ou problemas com a Receita Federal.
- Recomenda-se fortemente validar os resultados com um contador especializado em renda variável.

**Não é permitida a venda ou uso comercial** desta ferramenta sem autorização prévia do autor.

---

## Licença

Este projeto está licenciado sob a **MIT License** com a seguinte ressalva adicional:

> O software é fornecido sem qualquer garantia, expressa ou implícita, incluindo, mas não se limitando a, garantias de comercialização, adequação a um propósito específico e não violação. Em nenhuma circunstância os autores ou titulares dos direitos autorais serão responsáveis por qualquer reclamação, danos ou outra responsabilidade, seja em ação de contrato, delito ou de outra forma, decorrente de, ou em conexão com o software ou o uso ou outras negociações no software.

Veja o arquivo [`LICENSE`](LICENSE) para mais detalhes.

---

## Tecnologias utilizadas

- Python
- Streamlit
- pdfplumber
- Pandas
- Plotly

---

## Contribuindo

Contribuições são bem-vindas!  
Sinta-se à vontade para abrir **Issues** ou **Pull Requests**.

Se encontrar algum PDF que não é lido corretamente, por favor, abra uma Issue enviando (se possível) um exemplo **anonimizado** da nota.

---

## Aviso Legal Final

Esta ferramenta **não tem vínculo** com a Genial Investimentos.  
Foi desenvolvida de forma independente por um investidor para uso próprio e agora disponibilizada à comunidade.

Sempre consulte um profissional de contabilidade para assuntos tributários.

---

**Feito com ❤️ por traders para traders**

Quer ajudar a melhorar o projeto? Deixe uma ⭐ no repositório!
