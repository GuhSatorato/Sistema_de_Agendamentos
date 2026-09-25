# Discovery DevOps: Análise, Pesquisa e Planejamento de Modernização

**Estudante:** Gustavo Henrique Satorato  
**RA:** 202973-25  
**Produto Analisado:** Plataforma Web de Gestão e Agendamento ("Sistema AgendaFácil") — Unidade Academia da Saúde  
**Data:** 24 de Setembro de 2026  

---

## Parte 1 · Estado Atual

### 1.1 Arquitetura e Tecnologias Utilizadas
O produto analisado é o **Sistema AgendaFácil**, uma aplicação web monolítica orientada à gestão de fluxo e agendamento de atendimentos de reabilitação e condicionamento físico para a Organização Social (OS) **Academia da Saúde**. A arquitetura técnica estrutura-se em:
* **Frontend:** Páginas renderizadas no lado do servidor (SSR) via mecanismo de templates Jinja2. A marcação semântica utiliza HTML5 estruturado em formulários e tabelas dinâmicas, estilizado com CSS3 e o framework Bootstrap 5 (integrado via CDN para assegurar responsividade em monitores e tablets). Scripts leves em JavaScript puro (Vanilla JS) executam validações de formulário no cliente, confirmações modais de segurança (como diálogo antes de exclusão de registros) e máscaras para formatação de campos textuais (telefone e datas).
* **Backend:** Desenvolvido em linguagem Python (versão 3.10+), utilizando o microframework web Flask. O backend centraliza o roteamento HTTP, processamento de formulários (`POST` e `GET`), controle de fluxo de sessões/mensagens de alerta (*Flash Messages*) e a camada de regras de negócio, destacando-se a validação algorítmica de conflitos de agenda (impedindo que dois atendimentos sobreponham-se no mesmo intervalo de data e hora).
* **Banco de Dados:** Utiliza o SQLite3 como Sistema Gerenciador de Banco de Dados Relacional embarcado, operando sobre um arquivo local persistente denominado `database.db`. A modelagem é normalizada em tabelas relacionais (`pacientes` e `agendamentos`) interligadas por chaves estrangeiras (`paciente_id`), processadas nativamente por instruções SQL parametrizadas para evitar ataques de SQL Injection.
* **Comunicação e Protocolo:** Comunicação estritamente síncrona via HTTP/1.1 em rede local/intranet, trafegando cargas de dados encapsuladas em `application/x-www-form-urlencoded` a partir de submissões padrão de formulários web.

### 1.2 Forma Atual de Executar e Publicar
* **Execução em Desenvolvimento:** Cada membro da equipe executa a aplicação localmente disparando o interpretador via terminal CLI com o comando `python app.py`. O ambiente exige a instalação manual prévia do interpretador Python no sistema operacional e das bibliotecas externas através de comandos avulsos do gerenciador `pip` (geralmente sem um isolamento padronizado de ambiente virtual `venv`). A aplicação roda no servidor HTTP interno do Flask, escutando no endereço de loopback `http://127.0.0.1:5000` com a diretiva `debug=True` ativada.
* **Publicação / Implantação:** O processo atual é integralmente manual, físico e descentralizado. A publicação no ambiente operacional da recepção da Academia da Saúde envolve transferir a árvore de diretórios do projeto manualmente (via pendrive ou clone pontual de repositório Git), instalar a runtime do Python na estação física da OS, criar um atalho de inicialização em lote (`.bat`) na Área de Trabalho do Windows e executar a aplicação em segundo plano. Não existe servidor de aplicação WSGI de grau de produção (como Waitress ou Gunicorn), nem proxy reverso (Nginx) ou provisionamento em nuvem.

