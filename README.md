# Sistema de Detecção e Soma de Dados com OpenCV

## 1. Visão geral

Este projeto implementa um sistema de **visão computacional em Python** capaz de receber uma imagem contendo um ou mais dados sobre um fundo neutro, identificar os dados presentes na imagem, contar os pontos de suas faces e calcular a soma total.

A solução foi desenvolvida utilizando principalmente a biblioteca **OpenCV**, com apoio do **NumPy** e da classe `Counter`, da biblioteca padrão do Python.

O algoritmo foi estruturado utilizando **Programação Orientada a Objetos (POO)** por meio da classe `ContadorDeDados`.

> **Observação importante:** a lógica funcional do algoritmo original foi preservada. As alterações realizadas para a entrega concentram-se na organização e no aprimoramento dos comentários explicativos, sem modificar a estratégia de processamento que já apresentava os resultados esperados nas imagens de teste.

---

## 2. Objetivo

O objetivo da atividade é desenvolver um pequeno sistema capaz de:

1. Ler uma imagem contendo uma quantidade variável de dados;
2. Localizar os dados presentes na imagem;
3. Identificar os pontos existentes em cada face;
4. Determinar o valor de cada dado;
5. Somar os valores encontrados;
6. Exibir o resultado no terminal e também visualmente sobre a imagem.

O processamento é realizado automaticamente a partir da imagem fornecida pelo usuário.

---

## 3. Tecnologias utilizadas

| Tecnologia | Utilização |
|---|---|
| **Python 3** | Linguagem utilizada no desenvolvimento |
| **OpenCV (`cv2`)** | Processamento e análise das imagens |
| **NumPy** | Operações com matrizes e pixels |
| **Counter** | Identificação da contagem mais frequente |
| **HSV** | Segmentação dos dados pela cor |
| **Transformada de Distância** | Identificação dos centros dos pontos |
| **Componentes Conectados** | Contagem dos pontos encontrados |

---

## 4. Estrutura do algoritmo

O processamento segue um pipeline de visão computacional:

```text
Imagem de entrada
       │
       ▼
Leitura da imagem
       │
       ▼
Conversão BGR → HSV
       │
       ▼
Segmentação pela cor dos dados
       │
       ▼
Criação da máscara
       │
       ▼
Operações morfológicas
       │
       ▼
Detecção dos contornos
       │
       ▼
Identificação dos dados
       │
       ▼
Análise individual de cada dado
       │
       ▼
Identificação dos pontos brancos
       │
       ▼
Limiarização + Otsu
       │
       ▼
Transformada de Distância
       │
       ▼
Máximos locais
       │
       ▼
Componentes conectados
       │
       ▼
Valor de cada dado
       │
       ▼
Soma final
       │
       ▼
Imagem com resultado + terminal
```

---

# 5. Organização em Programação Orientada a Objetos

A solução utiliza a classe:

```python
class ContadorDeDados:
```

Essa classe concentra as operações necessárias para o processamento.

### Principais métodos

| Método | Responsabilidade |
|---|---|
| `__init__()` | Inicializa os parâmetros utilizados pelo algoritmo |
| `localizar_dados()` | Localiza os dados utilizando segmentação por cor |
| `_contar_para_limiar()` | Identifica os pontos para um determinado limiar |
| `valor_do_dado()` | Determina o valor de um dado |
| `processar()` | Executa o processamento completo da imagem |

Essa organização permite dividir o algoritmo em etapas com responsabilidades específicas, deixando o código mais organizado e facilitando sua manutenção.

---

# 6. Leitura da imagem

A imagem é carregada utilizando:

```python
imagem = cv2.imread(caminho)
```

O OpenCV trabalha, por padrão, com imagens coloridas no formato **BGR**.

Antes de continuar o processamento, o algoritmo verifica se a imagem foi carregada corretamente. Caso o arquivo não seja encontrado ou não possa ser aberto, é gerado um `FileNotFoundError`.

---

# 7. Conversão de BGR para HSV

Depois da leitura, a imagem é convertida:

```python
hsv = cv2.cvtColor(imagem, cv2.COLOR_BGR2HSV)
```

O espaço de cores HSV foi escolhido porque separa melhor algumas características da imagem:

- **H (Hue):** representa a matiz ou tonalidade da cor;
- **S (Saturation):** representa a intensidade/saturação da cor;
- **V (Value):** representa o brilho.

Essa separação facilita a identificação dos dados roxos em relação ao fundo neutro.

---

# 8. Segmentação por cor

A função:

```python
cv2.inRange()
```

é utilizada para criar uma máscara a partir de uma faixa de valores HSV.

O algoritmo utiliza:

```python
mascara = cv2.inRange(
    hsv,
    (115, 90, 60),
    (165, 255, 255)
)
```

A máscara é uma imagem binária na qual:

- `255` representa pixels que estão dentro da faixa selecionada;
- `0` representa pixels que estão fora da faixa.

Dessa maneira, o algoritmo consegue separar aproximadamente a região ocupada pelos dados do restante da imagem.

---

# 9. Operações morfológicas

Após a segmentação, a máscara pode apresentar pequenas falhas ou ruídos.

