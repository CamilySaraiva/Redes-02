# Sistema PUB/SUB com Sockets UDP - Feed de Notícias

Sistema distribuído cliente-servidor para um feed de notícias contínuo usando **Sockets UDP** com **repositório persistente** de notícias.

## 📋 Requisitos

- Python 3.7+
- Nenhuma biblioteca externa

## 🚀 Como Rodar

### Terminal 1 - Servidor

```bash
cd src
python servidor.py
```

### Terminal 2 - Cliente

```bash
cd src
python cliente.py
```

### Terminal 3 - Editor (Publicar Notícias)

```bash
cd src
python editor.py
```

## 📖 Como Usar

### Cliente

**Inscrever em categorias:**

```
> INSCREVER tecnologia
> INSCREVER esportes cultura
```

**Ver inscrições:**

```
> LISTAR
```

**Ver categorias disponíveis:**

```
> CATEGORIAS
```

**Ver histórico de notícias:**

```
> HISTORICO tecnologia
> HISTORICO
```

**Remover categoria:**

```
> REMOVER tecnologia
```

**Sair:**

```
> SAIR
```

### Editor

Digite o título, resumo e categoria da notícia:

```
Título: Python 3.13
Resumo: Nova versão com melhorias
Categoria: tecnologia
```

## 🔄 Como Funciona

1. **Servidor UDP** escuta na porta 5000 e carrega notícias do arquivo `noticias.json`
2. **Cliente** envia comandos via UDP para inscrever-se em categorias
3. **Editor** publica notícia para uma categoria via UDP
4. **Servidor** salva notícia no repositório (memória + arquivo)
5. **Servidor** envia notícia via UDP para todos os clientes inscritos
6. **Cliente** recebe notícia em tempo real
7. **Cliente** pode consultar histórico de notícias antigas

## 💾 Repositório de Notícias

- **Em Memória**: Lista Python com todas as notícias
- **Em Arquivo**: `noticias.json` para persistência
- **Formato**: JSON com id, título, resumo, categoria e data
- **Carregamento**: Automático ao iniciar servidor
- **Salvamento**: Automático a cada nova notícia

## 📂 Arquivos

```
src/
├── servidor.py       # Servidor UDP com repositório
├── cliente.py        # Cliente UDP
├── editor.py         # Editor de notícias
└── noticias.json     # Repositório persistente (gerado automaticamente)
```

## 🎯 Categorias Disponíveis

- tecnologia
- esportes
- cultura
- politica
- saude

## 🔍 Funcionalidades

✅ **Publicação em tempo real**: Notícias chegam instantaneamente  
✅ **Repositório persistente**: Notícias salvas em JSON  
✅ **Histórico**: Consulta de notícias antigas por categoria  
✅ **Multi-cliente**: Vários clientes simultâneos  
✅ **Thread-safe**: Acesso seguro ao repositório  
✅ **UDP**: Comunicação rápida e eficiente