### 1.3 Como a Equipe Testa
* A estratégia de testes baseia-se unicamente em **testes manuais exploratórios** de caixa preta executados diretamente no navegador web.
* O fluxo de verificação típico consiste em: iniciar o servidor localmente, abrir a rota raiz no navegador, preencher manualmente o formulário de cadastro de paciente, abrir o formulário de agendamento e tentar cadastrar um horário duplicado de propósito para atestar visualmente se o aviso de erro é exibido.
* Não há testes de unidade automatizados (utilizando frameworks como `unittest` ou `pytest`), testes de integração de rotas com clientes de teste do Flask (`test_client`) ou verificações de regressão visual. Caso uma alteração no código quebre uma rota legada, o defeito só é descoberto caso o desenvolvedor navegue manualmente até aquela página.

### 1.4 Como as Alterações são Registradas
* O versionamento do código é realizado por meio do Git com repositório remoto centralizado no GitHub.
* O fluxo de trabalho adota um padrão linear básico: os desenvolvedores comitam diretamente na branch `main` ou geram branches temporárias sem políticas de proteção (*Branch Protection Rules*). O repositório não exige revisões de código formais (*Pull Requests* obrigatórios com revisão por pares) para a integração de código.
* Foi implementado um arquivo `.gitignore` básico para barrar o envio de artefatos de compilação em cache (`__pycache__/`, `*.pyc`) e pastas de ambientes virtuais (`venv/`). Contudo, mensagens de commit com frequência são sucintas e despadronizadas, sem rastreabilidade direta com problemas catalogados (*issues*).

### 1.5 Riscos na Manutenção e na Entrega
* **Dependência do Ambiente Físico de Destino (Config Drift):** A máquina da recepção da Academia da Saúde pode sofrer variações de versão do sistema operacional Windows, atualizações de segurança ou remoção acidental de dependências do Python por usuários leigos, impedindo a inicialização do sistema.
* **Corrupção e Perda Catastrófica de Dados:** Sendo o SQLite um arquivo local único gravado em disco mecânico ou SSD da máquina cliente, qualquer falha no sistema de arquivos, desligamento abrupto de energia durante escrita ou ataque por malware resultará na perda irreversível do histórico clínico e de agendamentos dos cidadãos, visto que não há rotina programada de backup.
* **Vulnerabilidades e Instabilidade por Debug Server:** Manter `debug=True` em um ambiente acessível na rede local abre brechas de segurança graves (como a execução arbitrária de código via debugger interativo do Werkzeug no navegador) e instabilidade de concorrência, já que o servidor interno do Flask não foi concebido para requisições paralelas simultâneas.
* **Risco Elevado de Regressão Silenciosa:** Devido à ausência de testes automatizados executados na integração de código, melhorias em rotas (como novas opções no módulo de atendimento) podem romper rotas existentes de listagem ou de exclusão sem detecção prévia.

---

## Parte 2 · Pesquisa

Para investigar a modernização do ciclo de vida e a estabilidade do Sistema AgendaFácil, foram selecionadas quatro áreas técnicas fundamentadas nas Unidades 3 e 4:

### Possibilidade 1: Versionamento Estruturado e Workflow (GitHub Flow com Branch Protection)
* **O que é:** Prática de engenharia de software que define um conjunto de regras estritas para ramificação, integração e liberação de código no Git. Estabelece a branch principal (`main`) como permanentemente estável e bloqueada para escrita direta, canalizando todo o desenvolvimento para branches de funcionalidade (*feature branches*) integradas exclusivamente por meio de *Pull Requests* (PRs) com revisão obrigatória.
* **Qual problema resolve:** Resolve a sobreposição desordenada de código, conflitos de mesclagem acidentais entre membros da equipe e o risco de subir código inacabado ou com erros graves diretamente para a versão operacional de entrega.
* **Como poderia ajudar este produto:** Como o grupo divide o desenvolvimento entre módulos distintos (frontend em HTML/JS, regras de negócio no Flask e modelagem no SQLite), o GitHub Flow garante que uma funcionalidade (ex.: `feature/historico-paciente`) só seja fundida à `main` após ser inspecionada por outro colega, preservando uma linha de código historicamente auditável e sempre funcional.
* **Qual custo, risco ou dependência cria:** Custo financeiro nulo (recurso nativo e gratuito do GitHub). Cria um custo temporal de disciplina operacional, podendo desacelerar entregas imediatas pontuais caso a equipe demore para revisar e aprovar os Pull Requests pendentes.
* **Qual pré-requisito precisa ser investigado:** É necessário que todos os integrantes dominem comandos básicos de ramificação no Git (`git checkout -b`, `git pull`, abertura de PRs) e que as configurações de governança do repositório no GitHub sejam ativadas com travas de proteção de branch.

