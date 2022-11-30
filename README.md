# Instalação

Necessário ter o Python > 3.8 instalado.
Na raiz do diretório execute
```sh
$ pip install -r requirements.txt
```

# Executar
Na raiz do diretório execute

```sh
$ python main.py
```

# Saída

Será gerado um arquivo `hull_best_<id_grafo>.gexf` contendo o melhor fecho inicial encontrado para o problema. Esse arquivo pode ser visualizado com o programa [Gephi](https://gephi.org/).

# Variáveis

As variáveis estão definidas no arquivo `.env`

- **INITIAL_GRAPH**: o número que representa o arquivo que contém o grafo. Por exemplo, se o arquivo tiver o nome `01.txt` então esta variável deverá ter valor `01`.
- **CONTAMINANTS**: o número de vizinhos que devem estar contaminados para contaminar um vértice no problema do fecho convexo.
- **LENGTH_SAMPLE**: o número de conjuntos aleatórios que deverão ser gerados para buscar uma melhor solução durante a fase de otimização.
- **STOP_ON_FIRST_BEST_SAMPLE**: se definido como `True` não precisará gerar `LENGTH_SAMPLE` conjuntos para encontrar o melhor. No primeiro conjunto que for melhor que a melhor solução atual o algoritmo de geração de conjuntos será interrompido para prosseguir para a próxima tentativa da fase de otimização.
- **FLEXIBLE_BINARY_SEARCH**: se definido como `True` irá realizar o reset do tamanho do conjunto mínimo para 1 sempre que encontrar uma melhor solução na busca binária. É equivalente a rodar uma nova busca binária sempre que encontrar uma nova solução melhor.
- **WITH_WEIGHT**: se definido como `True` fará a seleção do conjunto de vértices pertencente ao fecho inicial aleatório baseado em pesos.
- **VELOCITY**: multiplicador do peso de um vértice ao encontrar uma nova solução na fase de geração de conjuntos aleatórios.
- **ONE_IN**: inverso da probabilidade de se escolher um conjunto igual na amostragem sem repetição por pesos. Por exemplo, se for 100, significa que na amostragem existe 1 chance em 100 de se obter um fecho convexo igual ao já encontrado.

# Formatação de Arquivos

## Grafo

É esperado que o arquivo de entrada tenha o nome `<id_grafo>.txt` e neste arquivo M linhas contendo dois números inteiros A e B (A >= 0, B >= 0) que representam a aresta (A, B) do grafo.

Exemplo:
```
0 1

1 2

1 3

1 4
```

# Grafos de Exemplo

- 05.txt
    - tipo: clique expansão
- 00.txt
    - tipo: escada
- 01.txt
    - tipo: clique expansão estranho