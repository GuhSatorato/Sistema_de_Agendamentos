# ESTUDO-PRODUTO.md: Análise de Continuidade e Manutenção Pós-Entrega

**Produto Analisado:** Sistema de Agendamentos — Academia da Saúde  
**Autores (Dupla):** Gustavo, Eric e Allef
**Data:** 24 de Setembro de 2026  
**Repositório do Código:** `https://github.com/GuhSatorato/Sistema_de_Agendamentos`

---

## 1. Diagnóstico do Produto Real

### 1.1 Qual é o produto e qual problema ele resolve?
O produto consiste numa aplicação web local (intranet) concebida com Python (Flask), SQLite, HTML5, CSS3 (Bootstrap 5) e JavaScript. O sistema resolve o descontrolo operacional verificado na receção da **Academia da Saúde**, onde os agendamentos eram anotados manualmente em cadernos de papel sujeitos a rasuras, sobreposições de horários com o mesmo instrutor, ausência de controlo de faltas e perda do histórico evolutivo dos utentes em reabilitação física.

### 1.2 Quem usa, quem mantém e quem recebe as versões?
* **Quem usa:** Os profissionais de educação física e rececionistas da unidade da Academia da Saúde para agendar treinos, registar presenças e preencher anotações de evolução corporal.
* **Quem mantém:** A dupla de estudantes responsável pelo desenvolvimento académico. Não existe equipa técnica ou administrador de sistemas contratado pela instituição.
* **Quem recebe as versões:** O computador físico localizado na receção da entidade social.

### 1.3 Como o produto é executado hoje?
A aplicação corre localmente e de forma isolada na máquina do balcão. O servidor embutido do microframework Flask é iniciado pelo terminal ou ficheiro de lote com o comando `python app.py`, expondo a porta local `http://127.0.0.1:5000`. Todas as transações leem e escrevem num único ficheiro local de base de dados SQLite (`database.db`).

### 1.4 Quais passos ainda dependem de ação manual?
* **Arranque e Paragem:** Inicialização diária da máquina física e execução do script Python para disponibilizar a aplicação no navegador.
* **Publicação de Atualizações:** Deslocação física à unidade (ou acesso remoto avulso) para atualizar os ficheiros através de `git pull` ou pen drive, seguida de reinicialização do interpretador.
* **Alterações de Estrutura de Dados:** Execução manual de comandos SQL caso novas funcionalidades exijam adicionar colunas nas tabelas `pacientes` ou `agendamentos`.
* **Segurança e Salvaguarda:** A criação de cópias de segurança depende de um funcionário copiar periodicamente o ficheiro `database.db` para outro local.

### 1.5 O que pode dar errado em uma nova entrega?
* **Perda ou Substituição da Base de Dados:** Uma atualização descuidada da pasta do projeto pode sobrescrever o ficheiro `database.db` com um ficheiro em branco de desenvolvimento, apagando todo o histórico acumulado dos utentes.
* **Quebra por Incompatibilidade de Módulos:** A inclusão de uma biblioteca nova no código sem a devida instalação via `pip` no computador de destino fará o serviço falhar no arranque.
* **Interrupção do Atendimento (Downtime):** A ocorrência de um erro de sintaxe ou de rota no ficheiro `app.py` deixará o posto sem sistema no momento do atendimento presencial.
* **Ausência de Reversão (Rollback):** Falta de uma estratégia rápida e documentada para regressar à versão funcional imediatamente anterior perante uma falha no terreno.

### 1.6 Que evidência mostra que o produto está pronto hoje?
A prontidão e funcionamento do sistema na versão 1.0.0 encontram-se documentados através de:
1. **Registo e Listagem Funcionais:** Capacidade comprovada de registar utentes (`/pacientes`) e visualizar a grelha de marcações cronológica na página principal (`/`).
2. **Bloqueio Efetivo de Conflito de Agendas:** Implementação da consulta de validação que impede marcações duplicadas na mesma data e horário (`SELECT id FROM agendamentos WHERE data = ? AND horario = ? AND status != 'Cancelado'`), gerando alertas visuais temporários (`flash`) em vez de paragens inesperadas do servidor.
3. **Fluxo Completo de Atendimento e Histórico:** Validação do módulo `/atender/<id>`, permitindo registar o relatório de treino e optar por "Finalizar" ou "Finalizar e Remarcar", ficando o histórico do utente protegido e consultável de forma permanente na rota `/historico/<paciente_id>`.
4. **Repositório Git Consolidado:** Código estável, com rotas organizadas, templates modulares e folha de estilo padronizada.

