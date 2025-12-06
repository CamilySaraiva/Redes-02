# Sistema PUB/SUB com Sockets TCP - Feed de Notícias

Sistema distribuído cliente-servidor para um feed de notícias contínuo usando Sockets TCP.

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

**Remover categoria:**

```
> REMOVER tecnologia
```

**Sair:**

```
> SAIR
```

### Editor

Digite o título, resumo e categoria da notícia. Formato:

```
Título: Python 3.13
Resumo: Nova versão com melhorias
Categoria: tecnologia
```

## 🔄 Como Funciona

1. **Servidor** aceita múltiplas conexões TCP
2. **Cliente** se conecta e se inscreve em categorias
3. **Editor** publica notícia para uma categoria
4. **Servidor** envia notícia automaticamente para clientes inscritos
5. **Cliente** recebe notícia em tempo real (sem fazer requisição)

## 📂 Arquivos

```
src/
├── servidor.py       # Servidor TCP
├── cliente.py        # Cliente TCP
└── editor.py         # Editor de notícias
```

## 🎯 Categorias Disponíveis

- tecnologia
- esportes
- cultura
- politica
- saude