### Possibilidade 2: Containers (Docker e Dockerfile)
* **O que é:** Tecnologia de virtualização a nível de sistema operacional que empacota o código da aplicação, interpretador, bibliotecas declaradas, variáveis e arquivos estáticos dentro de uma unidade de software isolada, padronizada e imutável chamada container.
* **Qual problema resolve:** Elimina de forma definitiva o problema de incompatibilidade de ambiente e discrepâncias de sistema operacional ("na máquina do desenvolvedor funciona, no computador do posto não roda").
* **Como poderia ajudar este produto:** O Sistema AgendaFácil pode ser encapsulado em uma imagem Docker baseada em Python Alpine (leve e segura), executando sobre um servidor WSGI leve (como Waitress ou Gunicorn). No computador da recepção da Academia da Saúde, a aplicação pode ser iniciada com um único comando ou arquivo de composição, montando o arquivo `database.db` em um volume persistente fora do container para garantir a segurança dos dados.
* **Qual custo, risco ou dependência cria:** Exige a instalação do Docker Desktop ou Docker Engine no computador da recepção da OS, o que impõe um custo significativo de consumo de memória RAM e processamento em máquinas de baixo desempenho. Cria o risco de perda de dados caso a equipe configure incorretamente o mapeamento de volumes persistentes do SQLite.
* **Qual pré-requisito precisa ser investigado:** Verificar se o hardware da máquina física da Academia da Saúde possui suporte à virtualização ativado na BIOS/UEFI e capacidade mínima de memória RAM (ao menos 4 GB livres) para suportar o subsistema de containers.

### Possibilidade 3: GitHub Actions e Pipelines de CI (Integração Contínua)
* **O que é:** Plataforma de automação orientada a eventos integrada ao ecossistema GitHub, permitindo criar fluxos de trabalho (*workflows*) declarados em arquivos estruturados YAML para orquestrar etapas de compilação, análise estática de código e execução de suítes de testes.
* **Qual problema resolve:** Elimina a verificação manual passível de erro humano, impedindo que falhas sintáticas, violações de estilo de código ou regressões lógicas sejam mescladas ao projeto sem aviso prévio.
* **Como poderia ajudar este produto:** A cada `push` ou abertura de `Pull Request`, o GitHub Actions provisiona automaticamente um ambiente virtual efêmero (Ubuntu Runner), instala as dependências declaradas em `requirements.txt`, executa um linter de código (`flake8`) para validar a conformidade da sintaxe Python e roda testes automatizados com `pytest` simulando o comportamento das rotas web do Flask (garantindo que cadastros e a trava de choque de horários estejam funcionando antes do merge).
* **Qual custo, risco ou dependência cria:** Dependência de conectividade de rede com a infraestrutura do GitHub e consumo de franquia de minutos de execução (gratuita para repositórios públicos, porém limitada para repositórios privados). Cria a obrigação técnica de a equipe escrever e manter testes unitários em sincronia com o crescimento do código.
* **Qual pré-requisito precisa ser investigado:** Estruturar previamente um arquivo `requirements.txt` sem conflitos de versão e implementar uma suíte mínima de testes funcionais em Python que possam ser invocados por linha de comando sem interação gráfica.

