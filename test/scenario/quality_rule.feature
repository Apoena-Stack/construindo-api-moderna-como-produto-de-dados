# language: pt
Funcionalidade: Permitir criação da regra de qualidade para uma determinada tabela e coluna desta tabela.

    Cenario: Solicitada criação de uma regra de qualidade com todos os atributos fornecidos: tipo de regra, nome da tabela, coluna e parâmetros dependendo da regra.
        Dado a criação de um nova nova regra de unicidade com todos os atributos: tipo de regra (unicidade), tabela e coluna
        Quando o método de criação for utilizado passando esses atributos
        Entao a verificacao se a tabela existe
        E se a regra em questao já não existe 
        E criar a regra de qualidade

     Cenario: Solicitada criação de uma regra de qualidade com todos os atributos fornecidos: tipo de regra, nome da tabela, coluna e parâmetros dependendo da regra.
        Dado a criação de um nova nova regra de unicidade com todos os atributos: tipo de regra (unicidade), tabela e coluna
        Quando o método de criação for utilizado passando esses atributos
        Entao a verificacao se a tabela existe
        E se a regra em questao já não existe 
        E criar a regra de qualidade