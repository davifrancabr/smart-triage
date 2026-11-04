# Sistema de Triagem Médica Inteligente (Smart Triage)

Este sistema é direcionado para uso hospitalar, com objetivo de ordenar os pacientes cadastrados, dependendo da gravidade em que o paciente se encontra, para atendimento médico. Priorizando aqueles que estiverem em estado mais grave. Com assistência de Inteligência Artificial.

## Funcionalidades

- **Paciente:** Área de cadastro do paciente no sistema, contendo nome, idade e sintomas.
- **Médico:** Área acessada por médicos, para visualizar a lista de prioridade para atendimento.
- **Triagem:** Área que registra e indica a triagem dos pacientes cadastrados.
- **Integração com uma API de IA:** Recebe o cadastro dos pacientes, auxiliando na análise e classificação no grau de risco dos pacientes, gerando a Lista de Prioridade.

## Tecnologias utilizadas

- **Servidor:** Python 3.10+
- **Banco de Dados:** MySQL
- **Inteligência Artificial:** OpenAI (integração com API de IA)
- **Ferramentas:** Git, VS Code / PyCharm

### Pré-requisitos

- Python 3.9+
- Pacotes obrigatórios (listado no `requirements.txt`)

## Como Instalar e Rodar

1. Clone este repositório:

   ```bash
   git clone https://github.com/davifrancabr/smart-triage.git
   ```

2. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```
   
3. Configura todas as credenciais necessárias no `.env`
```dotenv
DB_HOST=localhost
DB_PORT=3306
DB_USER=
DB_PASSWORD=
DB_NAME=
OPENAI_API_KEY=Seu Token da OpenAI
```

4. Execute o projeto:

   ```bash
   python main.py
   ```


## Como Contribuir

Sinta-se livre para abrir uma **Issue** ou enviar um **Pull Request** contribuir com o projeto:

1. Faça o fork do projeto
2. Crie uma nova branch
3. Faça as mudanças
4. Mande um pull request com as mudanças

## Licença

Esse projeto é open source e está disponivel sob a licença do MIT.

## Integrantes:

| Nome | Matrícula |
|------|-----------|
| Davi Cavalcante França | 2671244 |
| Eduarda Rafaella Silva Melo | 2633621 |
| Tayná Santos Santana González  | 2636576 |
| lívia da Silva Teixeira de Barros | 2653161 |
| Gustavo WIlliam Dos Santos | 2639157 |

## Informações Acadêmicas

- **Instituição:** Afya - Centro Universitário de Maceió
- **Curso:** Ciência da Computação
- **Disciplina:** Estrutura de Dados
- **Professor(a):** Amaury Nogueira Neto