### Possibilidade 4: Monitoramento e Documentação Operacional (Rotinas de Resiliência e Backup do SQLite)
* **O que é:** Conjunto integrado de processos, scripts operacionais e documentações técnicas (como Manuais de Procedimento Operacional / Runbooks) voltados a monitorar a saúde da aplicação em execução, registrar logs estruturados de eventos e executar rotinas preventivas de tolerância a falhas.
* **Qual problema resolve:** Resolve a cegueira técnica e a vulnerabilidade da operação local, onde falhas críticas e corrupções silenciosas no banco de dados só são percebidas após o dano estar consolidado e o atendimento presencial paralisado.
* **Como poderia ajudar este produto:** Implementação do módulo nativo `logging` do Python para gravar arquivos de log com rotação diária (registrando erros HTTP 500 e exceções de banco), associado a um script em lote agendado no sistema operacional (Agendador de Tarefas do Windows) que execute diariamente cópias de backup a quente do arquivo `database.db` utilizando a API nativa de backup do SQLite, exportando o arquivo para um diretório protegido ou armazenamento removível seguro.
* **Qual custo, risco ou dependência cria:** Custo financeiro inexistente; cria uma dependência de intervenção humana disciplinada para checar periodicamente a integridade das cópias de backup e o preenchimento de espaço em disco pelo acúmulo de arquivos de log.
* **Qual pré-requisito precisa ser investigado:** Identificar o sistema operacional exato da recepção da Academia da Saúde, os privilégios de usuário concedidos à conta local da máquina e a disponibilidade de uma unidade de disco secundária para alocação dos backups.

---

## Parte 3 · Comparação e Decisão

### 3.1 Comparação de Alternativas
Para solucionar o gargalo de **Garantia de Qualidade, Estabilidade e Redução de Falhas na Entrega de Código**, foram comparadas duas alternativas de trabalho:

| Critério | Alternativa A: Workflow Manual (Commit direto na Main sem CI) | Alternativa B: GitHub Flow com Pipeline de CI (GitHub Actions) |
| :--- | :--- | :--- |
| **Tempo de Verificação** | Indeterminado; depende da iniciativa de cada estudante testar rotas no navegador. | 60 a 120 segundos, acionado automaticamente a cada alteração submetida. |
| **Risco Operacional** | Altíssimo; erros de sintaxe ou quebras de regras de agendamento vão direto para a branch de release. | Extremamente baixo; o repositório barra automaticamente a fusão de códigos com falha técnica. |
| **Esforço Inicial** | Zero; método empírico informal adotado no início do desenvolvimento. | Baixo a Médio; escrita de arquivo de manifesto YAML e testes estruturados em `pytest`. |
| **Rastreabilidade e Governança** | Nula; histórico de commits fragmentado, sem histórico de aprovação ou registros de testes. | Total; histórico auditável no GitHub com carimbos visuais de status (*checks* verdes) e autores de revisão. |
| **Impacto na OS (Academia da Saúde)** | Alto risco de interrupção do atendimento presencial por falhas em horários de pico. | Entrega de versões previamente validadas, aumentando a confiabilidade dos atendimentos. |

### 3.2 Decisão e Justificativa
* **Decisão Escolhida:** Adotar a **Alternativa B (GitHub Flow com Pipeline de CI via GitHub Actions)** integrada a testes básicos em Python.
* **Justificativa Detalhada:**
  * **Valor para o Cliente:** A Academia da Saúde atende cidadãos em situação de reabilitação física e necessita de um sistema que opere sem travamentos durante o expediente da recepção. Uma entrega defeituosa paralisaria a fila presencial. O CI atua como uma barreira protetora que impede que bugs cheguem ao ambiente físico.
  * **Momento do Produto:** O produto superou a fase de protótipo visual e está incorporando regras de negócio sensíveis (atendimento, conclusão, cancelamento e histórico médico). Alterar o código nessas fases sem um validador automático geraria regressões frequentes entre os membros da equipe.
  * **Equipe e Esforço:** A equipe é enxuta e composta por alunos em formação técnica. O esforço para implementar uma pipeline de CI básica em Python/Flask é mínimo (cerca de 35 linhas de YAML) e utiliza infraestrutura 100% gratuita do GitHub, gerando ganhos substanciais de maturidade profissional e confiabilidade com custo financeiro zero.

