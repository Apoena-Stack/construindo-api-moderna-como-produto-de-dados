# language: pt

Funcionalidade: Gerenciar regras de qualidade de dados
    Como usuário da API de qualidade de dados,
    Quero criar, consultar, atualizar e ativar/desativar regras de qualidade,
    Para garantir a integridade dos dados nas tabelas monitoradas.

# ─────────────────────────────────────────
# POST /rule/  –  Criar regra de qualidade
# ─────────────────────────────────────────

    Cenario: Criar regra de unicidade com sucesso
        Dado que não existe nenhuma regra do tipo "unicity" para a tabela "vendas" na coluna "id_pedido"
        Quando uma requisição POST é enviada para "/rule/" com os campos:
            | rule_type | target_table | target_column |
            | unicity   | vendas       | id_pedido     |
        Entao a API retorna o status HTTP 201
        E o corpo da resposta contém a regra criada com "rule_type" igual a "unicity"
        E o campo "is_active" da regra retornada é verdadeiro

    Cenario: Criar regra de completude com sucesso
        Dado que não existe nenhuma regra do tipo "completeness" para a tabela "clientes" na coluna "email"
        Quando uma requisição POST é enviada para "/rule/" com os campos:
            | rule_type    | target_table | target_column |
            | completeness | clientes     | email         |
        Entao a API retorna o status HTTP 201
        E o corpo da resposta contém a regra criada com "rule_type" igual a "completeness"

    Cenario: Criar regra de precisão com intervalo numérico
        Dado que não existe nenhuma regra do tipo "precision" para a tabela "produtos" na coluna "preco"
        Quando uma requisição POST é enviada para "/rule/" com os campos:
            | rule_type | target_table | target_column | min_value | max_value |
            | precision | produtos     | preco         | 0.01      | 9999.99   |
        Entao a API retorna o status HTTP 201
        E o corpo da resposta contém os campos "min_value" igual a 0.01 e "max_value" igual a 9999.99

    Cenario: Criar regra de precisão com lista de valores permitidos
        Dado que não existe nenhuma regra do tipo "precision" para a tabela "pedidos" na coluna "status"
        Quando uma requisição POST é enviada para "/rule/" com os campos:
            | rule_type | target_table | target_column | enum_value                        |
            | precision | pedidos      | status        | ["pendente","pago","cancelado"]   |
        Entao a API retorna o status HTTP 201
        E o corpo da resposta contém o campo "enum_value" com os valores informados

    Cenario: Criar regra de validade com expressão regular
        Dado que não existe nenhuma regra do tipo "validity" para a tabela "clientes" na coluna "cpf"
        Quando uma requisição POST é enviada para "/rule/" com os campos:
            | rule_type | target_table | target_column | regex_expr              |
            | validity  | clientes     | cpf           | ^\d{3}\.\d{3}\.\d{3}-\d{2}$ |
        Entao a API retorna o status HTTP 201
        E o corpo da resposta contém o campo "regex_expr" com a expressão informada

    Cenario: Tentar criar regra duplicada
        Dado que já existe uma regra do tipo "unicity" para a tabela "vendas" na coluna "id_pedido"
        Quando uma requisição POST é enviada para "/rule/" com os mesmos dados da regra existente
        Entao a API retorna o status HTTP 409

    Cenario: Tentar criar regra de unicidade com parâmetros extras não permitidos
        Dado que o tipo de regra "unicity" não aceita parâmetros adicionais
        Quando uma requisição POST é enviada para "/rule/" com os campos:
            | rule_type | target_table | target_column | min_value |
            | unicity   | vendas       | id_pedido     | 10.0      |
        Entao a API retorna o status HTTP 422

    Cenario: Tentar criar regra de precisão sem os parâmetros obrigatórios
        Dado que o tipo de regra "precision" requer "min_value" e "max_value" juntos, ou apenas "enum_value"
        Quando uma requisição POST é enviada para "/rule/" com os campos:
            | rule_type | target_table | target_column | min_value |
            | precision | produtos     | preco         | 10.0      |
        Entao a API retorna o status HTTP 422

    Cenario: Tentar criar regra de validade sem expressão regular
        Dado que o tipo de regra "validity" exige o parâmetro "regex_expr"
        Quando uma requisição POST é enviada para "/rule/" com os campos:
            | rule_type | target_table | target_column |
            | validity  | clientes     | cpf           |
        Entao a API retorna o status HTTP 422

    Cenario: Tentar criar regra de validade com expressão regular inválida
        Dado que o tipo de regra "validity" valida a expressão regular fornecida
        Quando uma requisição POST é enviada para "/rule/" com os campos:
            | rule_type | target_table | target_column | regex_expr |
            | validity  | clientes     | cpf           | [abc       |
        Entao a API retorna o status HTTP 422

# ─────────────────────────────────────────
# GET /rule/{rule_id}  –  Buscar por ID
# ─────────────────────────────────────────

    Cenario: Buscar regra existente pelo ID
        Dado que existe uma regra de qualidade com id 1
        Quando uma requisição GET é enviada para "/rule/1"
        Entao a API retorna o status HTTP 200
        E o corpo da resposta contém a regra com "id" igual a 1

    Cenario: Buscar regra inexistente pelo ID
        Dado que não existe nenhuma regra de qualidade com id 9999
        Quando uma requisição GET é enviada para "/rule/9999"
        Entao a API retorna o status HTTP 404

# ─────────────────────────────────────────────────────────
# GET /rule/table/{target_table}  –  Buscar por tabela
# ─────────────────────────────────────────────────────────

    Cenario: Buscar regras ativas de uma tabela
        Dado que existem regras de qualidade cadastradas para a tabela "vendas", algumas ativas e outras inativas
        Quando uma requisição GET é enviada para "/rule/table/vendas?is_active=true"
        Entao a API retorna o status HTTP 200
        E o corpo da resposta é uma lista contendo apenas regras com "is_active" igual a verdadeiro

    Cenario: Buscar regras inativas de uma tabela
        Dado que existem regras de qualidade inativas cadastradas para a tabela "vendas"
        Quando uma requisição GET é enviada para "/rule/table/vendas?is_active=false"
        Entao a API retorna o status HTTP 200
        E o corpo da resposta é uma lista contendo apenas regras com "is_active" igual a falso

    Cenario: Buscar todas as regras de uma tabela sem filtro de status
        Dado que existem regras de qualidade cadastradas para a tabela "vendas"
        Quando uma requisição GET é enviada para "/rule/table/vendas"
        Entao a API retorna o status HTTP 200
        E o corpo da resposta é uma lista com todas as regras da tabela independente do status

    Cenario: Buscar regras de uma tabela sem nenhuma regra cadastrada
        Dado que não existem regras de qualidade cadastradas para a tabela "historico_acesso"
        Quando uma requisição GET é enviada para "/rule/table/historico_acesso"
        Entao a API retorna o status HTTP 200
        E o corpo da resposta é uma lista vazia

# ─────────────────────────────────────────
# PUT /rule/{rule_id}  –  Atualizar regra
# ─────────────────────────────────────────

    Cenario: Atualizar regra ativa com sucesso
        Dado que existe uma regra ativa com id 1
        Quando uma requisição PUT é enviada para "/rule/1" com novos dados válidos
        Entao a API retorna o status HTTP 201
        E o corpo da resposta reflete os dados atualizados

    Cenario: Tentar atualizar regra inexistente
        Dado que não existe nenhuma regra de qualidade com id 9999
        Quando uma requisição PUT é enviada para "/rule/9999" com dados válidos
        Entao a API retorna o status HTTP 404

    Cenario: Tentar atualizar regra inativa
        Dado que existe uma regra inativa com id 2
        Quando uma requisição PUT é enviada para "/rule/2" com novos dados válidos
        Entao a API retorna o status HTTP 409

# ───────────────────────────────────────────────────────────────────
# PATCH /rule/{rule_id}  –  Ativar ou desativar regra
# ───────────────────────────────────────────────────────────────────

    Cenario: Desativar regra ativa com sucesso
        Dado que existe uma regra ativa com id 1
        Quando uma requisição PATCH é enviada para "/rule/1?is_active=false"
        Entao a API retorna o status HTTP 200
        E o campo "is_active" da regra retornada é falso

    Cenario: Ativar regra inativa com sucesso
        Dado que existe uma regra inativa com id 2
        Quando uma requisição PATCH é enviada para "/rule/2?is_active=true"
        Entao a API retorna o status HTTP 200
        E o campo "is_active" da regra retornada é verdadeiro

    Cenario: Tentar desativar regra que já está inativa
        Dado que existe uma regra já inativa com id 2
        Quando uma requisição PATCH é enviada para "/rule/2?is_active=false"
        Entao a API retorna o status HTTP 409

    Cenario: Tentar ativar regra que já está ativa
        Dado que existe uma regra já ativa com id 1
        Quando uma requisição PATCH é enviada para "/rule/1?is_active=true"
        Entao a API retorna o status HTTP 409

    Cenario: Tentar ativar regra inexistente
        Dado que não existe nenhuma regra de qualidade com id 9999
        Quando uma requisição PATCH é enviada para "/rule/9999?is_active=true"
        Entao a API retorna o status HTTP 404

    Cenario: Tentar desativar regra inexistente
        Dado que não existe nenhuma regra de qualidade com id 9999
        Quando uma requisição PATCH é enviada para "/rule/9999?is_active=false"
        Entao a API retorna o status HTTP 404
