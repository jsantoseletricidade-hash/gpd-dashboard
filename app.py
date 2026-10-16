from datetime import date
from pathlib import Path
import pandas as pd
import streamlit as st

# =========================================================
# CONFIGURAÇÃO GERAL, EMPRESA E LOGOTIPO
# =========================================================
NOME_EMPRESA = "J SANTOS ELETRICIDADE"
DIAS_FERIAS_LEGAIS = 22  # Dias úteis de férias por ano

st.set_page_config(page_title=NOME_EMPRESA, page_icon="⚡", layout="wide")

# Ficheiros de dados locais (CSV)
FILE_TRABALHOS = "registo_trabalhos.csv"
FILE_FERIAS = "registo_ferias.csv"
FILE_MAPA = "mapa_semanal.csv"
FILE_SALDO_INICIAL = "saldo_inicial_ferias.csv"


# Funções de leitura e escrita
def carregar_dados(caminho, colunas):
  if Path(caminho).exists():
    return pd.read_csv(caminho)
  return pd.DataFrame(columns=colunas)


def guardar_dados(df, caminho):
  df.to_csv(caminho, index=False)


# Função para calcular dias úteis entre duas datas
def calcular_dias_uteis(data_inicio, data_fim):
  try:
    dias = pd.date_range(start=data_inicio, end=data_fim, freq="B")
    return len(dias)
  except:
    return 0


# Inicializar bases de dados
df_trabalhos = carregar_dados(
    FILE_TRABALHOS,
    [
        "Data",
        "Colaborador",
        "Cliente / Obra",
        "Descricao dos Trabalhos",
        "Material Gasto",
        "Horas",
    ],
)
df_ferias = carregar_dados(
    FILE_FERIAS, ["Colaborador", "Data Inicio", "Data Fim", "Dias", "Estado"]
)
df_mapa = carregar_dados(
    FILE_MAPA,
    [
        "Semana / Referencia",
        "Dia",
        "Colaborador / Equipa",
        "Obra / Destino",
        "Observacoes",
    ],
)
df_saldo_inicial = carregar_dados(
    FILE_SALDO_INICIAL, ["Colaborador", "Dias Ja Gozados"]
)

# =========================================================
# BARRA LATERAL (LOGOTIPO, NOME DA EMPRESA E PERFIL)
# =========================================================
if Path("logo.png").exists():
  st.sidebar.image("logo.png", width="stretch")
elif Path("logo.jpg").exists():
  st.sidebar.image("logo.jpg", width="stretch")

st.sidebar.title(f"⚡ {NOME_EMPRESA}")
st.sidebar.markdown("---")

perfil = st.sidebar.selectbox(
    "Seleciona o teu Perfil",
    ["👷 Colaborador / Eletricista", "🛠️ Administração / Gerência"],
)

st.sidebar.markdown("---")

