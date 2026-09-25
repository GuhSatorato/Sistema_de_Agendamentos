# Relatório Técnico de Entrega: Sistema de Agendamentos (Academia da Saúde)

**Projeto:** Sistema AgendaFácil — Academia da Saúde (PIESC II)  
**Estudante Líder / Apresentador:** Gustavo Henrique Satorato — RA: 202973-25  
**Data da Entrega:** 24 de Setembro de 2026  
**Versão do Produto Entregue:** `v1.0.0-stable-offline`  

---

## 1. Identificação do Produto e Objetivo

O **Sistema AgendaFácil (Academia da Saúde)** é uma aplicação web monolítica voltada para a gestão de fluxo, agendamento de consultas e acompanhamento histórico de cidadãos atendidos gratuitamente por serviços de fisioterapia, condicionamento físico adaptado e reabilitação motora.

### 1.1 Objetivo da Entrega
Disponibilizar uma versão estável, autossuficiente e executável em ambiente de intranet/offline, substituindo o método manual de cadernos de papel e agendas físicas. O sistema elimina conflitos de horários entre instrutores, registra a evolução física em cada atendimento e viabiliza a consulta rápida do prontuário do paciente pela recepção.

---

## 2. README Operacional do Repositório (`README.md`)

```markdown
# Sistema de Agendamentos — Academia da Saúde

Sistema web para controle de agendamentos, triagem de pacientes e histórico de atendimentos desenvolvido para a Academia da Saúde.

## Tecnologias Empregadas
- **Linguagem Backend:** Python 3.10+
- **Framework Web:** Flask 3.0+
- **Banco de Dados:** SQLite3 (base relacional em arquivo local)
- **Frontend / Interface:** HTML5, CSS3 com Bootstrap 5 (CDN) e Vanilla JavaScript
- **Mecanismo de Templates:** Jinja2

## Pré-requisitos
- Python 3 instalado no sistema operacional ([Download oficial](https://www.python.org/downloads/))
- Navegador web moderno (Google Chrome, Microsoft Edge ou Mozilla Firefox)

## Instruções de Execução Passo a Passo

1. Abra o terminal ou Prompt de Comando (CMD) na pasta raiz do projeto:
   ```bash
   cd Sistema_de_Agendamentos
   ```

2. (Opcional, mas recomendado) Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   # No Windows:
   venv\Scripts\activate
   # No Linux/macOS:
   source venv/bin/activate
   ```

3. Instale o microframework Flask:
   ```bash
   pip install flask
   ```

4. Inicie o servidor da aplicação:
   ```bash
   python app.py
   ```

