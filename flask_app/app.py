from flask import Flask, render_template, request, redirect, jsonify
from datetime import datetime
import mysql.connector
import json

# Inicializar a aplicação Flask
app = Flask(__name__)

# Função para obter uma nova conexão com o banco de dados
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="apibyte",
        password="190@Mudar",
        database="apibyte",
        charset='utf8mb4',
        collation='utf8mb4_general_ci'
    )

# Rotas já existentes

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/menu")
def menu():
    with open("flask_app/perfil.json", encoding='utf-8', errors='ignore') as f:
        vereadores = json.load(f)
 
    # Extraindo todos os vereadores para exibição
    vereadores_list = [
        {
            'id': int(id_),
            'nome_civil': v['nome_civil'],
            'partido': v['partido'],
            'foto': v['foto']
        }
        for id_, v in vereadores.items()
    ]
 
    return render_template("menu.html", vereadores=vereadores_list)
 
 

@app.route("/estatisticas")
def estatisticas():
    return render_template("estatisticas.html")

@app.route("/perfil/<int:id_vereador>")
def perfil(id_vereador):
    try:
        with open("flask_app/perfil.json", encoding='utf-8') as f:
            vereadores = json.load(f)
        vereador = vereadores.get(str(id_vereador))

        if vereador:
            filtro = request.args.get('filtro', 'projetos_aprovados')
            return render_template("perfil.html", vereador=vereador, filtro=filtro)
        else:
            return "Vereador não encontrado", 404
    except Exception as e:
        return f"Erro ao carregar o perfil do vereador: {e}", 500