---

## Parte 4 · Plano de Adoção

O plano de evolução DevOps foi estruturado em três horizontes cronológicos bem delimitados:

```
[ AGORA ]
  ├── Congelamento de Dependências (requirements.txt)
  ├── Proteção de Branch (GitHub Flow)
  └── Esteira Básica de CI (Linter + Pytest no GitHub Actions)
       │
[ DEPOIS ]
  ├── Servidor WSGI para Produção Local (Waitress)
  ├── Rotina Automatizada de Backup do SQLite
  └── Centralização de Logs da Aplicação
       │
[ MAIS ADIANTE ]
  ├── Empacotamento em Container Docker Leve
  └── Migração para Cloud/PaaS Gratuita com PostgreSQL
```

| Momento | Ação | Responsável | Pré-requisito | Evidência de Conclusão | Risco Identificado |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Agora** | Congelar dependências em `requirements.txt`, ativar proteção de branch na `main` e adotar GitHub Flow com PRs obrigatórios. | Gustavo Henrique Satorato (Líder Técnico) | Git e Python instalados nas estações da equipe; privilégios de admin no GitHub. | Arquivo `requirements.txt` versionado; branch `main` rejeitando commits diretos sem PR. | Resistência de membros da equipe em seguir o fluxo de PRs em vez de comitar direto na main. |
| **Agora** | Construir pipeline de CI no GitHub Actions validando sintaxe com `flake8` e executando testes de rotas com `pytest`. | Gustavo Henrique Satorato | Repositório hospedado no GitHub; scripts de teste criados na pasta `/tests`. | Workflow `.github/workflows/ci.yml` funcional com status de aprovação verde nos PRs. | Falhas no pipeline por divergências de sistema operacional entre o runner Linux e máquinas Windows. |
| **Depois** | Substituir o servidor de desenvolvimento por um servidor WSGI (Waitress) e configurar script `.bat` de inicialização segura. | Integrante responsável por Backend | Pacote `waitress` instalado e documentado nas dependências. | Aplicação iniciando sem exibir o alerta de segurança do Flask Development Server. | Dificuldade em gerenciar encerramentos inesperados do processo sem interface visível. |
| **Depois** | Criar script automatizado agendado para backup diário a quente do `database.db` e documentar o Runbook de restauração. | Integrante responsável por Banco de Dados | Acesso à máquina da recepção; definição de pasta destino de segurança. | Arquivo de script gerando cópias datadas com sucesso; manual de restauração redigido. | Esgotamento do espaço em disco caso a rotina de expurgo de backups antigos não funcione. |
| **Mais Adiante** | Conteinerizar a aplicação com Docker e avaliar migração para nuvem (ex.: Render ou VPS) com PostgreSQL. | Toda a equipe | Conexão de internet de alta disponibilidade na OS e eventual autorização orçamentária. | Arquivo `Dockerfile` funcional no repositório ou URL pública segura (HTTPS) ativa. | Custos financeiros recorrentes que a instituição pública/social não tenha como custear. |

---

## Parte 5 · Uso da IA

### 5.1 Registro de Perguntas Feitas
Durante o processo de discovery e levantamento arquitetural, foram submetidas as seguintes questões para ferramentas de Inteligência Artificial:
1. *"Como estruturar uma pipeline de CI/CD completa e moderna para uma aplicação web Python Flask com banco SQLite que será instalada localmente no computador de uma instituição social pública?"*
2. *"Qual a melhor estratégia para garantir a integridade dos dados e alta disponibilidade de um sistema web interno operando com SQLite em uma máquina de recepção sem conexão contínua de internet?"*