### 1.7 Que informação precisaria ser documentada para outra pessoa manter o sistema?
* **Manual de Arranque e Dependências:** Versão requerida do interpretador Python, criação do ambiente virtual (`python -m venv venv`) e ficheiro `requirements.txt` atualizado.
* **Dicionário das Tabelas:** Esquema relacional das tabelas `pacientes` e `agendamentos` com tipos de dados, chaves primárias, estrangeiras e restrições.
* **Mapa de Rotas e Regras de Negócio:** Documentação explicativa sobre a validação de sobreposição de marcações e a bifurcação entre finalizar e remarcar atendimentos no `app.py`.
* **Procedimento de Cópia e Restauro de Segurança:** Instruções passo a passo sobre a localização do ficheiro `database.db` e procedimentos de salvaguarda antes de qualquer intervenção técnica.

---

## 2. Leitura do Futuro do Produto (Unidades 3 e 4)

---

### Ponto 1: GitHub Actions e Pipeline de Testes Automatizados (CI)
* **Qual problema ele poderia resolver:** Elimina a dependência de testes exclusivamente manuais feitos no navegador antes de enviar alterações para a branch principal (`main`).
* **Que benefício traria ao cliente ou à equipe:** Assegura à equipa que alterações nas rotas do Flask ou regras de cálculo de horário não provocam regressões silenciosas. O cliente tem a garantia de que as versões entregues superaram validações prévias de integridade.
* **Que custo, risco ou dificuldade criaria:** A equipa necessita de redigir testes automatizados com bibliotecas como o `pytest` e estruturar o ficheiro de workflow em formato YAML. Há o risco de bloquear publicações urgentes com avisos irrelevantes de formatação caso a configuração seja desnecessariamente restritiva.
* **Que informação ainda faltaria investigar:** Como configurar uma fixture de teste no Flask (`test_client`) que simule requisições `POST` isoladas sem interferir com uma base de dados persistente.

---

### Ponto 2: Ambiente Reproduzível com Contentores (Docker)
* **Qual problema ele poderia resolver:** Anula o risco de discrepâncias entre o ambiente de desenvolvimento e o ambiente do computador da receção (versão desatualizada do Python, ausência de compiladores C ou limitações de permissões no Windows).
* **Que benefício traria ao cliente ou à equipe:** Torna a distribuição independente do estado do sistema operativo hospedeiro. Toda a pilha (interpretador, dependências, servidor WSGI e código) é executada a partir de uma imagem isolada e imutável.
* **Que custo, risco ou dificuldade criaria:** Exige a instalação e suporte do Docker Desktop num computador que pode dispor de recursos de hardware modestos (processador ou memória RAM limitados). Além disso, a gestão de *Volumes* exige atenção redobrada para que os dados do SQLite não sejam eliminados ao reiniciar o contentor.
* **Que informação ainda faltaria investigar:** A arquitetura de hardware, quantidade de memória RAM disponível e versão do sistema operativo (Windows de 32 ou 64 bits) do computador do balcão da Academia da Saúde.

---

### Ponto 3: Monitorização Operacional e Rotina Automatizada de Cópia de Segurança
* **Qual problema ele poderia resolver:** Evita a perda catastrófica e irreversível de dados clínicos e cadastrais perante uma falha física de hardware, infeção por malware ou eliminação inadvertida da pasta da aplicação.
* **Que benefício traria ao cliente ou à equipe:** Tranquilidade e continuidade de serviço. O sistema passa a registar ocorrências de erro num ficheiro de log acessível e salvaguarda cópias diárias do ficheiro `database.db` em diretórios protegidos.
* **Que custo, risco ou dificuldade criaria:** Praticamente sem impacto orçamental; contudo, introduz a complexidade de configurar tarefas agendadas no sistema operativo (Agendador de Tarefas do Windows) e gerir a rotação de ficheiros para não esgotar o espaço em disco com cópias obsoletas.
* **Que informação ainda faltaria investigar:** Determinar se o computador da instituição possui acesso estável a pastas partilhadas, suporte para pen drives dedicadas ou autorização institucional para sincronização cifrada com um serviço de nuvem pública.

---

## 3. Síntese de Sustentação

O produto cumpre na totalidade o objetivo de informatizar e mitigar as falhas analógicas da Academia da Saúde sem acarretar custos operacionais diretos. 

Para assegurar a sua longevidade após o término da avaliação académica, a aplicação deve transitar de um modelo de manutenção empírico para uma rotina estruturada assente em três eixos: validação automática de código prévia à entrega, isolamento da execução e garantia sistemática de salvaguarda dos registos clínicos dos utentes.