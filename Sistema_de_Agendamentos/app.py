from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "academia_da_saude_secret_key"

def conectar_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_banco():
    conn = conectar_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            obs TEXT
        )
    ''')
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

# 1. Rota Principal (Agenda)
@app.route('/')
def index():
    conn = conectar_db()
    agendamentos = conn.execute('''
        SELECT a.id, a.data, a.horario, a.status, a.descricao, p.nome, p.telefone 
        FROM agendamentos a 
        JOIN pacientes p ON a.paciente_id = p.id 
        ORDER BY a.data ASC, a.horario ASC
    ''').fetchall()
    conn.close()
    return render_template('index.html', agendamentos=agendamentos)

# 2. Tela e Listagem de Pacientes
@app.route('/pacientes')
def pacientes():
    conn = conectar_db()
    lista = conn.execute('SELECT * FROM pacientes ORDER BY nome ASC').fetchall()
    conn.close()
    return render_template('pacientes.html', pacientes=lista)

# 3. Salvar Paciente
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
    flash('Paciente cadastrado com sucesso!', 'success')
    return redirect(url_for('pacientes'))

# 4. Tela de Novo Agendamento
@app.route('/agendar')
def agendar():
    conn = conectar_db()
    lista_pacientes = conn.execute('SELECT id, nome FROM pacientes ORDER BY nome ASC').fetchall()
    conn.close()
    return render_template('agendar.html', pacientes=lista_pacientes)

# 5. Salvar Agendamento com Verificação de Choque
@app.route('/salvar_agendamento', methods=['POST'])
def salvar_agendamento():
    paciente_id = request.form.get('paciente_id')
    data = request.form.get('data')
    horario = request.form.get('horario')
    descricao = request.form.get('descricao', '').strip()

    if not paciente_id or not data or not horario:
        flash('Por favor, preencha todos os campos obrigatórios!', 'danger')
        return redirect(url_for('agendar'))

    conn = conectar_db()
    conflito = conn.execute(
        'SELECT id FROM agendamentos WHERE data = ? AND horario = ? AND status != "Cancelado"',
        (data, horario)
    ).fetchone()

    if conflito:
        conn.close()
        flash(f'Erro de conflito: Já existe um atendimento marcado para {data} às {horario}!', 'danger')
        return redirect(url_for('agendar'))

    conn.execute('''
        INSERT INTO agendamentos (paciente_id, data, horario, status, descricao) 
        VALUES (?, ?, ?, 'Agendado', ?)
    ''', (paciente_id, data, horario, descricao))
    conn.commit()
    conn.close()
    flash('Agendamento realizado com sucesso!', 'success')
    return redirect(url_for('index'))

# 6. Excluir Agendamento
@app.route('/excluir/<int:id>')
def excluir(id):
    conn = conectar_db()
    conn.execute('DELETE FROM agendamentos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Agendamento excluído com sucesso!', 'warning')
    return redirect(url_for('index'))

# 7. Tela de Atendimento
@app.route('/atender/<int:id>')
def atender(id):
    conn = conectar_db()
    agendamento = conn.execute('''
        SELECT a.id, a.data, a.horario, a.status, a.descricao, a.paciente_id, p.nome 
        FROM agendamentos a 
        JOIN pacientes p ON a.paciente_id = p.id 
        WHERE a.id = ?
    ''', (id,)).fetchone()
    conn.close()

    if not agendamento:
        flash('Agendamento não encontrado!', 'danger')
        return redirect(url_for('index'))

    return render_template('atendimento.html', agendamento=agendamento)

# 8. Processar Finalização / Remarcação do Atendimento
@app.route('/processar_atendimento', methods=['POST'])
def processar_atendimento():
    agendamento_id = request.form.get('agendamento_id')
    descricao = request.form.get('descricao', '').strip()
    acao = request.form.get('acao')

    conn = conectar_db()
    conn.execute('''
        UPDATE agendamentos 
        SET status = 'Finalizado', descricao = ? 
        WHERE id = ?
    ''', (descricao, agendamento_id))
    conn.commit()
    conn.close()

    if acao == 'remarcar':
        flash('Atendimento finalizado com sucesso! Agora defina a nova data e horário.', 'info')
        return redirect(url_for('agendar'))

    flash('Atendimento finalizado com sucesso!', 'success')
    return redirect(url_for('index'))

# 9. Histórico do Paciente
@app.route('/historico/<int:paciente_id>')
def historico(paciente_id):
    conn = conectar_db()
    paciente = conn.execute('SELECT * FROM pacientes WHERE id = ?', (paciente_id,)).fetchone()
    if not paciente:
        conn.close()
        flash('Paciente não encontrado!', 'danger')
        return redirect(url_for('pacientes'))

    atendimentos = conn.execute('''
        SELECT data, horario, status, descricao 
        FROM agendamentos 
        WHERE paciente_id = ? 
        ORDER BY data DESC, horario DESC
    ''', (paciente_id,)).fetchall()
    conn.close()

    return render_template('historico.html', paciente=paciente, atendimentos=atendimentos)

if __name__ == '__main__':
    inicializar_banco()
    app.run(debug=True)