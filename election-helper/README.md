
# Ajudante de Eleições
O código presente nessa sub-árvore do repositório tem como propósito auxiliar processos automatizáveis que envolvem a eleição de um artigo candidato a ser lido pelo Clube.

## Instalação
### Pré-requisitos
- Python 3.8

### Passo-a-passo
Uma vez clonado o repositório, basta executar o comando `bash` abaixo para configurar um ambiente Python capaz de interpretar o código-fonte do módulo ajudante.

```
make all
```

O comando criará um ambiente Python no diretório `.venv`, instalará as dependências especificadas no arquivo `requirements.txt` neste ambiente, e criará um executável no caminho `bin/helper`.

## Casos de uso
Essa seção do documento descreve casos de uso do módulo ajudante, almejando solucionar alguns dos processos mais comuns durante a eleição de artigos.

Os exemplos abaixo assumem que o diretório `bin` criado pelas regras do arquivo `Makefile` está dentro dos diretórios executáveis pelo sistema.

### Mostrar artigos vencedores
Ao final de cada eleição, podemos facilmente visualizar quais são os artigos mais votados através do seguinte comando:

```
helper
```

ou

```
helper --view winners
```

### Deletando todos os votos
É comum apagarmos todos os votos a cada eleição. Isso pode ser feito através do comando abaixo:

```
helper --view clear
```

### Verificando a situação dos votantes
É comum os membros do Clube verificarem se os outros membros já votaram, tanto para os colegas do prazo de votação quanto para encerrá-la mais cedo. A quantidade de votos realizada por cada membro do Clube pode ser consultada através do seguinte comando:

```
helper --view voters
```

### Delimitando o escopo
É possível limitar o escopo de artigos e vontantes a serem considerados através dos argumentos `--users` e `--issues`. Por exemplo, caso se queira deletar os votos da Michele e do Jota no artigo _Masked Autoencoders Are Scalable Vision Learners_ (cujo identificador de issue é 64), se executaria o comando abaixo:

```
helper --view clear --users mchelem josepsmartinez --issues 64
```

