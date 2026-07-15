# API Moderna como Produto de Dados

API REST para gerenciamento de regras de qualidade de dados, construída com FastAPI, SQLAlchemy e injeção de dependências via `dependency-injector`.

## Visão geral

A API permite criar, consultar, atualizar, ativar e desativar regras de qualidade associadas a tabelas e colunas de um banco de dados. Cada regra pertence a um dos quatro tipos suportados:

| Tipo | Descrição | Parâmetros obrigatórios |
|---|---|---|
| `unicity` | Garante unicidade dos valores | — |
| `completeness` | Garante ausência de nulos | — |
| `precision` | Valida intervalo numérico ou lista de valores aceitos | `min_value` + `max_value` **ou** `enum_value` |
| `validity` | Valida formato via expressão regular | `regex_expr` |

## Estrutura do projeto

```
.
├── db/
│   └── init_db.py          # Inicialização do banco SQLite
├── source/
│   ├── app.py              # Entrada FastAPI + wiring do container
│   ├── config/
│   │   └── containers.py   # Container raiz (dependency-injector)
│   ├── controller/
│   │   └── v1/
│   │       └── quality_controller.py
│   ├── exceptions/
│   │   ├── quality_rule_exceptions.py
│   │   └── repo_exceptions.py
│   ├── gateway/
│   │   └── sqlite_client.py
│   ├── model/
│   │   └── quality_rule_model.py
│   ├── repository/
│   │   └── sqlite_quality_rule_repository.py
│   ├── schema/
│   │   ├── quality_rule_schema.py
│   │   └── response_schema.py
│   └── service/
│       └── quality_rule_service.py
└── test/
    ├── scenario/
    │   └── quality_rule.feature  # Cenários Gherkin (Give-When-Then)
    └── unit/
        ├── test_sqlite_client.py
        ├── test_quality_rule_repository.py
        ├── test_quality_rule_schema.py
        ├── test_quality_rule_service.py
        └── test_quality_controller.py
```

## Pré-requisitos

- Python 3.14+
- [Poetry](https://python-poetry.org/)

## Instalação

```bash
poetry install
```

## Uso

### Subir a API

```bash
make up
```

Isso inicializa o banco SQLite em `db/database.db` e sobe o servidor em `http://localhost:8000`.  
A documentação interativa fica disponível em `http://localhost:8000/docs`.

### Rodar os testes

```bash
make test
```

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/v1/rule/` | Cria uma nova regra de qualidade |
| `GET` | `/api/v1/rule/{rule_id}` | Busca regra pelo ID |
| `GET` | `/api/v1/rule/table/{target_table}` | Lista regras de uma tabela (filtro opcional por `is_active`) |
| `PUT` | `/api/v1/rule/{rule_id}` | Atualiza uma regra ativa |
| `PATCH` | `/api/v1/rule/{rule_id}` | Ativa (`is_active=true`) ou desativa (`is_active=false`) uma regra |

### Exemplos

**Criar regra de unicidade**
```bash
curl -X POST http://localhost:8000/api/v1/rule/ \
  -H "Content-Type: application/json" \
  -d '{"rule_type": "unicity", "target_table": "vendas", "target_column": "id_pedido"}'
```

**Criar regra de precisão com intervalo**
```bash
curl -X POST http://localhost:8000/api/v1/rule/ \
  -H "Content-Type: application/json" \
  -d '{"rule_type": "precision", "target_table": "produtos", "target_column": "preco", "min_value": 0.01, "max_value": 9999.99}'
```

**Criar regra de validade com regex**
```bash
curl -X POST http://localhost:8000/api/v1/rule/ \
  -H "Content-Type: application/json" \
  -d '{"rule_type": "validity", "target_table": "clientes", "target_column": "cpf", "regex_expr": "^\\d{3}\\.\\d{3}\\.\\d{3}-\\d{2}$"}'
```

**Desativar uma regra**
```bash
curl -X PATCH "http://localhost:8000/api/v1/rule/1?is_active=false"
```