5. Acesse a aplicação no seu navegador:
   Abra o endereço [http://127.0.0.1:5000](http://127.0.0.1:5000)

> **Nota Operacional:** O banco de dados `database.db` é provisionado automaticamente com todas as tabelas e índices necessários no primeiro arranque do servidor.
```

---

## 3. Código-Fonte Completo e Consolidado

Abaixo constam os quatro arquivos que compõem a arquitetura funcional da entrega:

### 3.1 Backend Central (`app.py`)

```python
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "academia_saude_piesc_secret_key"

def conectar_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_banco():
    conn = conectar_db()
    # Tabela de pacientes
    conn.execute('''
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            obs TEXT
        )
    ''')
    # Tabela de agendamentos e historico
    conn.execute('''
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER,
            data TEXT NOT NULL,
            horario TEXT NOT NULL,
            status TEXT DEFAULT 'Agendado',
            descricao TEXT,
            FOREIGN KEY (paciente_id) REFERENCES pacientes (id)
        )
    ''')
    conn.commit()
    conn.close()

# Rota 1: Tela Principal (Agenda do Dia / Ativos)
@app.route('/')
def index():
    conn = conectar_db()
    agendamentos = conn.execute('''
        SELECT a.id, a.data, a.horario, a.status, a.descricao, p.nome, p.telefone 
        FROM agendamentos a 
        JOIN pacientes p ON a.paciente_id = p.id 
        WHERE a.status != 'Concluído'
        ORDER BY a.data ASC, a.horario ASC
    ''').fetchall()
    conn.close()
    return render_template('index.html', agendamentos=agendamentos)

# Rota 2: Listagem e Cadastro de Pacientes
@app.route('/pacientes')
def pacientes():
    conn = conectar_db()
    lista = conn.execute('SELECT * FROM pacientes ORDER BY nome ASC').fetchall()
    conn.close()
    return render_template('pacientes.html', pacientes=lista)

@app.route('/salvar_paciente', methods=['POST'])
def salvar_paciente():
    nome = request.form.get('nome', '').strip()
    telefone = request.form.get('telefone', '').strip()
    obs = request.form.get('obs', '').strip()

    if not nome:
        flash('O nome do paciente é obrigatório!', 'danger')
        return redirect(url_for('pacientes'))

    conn = conectar_db()
    conn.execute('INSERT INTO pacientes (nome, telefone, obs) VALUES (?, ?, ?)', (nome, telefone, obs))
    conn.commit()
    conn.close()
    flash(f'Paciente {nome} cadastrado com sucesso!', 'success')
    return redirect(url_for('pacientes'))

# Rota 3: Tela de Novo Agendamento
@app.route('/agendar')
def agendar():
    conn = conectar_db()
    lista_pacientes = conn.execute('SELECT id, nome FROM pacientes ORDER BY nome ASC').fetchall()
    conn.close()
    return render_template('agendar.html', pacientes=lista_pacientes)

@app.route('/salvar_agendamento', methods=['POST'])
def salvar_agendamento():
    paciente_id = request.form.get('paciente_id')
    data = request.form.get('data')
    horario = request.form.get('horario')
    descricao = request.form.get('descricao', '').strip()

    if not paciente_id or not data or not horario:
        flash('Preencha todos os campos obrigatórios (Paciente, Data e Horário)!', 'warning')
        return redirect(url_for('agendar'))

    conn = conectar_db()
    # Verificação de colisão de horário
    conflito = conn.execute('''
        SELECT id FROM agendamentos 
        WHERE data = ? AND horario = ? AND status != 'Cancelado'
    ''', (data, horario)).fetchone()

    if conflito:
        conn.close()
        flash(f'Horário indisponível! Já existe um atendimento agendado para o dia {data} às {horario}.', 'danger')
        return redirect(url_for('agendar'))

    conn.execute('''
        INSERT INTO agendamentos (paciente_id, data, horario, status, descricao) 
        VALUES (?, ?, ?, 'Agendado', ?)
    ''', (paciente_id, data, horario, descricao))
    conn.commit()
    conn.close()
    flash('Horário agendado com sucesso!', 'success')
    return redirect(url_for('index'))

# Rota 4: Atendimento do Paciente (Finalizar ou Remarcar)
@app.route('/atender/<int:id>')
def atender(id):
    conn = conectar_db()
    agendamento = conn.execute('''
        SELECT a.id, a.data, a.horario, a.descricao, a.paciente_id, p.nome, p.telefone, p.obs as obs_medica
        FROM agendamentos a
        JOIN pacientes p ON a.paciente_id = p.id
        WHERE a.id = ?
    ''', (id,)).fetchone()
    conn.close()

    if not agendamento:
        flash('Agendamento não encontrado!', 'warning')
        return redirect(url_for('index'))

    return render_template('atendimento.html', agendamento=agendamento)

@app.route('/finalizar_atendimento', methods=['POST'])
def finalizar_atendimento():
    agendamento_id = request.form.get('agendamento_id')
    descricao_consulta = request.form.get('descricao_consulta', '').strip()
    acao = request.form.get('acao')

    conn = conectar_db()
    conn.execute('''
        UPDATE agendamentos 
        SET status = 'Concluído', descricao = ? 
        WHERE id = ?
    ''', (descricao_consulta, agendamento_id))
    conn.commit()
    conn.close()

    if acao == 'remarcar':
        flash('Atendimento registrado! Prossiga com a nova marcação.', 'info')
        return redirect(url_for('agendar'))

    flash('Atendimento concluído e registrado no prontuário histórico do paciente!', 'success')
    return redirect(url_for('index'))

# Rota 5: Histórico do Paciente
@app.route('/historico/<int:paciente_id>')
def historico(paciente_id):
    conn = conectar_db()
    paciente = conn.execute('SELECT * FROM pacientes WHERE id = ?', (paciente_id,)).fetchone()
    consultas = conn.execute('''
        SELECT data, horario, status, descricao 
        FROM agendamentos 
        WHERE paciente_id = ? 
        ORDER BY data DESC, horario DESC
    ''', (paciente_id,)).fetchall()
    conn.close()
    return render_template('historico.html', paciente=paciente, consultas=consultas)

# Rota 6: Exclusão de Agendamento
@app.route('/excluir/<int:id>')
def excluir(id):
    conn = conectar_db()
    conn.execute('DELETE FROM agendamentos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Agendamento cancelado e removido da grade.', 'secondary')
    return redirect(url_for('index'))

if __name__ == '__main__':
    inicializar_banco()
    app.run(debug=False)
```

---

### 3.2 Template da Agenda Principal (`templates/index.html`)

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agenda — Academia da Saúde</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-success shadow-sm">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/">Academia da Saúde</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link active" href="/">Agenda</a>
                <a class="nav-link" href="/pacientes">Pacientes</a>
                <a class="nav-link" href="/agendar">Novo Agendamento</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <!-- Alertas do Sistema -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <div class="card shadow-sm border-0">
            <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
                <h5 class="mb-0 text-success fw-bold">Atendimentos Agendados</h5>
                <a href="/agendar" class="btn btn-success btn-sm">+ Novo Agendamento</a>
            </div>
            <div class="card-body p-0">
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th>Data</th>
                                <th>Horário</th>
                                <th>Paciente</th>
                                <th>Telefone</th>
                                <th>Status</th>
                                <th class="text-end pe-4">Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for a in agendamentos %}
                            <tr>
                                <td><span class="fw-semibold">{{ a.data }}</span></td>
                                <td>{{ a.horario }}</td>
                                <td>{{ a.nome }}</td>
                                <td>{{ a.telefone or 'Não informado' }}</td>
                                <td><span class="badge bg-primary">{{ a.status }}</span></td>
                                <td class="text-end pe-4">
                                    <a href="/atender/{{ a.id }}" class="btn btn-sm btn-outline-success">Atender</a>
                                    <a href="/excluir/{{ a.id }}" class="btn btn-sm btn-outline-danger" onclick="return confirm('Deseja realmente remover este agendamento?');">Excluir</a>
                                </td>
                            </tr>
                            {% else %}
                            <tr>
                                <td colspan="6" class="text-center py-4 text-muted">
                                    Nenhum atendimento pendente na grade. Clique em <strong>Novo Agendamento</strong> para incluir.
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

---

### 3.3 Template de Atendimento (`templates/atendimento.html`)

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Atendimento — Academia da Saúde</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-success shadow-sm">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/">Academia da Saúde</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/">Agenda</a>
                <a class="nav-link" href="/pacientes">Pacientes</a>
                <a class="nav-link" href="/agendar">Novo Agendamento</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="col-lg-8 mx-auto">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-white py-3">
                    <h5 class="mb-0 text-success fw-bold">Registro de Atendimento</h5>
                </div>
                <div class="card-body p-4">
                    <div class="alert alert-info mb-4">
                        <h6 class="alert-heading fw-bold mb-1">Paciente: {{ agendamento.nome }}</h6>
                        <small class="text-muted d-block">Data marcada: {{ agendamento.data }} às {{ agendamento.horario }} | Contato: {{ agendamento.telefone or 'Sem telefone' }}</small>
                        {% if agendamento.obs_medica %}
                        <hr class="my-2">
                        <small><strong>Observações Clínicas Pré-existentes:</strong> {{ agendamento.obs_medica }}</small>
                        {% endif %}
                    </div>

                    <form action="/finalizar_atendimento" method="POST">
                        <input type="hidden" name="agendamento_id" value="{{ agendamento.id }}">
                        
                        <div class="mb-4">
                            <label class="form-label fw-semibold">Relatório e Evolução da Consulta / Treino:</label>
                            <textarea name="descricao_consulta" class="form-control" rows="5" placeholder="Descreva os exercícios realizados, queixas álgicas, evolução motora ou orientações fornecidas ao paciente..." required></textarea>
                        </div>

                        <div class="d-flex gap-2 justify-content-end">
                            <a href="/" class="btn btn-outline-secondary">Voltar sem Salvar</a>
                            <button type="submit" name="acao" value="remarcar" class="btn btn-outline-warning text-dark fw-semibold">Finalizar e Remarcar</button>
                            <button type="submit" name="acao" value="finalizar" class="btn btn-success fw-semibold">Finalizar Atendimento</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

---

### 3.4 Template de Histórico do Prontuário (`templates/historico.html`)

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Histórico — Academia da Saúde</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-success shadow-sm">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/">Academia da Saúde</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/">Agenda</a>
                <a class="nav-link active" href="/pacientes">Pacientes</a>
                <a class="nav-link" href="/agendar">Novo Agendamento</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="card shadow-sm border-0 mb-4">
            <div class="card-body p-4">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h4 class="fw-bold text-success mb-1">{{ paciente.nome }}</h4>
                        <p class="text-muted mb-1">Telefone: {{ paciente.telefone or 'Não informado' }}</p>
                        <p class="mb-0 text-secondary"><small><strong>Condição Geral / Observações:</strong> {{ paciente.obs or 'Nenhum registro prévio.' }}</small></p>
                    </div>
                    <a href="/pacientes" class="btn btn-outline-secondary btn-sm">Voltar para Pacientes</a>
                </div>
            </div>
        </div>

        <h5 class="fw-bold text-dark mb-3">Histórico de Consultas e Atendimentos</h5>

        {% for c in consultas %}
        <div class="card shadow-sm border-0 mb-3">
            <div class="card-body">
                <div class="d-flex justify-content-between">
                    <span class="fw-bold text-dark">Data: {{ c.data }} às {{ c.horario }}</span>
                    <span class="badge {% if c.status == 'Concluído' %}bg-success{% else %}bg-secondary{% endif %}">{{ c.status }}</span>
                </div>
                <hr class="my-2">
                <p class="mb-0 text-secondary">{{ c.descricao or 'Sem observações registradas no momento da consulta.' }}</p>
            </div>
        </div>
        {% else %}
        <div class="alert alert-light border text-center py-4 text-muted">
            Este paciente ainda não possui histórico de atendimentos finalizados.
        </div>
        {% endfor %}
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

---

## 4. Recursos Entregues e Funcionalidades Operacionais

| Módulo | Recurso Implementado | Descrição Funcional |
| :--- | :--- | :--- |
| **Triagem & Cadastro** | Cadastro de Pacientes | Formulário com campos de nome, telefone e observações clínicas permanentes (patologias crônicas, cirurgias). |
| **Marcação de Consultas** | Validação de Conflito de Horário | Algoritmo em Python que bloqueia submissões para o mesmo dia e horário caso já haja agendamento não cancelado. |
| **Agenda Central** | Painel da Recepção | Listagem organizada cronologicamente dos pacientes com botões de ação direta (*Atender* e *Excluir*). |
| **Atendimento Clínico** | Finalização e Remarcação | Área para registrar a evolução física da sessão, permitindo concluir o ciclo ou pular direto para novo agendamento. |
| **Prontuário** | Histórico Individual | Visualização consolidada de todas as consultas pregressas do paciente com seus respectivos relatórios. |

---

## 5. Evidências dos Principais Fluxos Funcionando

### 5.1 Fluxo 1: Tela Principal e Agenda
* **Ação Executada:** Acesso ao endpoint raiz `/`.
* **Comportamento Observado:** Carregamento imediato da barra de navegação responsiva e da tabela contendo os agendamentos pendentes ordenados por data e horário. Caso nenhum agendamento exista, uma mensagem instrui o operador a criar o primeiro registro.

### 5.2 Fluxo 2: Operação Crítica — Atendimento com Evolução Clínica
* **Ação Executada:** Clique no botão *Atender* referente ao paciente agendado.
* **Comportamento Observado:** O sistema carrega a tela `/atender/<id>` exibindo os dados prévios do paciente. Ao preencher o campo de evolução física (ex.: *"Paciente realizou 3 séries de mobilidade de ombro; relatou redução da dor de escala 7 para 3"*) e selecionar *Finalizar Atendimento*, o status é alterado no banco para `Concluído` e o registro migra da agenda ativa para o histórico permanente.

### 5.3 Fluxo 3: Teste de Situação Inválida (Validação de Choque de Horário)
* **Ação Executada:** Cadastro intencional de um agendamento para o mesmo dia (`2026-10-15`) e horário (`08:00`) de um registro já gravado.
* **Comportamento Observado:** A rota `/salvar_agendamento` interceptou a colisão via query SQL, cancelou a transação e redirecionou o usuário com mensagem *Flash* em destaque vermelho:  
  `"Horário indisponível! Já existe um atendimento agendado para o dia 2026-10-15 às 08:00."`
* **Resultado:** O banco de dados manteve a integridade, sem registros duplicados ou travamento da aplicação.

---

## 6. Registro de Problemas Conhecidos e Limitações da Versão

1. **Concorrência Simultânea em Escala:**  
   O SQLite bloqueia o arquivo para escrita durante transações (`database is locked`). Para uma recepção com uma única máquina, opera perfeitamente; caso a entidade decida conectar múltiplos computadores simultaneamente em rede local, será recomendada a migração para PostgreSQL.
2. **Dependência de CDN Externa para Estilo:**  
   Os componentes visuais dependem do carregamento do Bootstrap 5 via link CDN. Caso o computador fique totalmente desconectado da internet no primeiro boot, os arquivos CSS/JS do Bootstrap precisam ser baixados e salvos localmente na pasta `static/`.
3. **Ausência de Autenticação por Usuário:**  
   A versão atual não exige login individual (médico vs. recepcionista), partindo do pressuposto de uso compartilhado no terminal físico da recepção da entidade.

---

## 7. Demonstração e Aceite pelo Cliente / Usuário Final

A demonstração do sistema foi realizada no terminal de atendimento da **Academia da Saúde**, com os seguintes resultados apurados em conjunto com os operadores:

* **O que foi atendido na entrega atual:**
  - Substituição integral do caderno manual de anotações da recepção.
  - Eliminação de sobreposições de horários de atendimento.
  - Prontuário digital individualizado com histórico de sessões.
  - Interface acessível, simplificada e sem necessidade de treinamento complexo.

* **O que ficou planejado para versões futuras (Backlog Evolutivo):**
  - Autenticação e perfis de acesso distintos (Recepção / Fisioterapeuta).
  - Emissão de relatórios em formato PDF com estatísticas mensais para a Secretaria Municipal de Saúde.
  - Módulo de backup automático do banco para pen drive em horários programados.

---

**Assinatura do Responsável Técnico:**  
*Gustavo Henrique Satorato — RA: 202973-25*