Por isso são utilizadas operações morfológicas.

## Fechamento

```python
cv2.MORPH_CLOSE
```

O fechamento ajuda a preencher pequenos buracos ou falhas dentro das regiões identificadas como dados.

Isso é especialmente importante porque os pontos claros presentes nos dados podem provocar pequenas interrupções na máscara.

## Abertura

```python
cv2.MORPH_OPEN
```

A abertura ajuda a remover pequenas regiões isoladas que podem ser interpretadas como ruído.

Dessa forma, a máscara fica mais adequada para a próxima etapa: a identificação dos contornos.

---

# 10. Detecção dos dados através de contornos

A função:

```python
cv2.findContours()
```

é utilizada para encontrar os contornos presentes na máscara.

O algoritmo utiliza:

```python
cv2.RETR_EXTERNAL
```

para trabalhar com os contornos externos.

Depois, a área de cada contorno é analisada:

```python
cv2.contourArea(c)
```

Somente contornos com área maior que a área mínima configurada são considerados dados.

Isso evita que pequenos ruídos sejam interpretados como novos dados.

---

# 11. Análise individual dos dados

Depois que os dados são localizados, o algoritmo percorre cada contorno:

```python
for c in contornos:
```

Cada dado é analisado individualmente.

Isso é importante porque a quantidade de dados presentes na imagem pode variar.

Para cada dado, o algoritmo procura seus pontos e determina seu valor.

---

# 12. Criação da medida de brilho

Para identificar os pontos brancos, o algoritmo calcula uma medida de brilho utilizando os canais `V` e `S` do HSV:

```python
brilho = (
    hsv[:, :, 2].astype(np.float32) *
    (1 - hsv[:, :, 1].astype(np.float32) / 255)
).astype(np.uint8)
```

A ideia é destacar regiões que apresentam alto brilho e baixa saturação, características esperadas de regiões brancas.

Assim, o cálculo ajuda a diferenciar os pontos brancos de outras regiões claras que ainda possuem uma coloração mais forte.

---

# 13. Máscara individual do dado

Para analisar somente a região de um determinado dado, é criado um casco convexo:

```python
casco = cv2.convexHull(contorno)
```

Depois é criada uma máscara preenchendo essa região:

```python
cv2.drawContours(
    mascara,
    [casco],
    -1,
    255,
    -1
)
```

Com isso, o algoritmo consegue concentrar a análise dos pontos na área correspondente ao dado.

---

# 14. Limiarização e método de Otsu

O algoritmo utiliza:

```python
cv2.threshold()
```

com:

```python
cv2.THRESH_OTSU
```

O método de Otsu calcula automaticamente um limiar com base nos valores de intensidade presentes na região analisada.

O valor encontrado por Otsu não é utilizado isoladamente. Ele serve como ponto inicial para testar vários limiares.

O algoritmo faz isso através de:

```python
for limiar in range(int(otsu), 250, 5):
```

Assim, diferentes níveis de brilho são testados.

Essa estratégia torna a identificação menos dependente de um único limiar e ajuda diante de pequenas diferenças de iluminação e reflexos.

---

# 15. Identificação dos pontos brancos

Depois de escolhido um limiar, o algoritmo realiza uma binarização:

```python
pontos = (
    (brilho > limiar) &
    (mascara_larga > 0)
).astype(np.uint8) * 255
```

O objetivo é obter uma imagem na qual as regiões claras dentro da área do dado sejam destacadas.

Em seguida, uma operação de abertura morfológica ajuda a eliminar pequenos reflexos e regiões muito finas que não correspondem aos pontos.

---

# 16. Transformada de Distância

Uma das etapas mais importantes do algoritmo é:

```python
dist = cv2.distanceTransform(
    pontos,
    cv2.DIST_L2,
    5
)
```

A Transformada de Distância calcula uma medida de distância de cada pixel da região branca até a região preta mais próxima.

Como consequência, o centro de uma região branca tende a apresentar valores maiores.

Esses valores são utilizados como **picos**, que representam possíveis centros dos pontos do dado.

Essa estratégia é útil principalmente quando dois pontos estão próximos ou aparecem unidos depois da binarização.

---

# 17. Máximos locais

Depois da Transformada de Distância, o algoritmo utiliza uma dilatação:

```python
maximos_locais = cv2.dilate(...)
```

O objetivo é identificar regiões que representam máximos locais da distância.

Depois são aplicadas condições relacionadas ao tamanho do dado:

```python
dist >= 0.095 * lado
dist <= 0.15 * lado
```

Esses limites ajudam a eliminar regiões que sejam pequenas ou grandes demais para representar um ponto.

---

# 18. Componentes conectados

Após encontrar os picos, é utilizada:

```python
cv2.connectedComponentsWithStats()
```

Essa função identifica regiões conectadas.

Cada região encontrada representa um possível ponto.

O componente de índice `0` representa o fundo, por isso o algoritmo utiliza:

```python
centros[1:]
```

para ignorá-lo.

A quantidade de centros encontrados corresponde à quantidade de pontos identificados no dado.

---