@app.route('/perfil/filtros')
def filtros_vereador():
    vereador_id = request.args.get('vereador_id')
    filtro = request.args.get('filtro')

    try:
        with open('flask_app/leis_aprovadas_vereadores.json', encoding='utf-8') as file:
            leis_aprovadas = json.load(file)

        with open('flask_app/perfil.json', encoding='utf-8') as file:
            perfil = json.load(file)

        comissoes_validas = [
            (37, "Comissão de Cultura e Esportes"),
            (43, "Comissão de Economia, Finanças e Orçamento"),
            (26, "Comissão de Educação e Promoção Social"),
            (40, "Comissão de Ética"),
            (39, "Comissão de Justiça, Redação e Direitos Humanos"),
            (42, "Comissão de Meio Ambiente"),
            (41, "Comissão de Planejamento Urbano, Obras e Transportes"),
            (38, "Comissão de Saúde")
        ]
        comissoes_dict = {str(id): nome for id, nome in comissoes_validas}

        response_data = {}

        if filtro == 'projetos_aprovados':
            projetos_aprovados = leis_aprovadas.get(str(vereador_id), [])
            response_data['projetos_aprovados'] = projetos_aprovados if projetos_aprovados else "Nenhum projeto aprovado encontrado para este vereador."

        elif filtro == 'biografia':
            biografia = perfil.get(str(vereador_id), {}).get('biografia', "Informação biográfica não disponível")
            response_data['biografia'] = biografia

        elif filtro == 'frequencia_sessoes':
            frequencia = perfil.get(str(vereador_id), {})
            response_data['frequencia'] = {
                'presenca_totais': frequencia.get('presenca_totais', 'N/A'),
                'presenca_2021': frequencia.get('presenca_2021', 'N/A'),
                'presenca_2022': frequencia.get('presenca_2022', 'N/A'),
                'presenca_2023': frequencia.get('presenca_2023', 'N/A'),
                'presenca_2024': frequencia.get('presenca_2024', 'N/A'),
                'faltas_totais': frequencia.get('faltas_totais', 'N/A'),
                'faltas_2021': frequencia.get('faltas_2021', 'N/A'),
                'faltas_2022': frequencia.get('faltas_2022', 'N/A'),
                'faltas_2023': frequencia.get('faltas_2023', 'N/A'),
                'faltas_2024': frequencia.get('faltas_2024', 'N/A'),
                'faltas_justificadas_totais': frequencia.get('faltas_justificadas_totais', 'N/A'),
                'faltas_justificadas_2021': frequencia.get('faltas_justificadas_2021', 'N/A'),
                'faltas_justificadas_2022': frequencia.get('faltas_justificadas_2022', 'N/A'),
                'faltas_justificadas_2023': frequencia.get('faltas_justificadas_2023', 'N/A'),
                'faltas_justificadas_2024': frequencia.get('faltas_justificadas_2024', 'N/A')
            }

        elif filtro == 'proposicoes':
            proposicoes = perfil.get(str(vereador_id), {})
            response_data['proposicoes'] = {
                'mocoes': proposicoes.get('mocoes', 'N/A'),
                'projeto_de_lei': proposicoes.get('projeto_de_lei', 'N/A'),
                'projeto_de_lei_aprovados': proposicoes.get('projeto_de_lei_aprovados', 'N/A'),
                'requerimento': proposicoes.get('requerimento', 'N/A')
            }

        elif filtro == 'comissoes':
            comissoes_anos = {
                '2021': perfil.get(str(vereador_id), {}).get('comissoes_atuantes_2021_id', []),
                '2022': perfil.get(str(vereador_id), {}).get('comissoes_atuantes_2022_id', []),
                '2023': perfil.get(str(vereador_id), {}).get('comissoes_atuantes_2023_id', []),
                '2024': perfil.get(str(vereador_id), {}).get('comissoes_atuantes_2024_id', [])
            }
            
            comissoes_final = {}
            for ano, comissoes in comissoes_anos.items():
                if comissoes:  # Verifica se há comissões
                    nomes_comissoes = [comissoes_dict.get(str(comissao_id), f"Comissão ID {comissao_id} não encontrada") for comissao_id in comissoes]
                    comissoes_final[ano] = nomes_comissoes
            
            response_data['comissoes'] = comissoes_final
        
        # Adicionando o novo filtro 'Posicionamento em Votações'
        elif filtro == 'posicionamento_votacoes':
            try:
                with open('flask_app/extratos_votacao.json', encoding='utf-8') as file:
                    votacoes = json.load(file)

                # Mapeamento de IDs dos vereadores para nomes
                vereadores_validos = [
                    (35, 'Amélia Naomi'),
                    (238, 'Dr. José Claudio'),
                    (38, 'Dulce Rita'),
                    (247, 'Fabião Zagueiro'),
                    (40, 'Fernando Petiti'),
                    (43, 'Juliana Fraga'),
                    (246, 'Junior da Farmácia'),
                    (44, 'Juvenil Silvério'),
                    (45, 'Lino Bispo'),
                    (47, 'Marcão da Academia'),
                    (244, 'Marcelo Garcia'),
                    (242, 'Milton Vieira Filho'),
                    (243, 'Rafael Pascucci'),
                    (245, 'Renato Santiago'),
                    (50, 'Robertinho da Padaria'),
                    (240, 'Roberto Chagas'),
                    (234, 'Roberto do Eleven'),
                    (249, 'Rogério da ACASEM'),
                    (239, 'Thomaz Henrique'),
                    (55, 'Walter Hayashi'),
                    (237, 'Zé Luís')
                ]

                # Criar um dicionário para facilitar a busca
                vereadores_dict = {str(id): nome for id, nome in vereadores_validos}

                votacoes_filtradas = []
                for votacao in votacoes:
                    for voto in votacao['votos']:
                        if voto['id'] == str(vereador_id):
                            # Substituir o ID da autoria pelo nome do vereador
                            autoria_nome = vereadores_dict.get(votacao['Autoria'], f"Vereador ID {votacao['Autoria']} não encontrado")
                            votacoes_filtradas.append({
                                'titulo': votacao['titulo'],
                                'autoria': autoria_nome,  # Relacionar o nome do vereador pela autoria
                                'resultado': votacao['resultado'],
                                'voto': voto['voto']
                            })

                if votacoes_filtradas:
                    response_data['posicionamento_votacoes'] = votacoes_filtradas
                else:
                    response_data['posicionamento_votacoes'] = "Nenhum posicionamento em votações encontrado para este vereador."

            except Exception as e:
                print(f"Erro ao carregar os dados de votações: {e}")
                response_data['posicionamento_votacoes'] = "Erro ao carregar posicionamento em votações."

        return jsonify(response_data)

    except Exception as e:
        print(f"Erro ao carregar os dados: {e}")
        return jsonify({"error": "Erro ao carregar informações."}), 500