### 5.2 Comparação de Respostas e Fontes
* **Resposta da IA A (Orientação Corporativa / Cloud-Native):** Propôs a migração compulsória de toda a arquitetura para a nuvem da Amazon Web Services (AWS), orquestrada via Kubernetes (EKS), com provisionamento de infraestrutura declarativa através de scripts em Terraform/OpenTofu, banco de dados gerenciado em nuvem (AWS RDS PostgreSQL Multi-AZ) e pipeline de esteira com AWS CodePipeline. Argumentou que apenas a nuvem garante resiliência e padrões corporativos aceitáveis de DevOps.
* **Resposta da IA B / Fóruns Especializados e Documentação Oficial (Abordagem Pragmática):** Confrontando a documentação oficial do Flask, a documentação da API de Backup do SQLite e discussões em comunidades técnicas, a abordagem alternativa sugeriu que forçar uma arquitetura em nuvem distribuída violaria a premissa central de funcionamento offline da instituição. A recomendação pragmática foi focar na integração contínua (CI via GitHub Actions) para validação do código em desenvolvimento e fortalecer a operação local do SQLite através de um servidor WSGI (Waitress no Windows) acompanhado de scripts automatizados de cópia de sombra (*hot backup*) do banco.

### 5.3 Análise Crítica: Sugestão Verificada e Rejeitada
* **Sugestão Rejeitada:** A recomendação da IA A de adotar **Kubernetes gerenciado em nuvem (AWS EKS) provisionado com Terraform e banco RDS**.
* **Motivo da Rejeição:** A sugestão foi criticamente avaliada e sumariamente descartada por constituir um caso severo de *overengineering* (complexidade desproporcional) e incoerência com a realidade social da Academia da Saúde:
  1. **Inviabilidade Financeira:** Serviços gerenciados como AWS EKS e RDS possuem custos mensais faturados em moeda estrangeira (dólar), incompatíveis com o orçamento de uma entidade social pública que fornece atendimento gratuito.
  2. **Dependência Crítica de Conectividade:** A recepção da unidade física enfrenta instabilidades e eventuais quedas no sinal de internet. Uma arquitetura em nuvem impediria a recepção de consultar ou registrar atendimentos no momento em que os pacientes estivessem presentes, paralisando as atividades essenciais.  
  Portanto, manteve-se a decisão técnica fundamentada: **uma arquitetura local simples, robusta e independente de internet externa, modernizada pelas práticas corretas de DevOps cabíveis ao estágio do produto — automação de testes com CI via GitHub Actions, governança de código e resiliência de dados através de rotinas programadas de backup**.

---

## Referências
1. FLASK DOCUMENTATION. *Deploying to Production (WSGI Servers)*. Pallets Projects. Disponível em: <https://flask.palletsprojects.com/en/latest/deploying/>. Acesso em: 2026.
2. GITHUB DOCS. *Building and Testing Python with GitHub Actions*. Disponível em: <https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python>. Acesso em: 2026.
3. HUMBLE, J.; FARLEY, D. *Entrega Contínua: Como Fazer o Desdobramento de Software Confiável por meio de Automação de Compilação, Teste e Implantação*. Porto Alegre: Bookman, 2014.
4. KIM, G.; HUMBLE, J.; DEBOIS, P.; WILLIS, J. *Manual de DevOps: Como Obter Agilidade, Confiabilidade e Segurança em Nível Mundial em Organizações de Tecnologia*. São Paulo: Alta Books, 2018.
5. SQLITE DOCUMENTATION. *SQLite Online Backup API*. SQLite Consortium. Disponível em: <https://www.sqlite.org/backup.html>. Acesso em: 2026.
6. WAITRESS DOCUMENTATION. *Waitress: A production-quality pure-Python WSGI server*. Pylons Project. Disponível em: <https://docs.pylonsproject.org/projects/waitress/>. Acesso em: 2026.