# 19. Escolha do valor mais estável

Como vários limiares são testados, podem aparecer pequenas diferenças nas quantidades encontradas.

Por exemplo:

```text
[4, 4, 4, 3, 4, 5]
```

Nesse caso, a quantidade `4` aparece mais vezes.

Para encontrar essa quantidade mais frequente, o código utiliza:

```python
Counter(contagens).most_common(1)[0][0]
```

Assim, o algoritmo utiliza a contagem que apareceu com maior frequência como o valor do dado.

Essa é uma forma de tornar o resultado mais resistente a pequenas variações causadas por iluminação e reflexos.

---

# 20. Resultado visual

Depois de identificar cada dado, o algoritmo desenha um retângulo ao redor dele:

```python
cv2.rectangle(...)
```

Também escreve o valor encontrado:

```python
cv2.putText(...)
```

Dessa forma, o usuário consegue visualizar quais regiões foram identificadas e qual valor foi atribuído a cada uma.

---

# 21. Cálculo da soma

Os valores encontrados são armazenados em uma lista:

```python
valores.append(valor)
```

Depois todos os valores são somados:

```python
soma = sum(valores)
```

A soma também é escrita na imagem:

```python
cv2.putText(
    resultado,
    f"Soma = {soma}",
    ...
)
```

Além disso, o resultado é apresentado no terminal.

---

# 22. Entrada do programa

O programa pode receber o nome da imagem diretamente pela linha de comando:

```text
python dados.py img1.jpg
```

Caso nenhum argumento seja fornecido, o programa solicita o nome da imagem:

```text
Digite o nome da imagem (ex.: img1.jpg):
```

Essa estrutura permite utilizar o mesmo algoritmo com diferentes imagens sem precisar alterar o código.

---

# 23. Saída do programa

No terminal são apresentados:

```text
Quantidade de dados encontrados: ...
Valor de cada dado: [...]
SOMA DAS FACES: ...
```

Além disso, é aberta uma janela contendo a imagem processada, com:

- retângulos ao redor dos dados;
- valor identificado em cada dado;
- soma total.

O resultado também pode ser salvo com o prefixo:

```text
resultado_
```

---

# 24. Exemplos de resultados

Os resultados esperados nas imagens de teste fornecidas são:

| Imagem | Valores encontrados | Soma |
|---|---:|---:|
| `img1.jpg` | `[1, 4, 6]` | `11` |
| `img2.jpg` | `[4]` | `4` |
| `img3.jpg` | `[6, 2, 3, 4]` | `15` |
| `img4.jpg` | `[3, 1, 2, 1]` | `7` |

---

# 25. Fundamentos de visão computacional utilizados

O algoritmo aplica diferentes fundamentos de processamento e análise de imagens:

- **Conversão de espaço de cores:** BGR para HSV;
- **Segmentação por cor:** seleção dos pixels pertencentes aos dados;
- **Imagem binária/máscara:** separação entre objeto e fundo;
- **Morfologia matemática:** abertura, fechamento e dilatação;
- **Detecção de contornos:** localização dos dados;
- **Análise de área:** eliminação de pequenos ruídos;
- **Limiarização:** separação das regiões claras;
- **Método de Otsu:** escolha automática de um limiar inicial;
- **Transformada de Distância:** localização dos centros dos pontos;
- **Máximos locais:** identificação dos possíveis centros;
- **Componentes conectados:** contagem das regiões identificadas.

A combinação dessas técnicas forma um pipeline completo de visão computacional aplicado a um problema específico.

---

# 26. Organização e manutenção

O código foi mantido com a mesma lógica funcional utilizada nos testes.

As melhorias realizadas para a entrega foram principalmente relacionadas à **documentação interna do código**, com comentários explicando:

- o propósito de cada etapa;
- o motivo da utilização das principais técnicas;
- o significado dos resultados intermediários;
- a relação entre as operações do OpenCV e o objetivo do algoritmo.

Não foram adicionadas funcionalidades que pudessem alterar o comportamento do processamento original.

---

# 27. Conclusão

O sistema desenvolvido utiliza conceitos de **Programação Orientada a Objetos** e diferentes técnicas de **visão computacional com OpenCV** para resolver o problema de identificação e soma das faces de dados em uma imagem.

O processamento é realizado de forma sequencial: primeiro os dados são separados do fundo pela cor, depois são encontrados seus contornos e, individualmente, suas faces são analisadas para localizar os pontos brancos.

A utilização de morfologia, limiarização, Otsu, Transformada de Distância e componentes conectados permite construir uma solução mais robusta do que uma simples contagem de pixels claros.

Por fim, o sistema apresenta o valor de cada dado, calcula a soma total e fornece uma visualização da análise realizada sobre a imagem.

---

## 28. Arquivos

O projeto pode ser organizado da seguinte maneira:

```text
atividade/
│
├── dados.py
├── img1.jpg
├── img2.jpg
├── img3.jpg
├── img4.jpg
│
└── resultado_img1.jpg
```

Para a entrega solicitada pela atividade, o código completo foi disponibilizado em um **único arquivo TXT**, conforme a orientação do enunciado.