@app.route("/proposicoes_aprovadas")
def proposicoes_aprovadas():
    try:
        with open("flask_app/perfil.json", encoding='utf-8') as f:
            vereadores = json.load(f)
        
        # Converte o campo 'projeto_de_lei_aprovados' para inteiro em cada vereador
        for vereador in vereadores.values():
            vereador['projeto_de_lei_aprovados'] = int(vereador['projeto_de_lei_aprovados'])
        
        # Converte para uma lista de vereadores
        vereadores_lista = [v for v in vereadores.values()]

        # Ordena a lista em ordem decrescente de projetos aprovados
        vereadores_lista.sort(key=lambda x: x['projeto_de_lei_aprovados'], reverse=True)

        return render_template("proposicoes2.html", vereadores=vereadores_lista)

    except Exception as e:
        return f"Erro ao carregar proposições aprovadas: {e}", 500

@app.route("/sobre_nos")
def sobre_nos():
    return render_template("sobre_nos.html")


# Rota para exibir os comentários com filtros e para inserir novos comentários
@app.route("/comentarios", methods=["GET", "POST"])
def comentarios():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Criação dos dicionários (listas predefinidas)
    vereadores_validos = [
        (35, 'Amélia Naomi'),
        (238, 'Dr. José Claudio'),
        (38, 'Dulce Rita'),
        (247, 'Fabião Zagueiro'),
        (40, 'Fernando Petiti'),
        (43, 'Juliana Fraga'),
        (246, 'Junior da Farmácia'),
        (44, 'Juvenil Silvério'),
        (45, 'Lino Bispo'),
        (47, 'Marcão da Academia'),
        (244, 'Marcelo Garcia'),
        (242, 'Milton Vieira Filho'),
        (243, 'Rafael Pascucci'),
        (245, 'Renato Santiago'),
        (50, 'Robertinho da Padaria'),
        (240, 'Roberto Chagas'),
        (234, 'Roberto do Eleven'),
        (249, 'Rogério da ACASEM'),
        (239, 'Thomaz Henrique'),
        (55, 'Walter Hayashi'),
        (237, 'Zé Luís')
    ]

    comissoes_validas = [
        (37, "Comissão de Cultura e Esportes"),
        (43, "Comissão de Economia, Finanças e Orçamento"),
        (26, "Comissão de Educação e Promoção Social"),
        (40, "Comissão de Ética"),
        (39, "Comissão de Justiça, Redação e Direitos Humanos"),
        (42, "Comissão de Meio Ambiente"),
        (41, "Comissão de Planejamento Urbano, Obras e Transportes"),
        (38, "Comissão de Saúde")
    ]

    partidos_validos = [
        (1, "Avante"),
        (2, "Cidadania"),
        (3, "Democracia Cristã (DC)"),
        (4, "Movimento Democrático Brasileiro (MDB)"),
        (5, "Partido Comunista Brasileiro (PCB)"),
        (6, "Partido Comunista do Brasil (PCdoB)"),
        (7, "Partido da Causa Operária (PCO)"),
        (8, "Partido da Mulher Brasileira (PMB)"),
        (9, "Partido da Renovação Democrática (PRD)"),
        (10, "Partido Democrático Trabalhista (PDT)"),
        (11, "Partido Liberal (PL)"),
        (12, "Partido Novo (NOVO)"),
        (13, "Partido Progressistas (PP)"),
        (14, "Partido Republicano da Ordem Social (PROS)"),
        (15, "Partido Renovador Trabalhista Brasileiro (PRTB)"),
        (16, "Partido Social Cristão (PSC)"),
        (17, "Partido Social Democrático (PSD)"),
        (18, "Partido Social Democracia Brasileira (PSDB)"),
        (19, "Partido Socialista Brasileiro (PSB)"),
        (20, "Partido Socialismo e Liberdade (PSOL)"),
        (21, "Partido Socialista dos Trabalhadores Unificado (PSTU)"),
        (22, "Partido Trabalhista Brasileiro (PTB)"),
        (23, "Partido dos Trabalhadores (PT)"),
        (24, "Podemos (PODE)"),
        (25, "Rede Sustentabilidade (REDE)"),
        (26, "Republicanos"),
        (27, "Solidariedade"),
        (28, "Unidade Popular (UP)"),
        (29, "União Brasil"),
        (30, "Aliança pelo Brasil (em formação)"),
        (31, "Patriota"),
        (32, "Partido Verde (PV)"),
        (33, "Progressistas (PP)")
    ]

    # Converte as listas para dicionários
    vereadores = {id: nome for id, nome in vereadores_validos}
    comissoes = {id: nome for id, nome in comissoes_validas}
    partidos = {id: nome for id, nome in partidos_validos}

    if request.method == "POST":
        comentario = request.form['comentario']
        vereador_id = request.form.get('vereador_id') or None
        partido_id = request.form.get('partido_id') or None
        comissao_id = request.form.get('comissao_id') or None

        if not vereador_id and not partido_id and not comissao_id:
            return "Erro: Pelo menos um filtro (vereador, partido ou comissão) deve ser preenchido."

        cursor.execute("""
            INSERT INTO comentarios (comentario, vereador_id, partido_id, comissao_id)
            VALUES (%s, %s, %s, %s)
        """, (comentario, vereador_id, partido_id, comissao_id))
        db.commit()

    # Buscando os comentários
    cursor.execute("SELECT * FROM comentarios")
    comentarios = cursor.fetchall()

    # Formatar as datas
    for comentario in comentarios:
        if comentario['data']:  # Verifica se o campo 'data' existe e não está vazio
            comentario['data'] = comentario['data'].strftime('%d/%m/%Y %H:%M')

    # Busca os últimos 5 comentários (ou a quantidade que desejar)
    cursor.execute("SELECT * FROM comentarios ORDER BY data DESC LIMIT 5")
    ultimos_comentarios = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("comentarios.html", vereadores=vereadores, partidos=partidos, comissoes=comissoes, comentarios=comentarios, ultimos_comentarios=ultimos_comentarios)

