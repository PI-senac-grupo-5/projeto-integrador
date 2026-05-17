# Projeto Integrador - Senac EAD

## Tema do Projeto

O objetivo do projeto usando o 50k Bug Dataset é organizar e analisar os registros de bugs para extrair informações
úteis
que ajudem a entender padrões, severidade e evolução dos problemas reportados.

## Integrantes

- José Lucas Evélinton da silva
- Jessica Dutra Ribeiro
- Anne Caroline Risso Sulzer
- Renato de Sena da Silva
- Lucas Randon Marques
- Guilherme Piva Matte

## Times

- Time 1 [Lucas Randon Marques | Anne Caroline Risso Sulzer]
- Time 2 [Jessica Dutra Ribeiro | José Lucas Evélinton da silva]
- Time 3 [Guilherme Piva Matte | Renato de Sena da Silva]

## Contexto

O arquivo bug_dataset_50k.csv contém informações detalhadas sobre 50.000 relatórios de erros de software coletados de
vários projetos. Cada linha representa um único bug e inclui um identificador exclusivo (bug_id), um título curto e uma
descrição detalhada que explica o problema. Ele também contém um código de erro associado ao bug, uma categoria de bug
classificando o tipo de problema e o domínio de bug indicando o subsistema afetado. Campos adicionais incluem a pilha de
tecnologia envolvida, a gravidade do bug (Baixo, Médio, Alto, Crítico), o ambiente em que ocorreu (Desenvolvimento,
Encenação, Produção) e a função de desenvolvedor designada para resolvê-lo. Este arquivo é adequado para tarefas como
classificação de bugs, recomendação de desenvolvedores e análise exploratória de defeitos de software em tecnologias e
ambientes.

## Objetivo da Análise

Explicar brevemente o que o grupo pretende descobrir ou demonstrar com os dados.

## Streamlit

A aplicação pode ser acessada pelo seguinte link: https://projeto-integrador-grupo-5.streamlit.app

## Planejamento das Tarefas

- *Coleta, validação e transformação dos dados:* Time 1
- *Análise estatística e métricas:* Time 2
- *Visualizações e Dashboards:* Time 3

### Cronograma

- Semana 1: Escolha e organização da base de dados
- Semana 2: Limpeza e transformação dos dados
- Semana 3: Análise e definição das métricas
- Semana 4: Desenvolvimento do ETL
- Semana 5: Criação do dashboard e ajustes finais

## Transformações previstas

- Remoção de valores nulos
- Normalização de valores
- Redução significativa do `CSV` final com redução de redundância nas `string` de certas colunas

## Métricas Definidas

| Métrica                    | Objetivo                           | Resultado Esperado               |
|----------------------------|------------------------------------|----------------------------------|
| Quantidade total de bugs   | Medir volume de falhas registradas | Controle das ocorrências         |
| Distribuição de severidade | Identificar gravidade dos bugs     | Priorização de correções         |
| Bugs por ambiente          | Avaliar estabilidade dos ambientes | Identificação de falhas críticas |
| Média de códigos de erro   | Avaliar padrões numéricos          | Identificação de recorrências    |
| Taxa de bugs críticos      | Medir impacto das falhas graves    | Redução de riscos no sistema     |


### Observações

- Todas as etapas serão registradas neste repositório.
- O README será atualizado conforme o projeto evoluir.