# ---------------------------------------------------------
# PERFIL 1: COLABORADOR (Registo Diário e Férias)
# ---------------------------------------------------------
if perfil == "👷 Colaborador / Eletricista":
  st.title(f"👷 Portal do Colaborador — {NOME_EMPRESA}")
  st.markdown(
      "Regista aqui o teu trabalho diário, os materiais aplicados na obra e"
      " consulta o mapa semanal planeado."
  )

  aba_c1, aba_c2, aba_c3 = st.tabs(
      [
          "📋 Folha de Obra Diária",
          "🌴 Marcar Férias & Saldo",
          "📅 Consultar Mapa Semanal",
      ]
  )

  with aba_c1:
    st.subheader("Registar Tarefas e Material Gasto")
    with st.form("form_colab_trabalho", clear_on_submit=True):
      c1, c2 = st.columns(2)
      with c1:
        data_t = st.date_input("Data do Trabalho", value=date.today())
        nome_colab = st.text_input("O teu Nome")
      with c2:
        cliente_o = st.text_input("Cliente / Local da Obra")
        horas_t = st.number_input(
            "Horas Trabalhadas",
            min_value=0.5,
            max_value=16.0,
            step=0.5,
            value=8.0,
        )

      desc_t = st.text_area("Descrição detalhada dos trabalhos efetuados")
      mat_t = st.text_area(
          "Material Gasto (Ex: 50m cabo XV 3x2.5, 2 disjuntores 16A, etc.)"
      )

      btn_enviar_t = st.form_submit_button("Submeter Folha de Obra")
      if btn_enviar_t:
        if nome_colab and cliente_o:
          novo_reg = pd.DataFrame(
              [{
                  "Data": str(data_t),
                  "Colaborador": nome_colab,
                  "Cliente / Obra": cliente_o,
                  "Descricao dos Trabalhos": desc_t,
                  "Material Gasto": mat_t,
                  "Horas": horas_t,
              }]
          )
          df_trabalhos = pd.concat([df_trabalhos, novo_reg], ignore_index=True)
          guardar_dados(df_trabalhos, FILE_TRABALHOS)
          st.success("Folha de obra submetida com sucesso!")
        else:
          st.warning("Por favor, preenche o teu nome e o cliente/obra.")

  with aba_c2:
    st.subheader("Pedido de Férias e Saldo Disponível")

    # Consultar saldo do colaborador ao introduzir o nome
    colab_consulta = st.text_input(
        "Introduz o teu Nome para veres o teu saldo de férias:"
    )
    if colab_consulta:
      # 1. Obter saldo inicial definido pela gerência
      dias_iniciais = 0
      if not df_saldo_inicial.empty:
        match_saldo = df_saldo_inicial[
            df_saldo_inicial["Colaborador"].str.lower()
            == colab_consulta.lower()
        ]
        if not match_saldo.empty:
          dias_iniciais = match_saldo["Dias Ja Gozados"].values[0]

      # 2. Obter dias pedidos/aprovados na app
      dias_app = 0
      if not df_ferias.empty:
        df_colab_f = df_ferias[
            (df_ferias["Colaborador"].str.lower() == colab_consulta.lower())
            & (df_ferias["Estado"] != "Rejeitado")
        ]
        if "Dias" in df_colab_f.columns:
          dias_app = df_colab_f["Dias"].sum()

      total_gastos = dias_iniciais + dias_app
      dias_restantes = DIAS_FERIAS_LEGAIS - total_gastos

      kpi1, kpi2, kpi3 = st.columns(3)
      kpi1.metric("Direito Anual", f"{DIAS_FERIAS_LEGAIS} dias")
      kpi2.metric("Total Gozados / Pedidos", f"{total_gastos} dias")
      kpi3.metric("Dias Disponíveis", f"{dias_restantes} dias")
      st.markdown("---")

    with st.form("form_colab_ferias", clear_on_submit=True):
      c1, c2, c3 = st.columns(3)
      with c1:
        nome_f = st.text_input("Nome do Colaborador (Férias)")
      with c2:
        inicio_f = st.date_input("Data de Início", value=date.today())
      with c3:
        fim_f = st.date_input("Data de Fim", value=date.today())

      btn_enviar_f = st.form_submit_button("Solicitar Férias")
      if btn_enviar_f:
        if nome_f:
          if inicio_f > fim_f:
            st.error("A data de início não pode ser posterior à data de fim.")
          else:
            n_dias = calcular_dias_uteis(inicio_f, fim_f)
            nova_feria = pd.DataFrame(
                [{
                    "Colaborador": nome_f,
                    "Data Inicio": str(inicio_f),
                    "Data Fim": str(fim_f),
                    "Dias": n_dias,
                    "Estado": "Pendente",
                }]
            )
            df_ferias = pd.concat([df_ferias, nova_feria], ignore_index=True)
            guardar_dados(df_ferias, FILE_FERIAS)
            st.success(
                f"Pedido de férias ({n_dias} dias úteis) enviado com sucesso"
                " para aprovação!"
            )
        else:
          st.warning("Indica o teu nome.")

  with aba_c3:
    st.subheader("Mapa Semanal (Apenas Consulta)")
    st.markdown("Consulta para onde estás escalado esta semana:")
    if not df_mapa.empty:
      st.dataframe(df_mapa, width="stretch")
    else:
      st.info("Ainda não existe nenhum mapa semanal publicado pela gerência.")