# Rota para aplicar os filtros nos comentários
@app.route("/comentarios_filtro", methods=["GET"])
def comentarios_filtro():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    vereador_id = request.args.get('vereador_id')
    partido_id = request.args.get('partido_id')
    comissao_id = request.args.get('comissao_id')

    query = "SELECT * FROM comentarios WHERE 1=1"
    params = []

    if vereador_id:
        query += " AND vereador_id = %s"
        params.append(vereador_id)
    if partido_id:
        query += " AND partido_id = %s"
        params.append(partido_id)
    if comissao_id:
        query += " AND comissao_id = %s"
        params.append(comissao_id)

    cursor.execute(query, params)
    comentarios = cursor.fetchall()

    # Converte listas para dicionários
    cursor.execute("SELECT id, nome FROM vereadores")
    vereadores_list = cursor.fetchall()
    vereadores = {v['id']: v['nome'] for v in vereadores_list}

    cursor.execute("SELECT id, nome FROM partidos")
    partidos_list = cursor.fetchall()
    partidos = {p['id']: p['nome'] for p in partidos_list}

    cursor.execute("SELECT id, nome FROM comissoes")
    comissoes_list = cursor.fetchall()
    comissoes = {c['id']: c['nome'] for c in comissoes_list}

    cursor.close()
    db.close()

    return render_template("comentarios.html", comentarios=comentarios, vereadores=vereadores, partidos=partidos, comissoes=comissoes)

# Rodar a aplicação
if __name__ == "__main__":
    app.run(debug=True)