# ---------------------------------------------------------
# PERFIL 2: ADMINISTRAÇÃO / GERÊNCIA (Planeamento e Controlo)
# ---------------------------------------------------------
elif perfil == "🛠️ Administração / Gerência":
  st.title(f"🛠️ Painel da Gerência — {NOME_EMPRESA}")
  st.markdown(
      "Gere o planeamento semanal das obras, aprova férias e define os saldos"
      " de férias da equipa."
  )

  aba_g1, aba_g2, aba_g3, aba_g4, aba_g5 = st.tabs([
      "📅 Gerir Mapa Semanal",
      "📋 Registos e Materiais (Equipa)",
      "🌴 Gestão de Férias & Saldos",
      "⚙️ Definir Saldo Inicial (Ano)",
      "📊 Exportar Dados",
  ])

  with aba_g1:
    st.subheader("Criar / Atualizar Planeamento Semanal")
    st.markdown(
        "Aqui defines para onde vai cada colaborador em cada dia da semana."
    )

    with st.form("form_admin_mapa", clear_on_submit=True):
      c1, c2 = st.columns(2)
      with c1:
        semana_ref = st.text_input(
            "Referência (Ex: Semana de 19 a 23 de Outubro)"
        )
        dia_semana = st.selectbox(
            "Dia da Semana",
            [
                "Segunda-feira",
                "Terça-feira",
                "Quarta-feira",
                "Quinta-feira",
                "Sexta-feira",
                "Fim de Semana",
            ],
        )
      with c2:
        colab_alocado = st.text_input("Colaborador / Equipa")
        obra_destino = st.text_input("Obra / Local de Destino / Tarefa")

      obs_admin = st.text_input(
          "Observações / Notas (Ex: Levar berbequim e tubagem)"
      )

      btn_gravar_mapa = st.form_submit_button(
          "Adicionar / Atualizar Planeamento"
      )
      if btn_gravar_mapa:
        if semana_ref and colab_alocado and obra_destino:
          novo_mapa = pd.DataFrame(
              [{
                  "Semana / Referencia": semana_ref,
                  "Dia": dia_semana,
                  "Colaborador / Equipa": colab_alocado,
                  "Obra / Destino": obra_destino,
                  "Observacoes": obs_admin,
              }]
          )
          df_mapa = pd.concat([df_mapa, novo_mapa], ignore_index=True)
          guardar_dados(df_mapa, FILE_MAPA)
          st.success("Planeamento semanal atualizado com sucesso!")
        else:
          st.warning("Preenche a referência, o colaborador e a obra/destino.")

    st.markdown("### Planeamento Atual Publicado")
    if not df_mapa.empty:
      st.dataframe(df_mapa, width="stretch")
      if st.button("Limpar Todo o Mapa Semanal"):
        df_mapa = pd.DataFrame(columns=df_mapa.columns)
        guardar_dados(df_mapa, FILE_MAPA)
        st.rerun()
    else:
      st.info("O mapa semanal está vazio.")

  with aba_g2:
    st.subheader("Histórico de Folhas de Obra e Materiais Gastos")
    if not df_trabalhos.empty:
      st.dataframe(df_trabalhos, width="stretch")
    else:
      st.info("Ainda não existem folhas de obra submetidas pelos colaboradores.")

  with aba_g3:
    st.subheader("Controlo Global de Férias e Saldo da Equipa")

    # Vamos construir um resumo consolidado combinando Saldo Inicial + Férias na App
    colaboradores_unicos = set()
    if not df_saldo_inicial.empty:
      colaboradores_unicos.update(df_saldo_inicial["Colaborador"].unique())
    if not df_ferias.empty:
      colaboradores_unicos.update(df_ferias["Colaborador"].unique())

    if colaboradores_unicos:
      lista_resumo = []
      for colab in sorted(colaboradores_unicos):
        # Dias iniciais
        d_inic = 0
        if not df_saldo_inicial.empty:
          m_s = df_saldo_inicial[
              df_saldo_inicial["Colaborador"].str.lower() == colab.lower()
          ]
          if not m_s.empty:
            d_inic = m_s["Dias Ja Gozados"].values[0]

        # Dias na App
        d_app = 0
        if not df_ferias.empty:
          m_f = df_ferias[
              (df_ferias["Colaborador"].str.lower() == colab.lower())
              & (df_ferias["Estado"] != "Rejeitado")
          ]
          if not m_f.empty and "Dias" in m_f.columns:
            d_app = m_f["Dias"].sum()

        total_g = d_inic + d_app
        restantes = DIAS_FERIAS_LEGAIS - total_g

        lista_resumo.append({
            "Colaborador": colab,
            "Saldo Inicial (Antes da App)": d_inic,
            "Férias Pedidas na App": d_app,
            "Total Gozados": total_g,
            "Dias Restantes": restantes,
        })

      df_resumo_global = pd.DataFrame(lista_resumo)
      st.markdown("### Resumo Consolidado por Colaborador")
      st.dataframe(df_resumo_global, width="stretch")

      st.markdown("### Lista Completa de Pedidos na App")
      if not df_ferias.empty:
        st.dataframe(df_ferias, width="stretch")

        col_aprov1, col_aprov2 = st.columns(2)
        with col_aprov1:
          registo_a_mudar = st.selectbox(
              "Seleciona a linha de férias a atualizar (índice)", df_ferias.index
          )
        with col_aprov2:
          novo_estado = st.selectbox(
              "Novo Estado", ["Aprovado", "Rejeitado", "Pendente"]
          )

        if st.button("Atualizar Estado das Férias"):
          df_ferias.loc[registo_a_mudar, "Estado"] = novo_estado
          guardar_dados(df_ferias, FILE_FERIAS)
          st.success("Estado atualizado com sucesso!")
          st.rerun()
      else:
        st.info("Não existem pedidos de férias registados na aplicação.")
    else:
      st.info(
          "Ainda não existem colaboradores com saldos ou pedidos registados."
      )

  with aba_g4:
    st.subheader(
        "Definir / Ajustar Saldo Inicial de Férias (Já gozados este ano)"
    )
    st.markdown(
        "Regista aqui os dias que cada colaborador já tinha gozado desde o"
        " início do ano antes de usarem a aplicação."
    )

    with st.form("form_saldo_inicial", clear_on_submit=True):
      col_s1, col_s2 = st.columns(2)
      with col_s1:
        nome_s = st.text_input("Nome do Colaborador")
      with col_s2:
        dias_s = st.number_input(
            "Dias já gozados este ano",
            min_value=0,
            max_value=22,
            step=1,
            value=0,
        )

      btn_gravar_s = st.form_submit_button("Guardar / Atualizar Saldo Inicial")
      if btn_gravar_s:
        if nome_s:
          # Verificar se já existe, atualizar ou adicionar
          if not df_saldo_inicial.empty and nome_s.lower() in df_saldo_inicial["Colaborador"].str.lower().values:
            df_saldo_inicial.loc[
                df_saldo_inicial["Colaborador"].str.lower()
                == nome_s.lower(),
                "Dias Ja Gozados",
            ] = dias_s
          else:
            novo_reg_s = pd.DataFrame(
                [{"Colaborador": nome_s, "Dias Ja Gozados": dias_s}]
            )
            df_saldo_inicial = pd.concat(
                [df_saldo_inicial, novo_reg_s], ignore_index=True
            )

          guardar_dados(df_saldo_inicial, FILE_SALDO_INICIAL)
          st.success(
              f"Saldo inicial de {dias_s} dias guardado para {nome_s}!"
          )
          st.rerun()
        else:
          st.warning("Indica o nome do colaborador.")

    st.markdown("### Tabela Atual de Saldos Iniciais Registados")
    if not df_saldo_inicial.empty:
      st.dataframe(df_saldo_inicial, width="stretch")
      if st.button("Apagar Todos os Saldos Iniciais"):
        df_saldo_inicial = pd.DataFrame(columns=df_saldo_inicial.columns)
        guardar_dados(df_saldo_inicial, FILE_SALDO_INICIAL)
        st.rerun()
    else:
      st.info("Ainda não foram definidos saldos iniciais.")

  with aba_g5:
    st.subheader("Exportação de Dados para Excel / CSV")
    c1, c2, c3 = st.columns(3)

    with c1:
      if not df_trabalhos.empty:
        csv_t = df_trabalhos.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Descarregar Trabalhos",
            csv_t,
            "trabalhos_geral.csv",
            "text/csv",
        )
    with c2:
      if not df_ferias.empty:
        csv_f = df_ferias.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Descarregar Férias", csv_f, "ferias_geral.csv", "text/csv"
        )
    with c3:
      if not df_mapa.empty:
        csv_m = df_mapa.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Descarregar Mapa", csv_m, "mapa_semanal_geral.csv", "text/csv"
        )