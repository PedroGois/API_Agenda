# 📘 Agenda API (Flask)

API simples para gerenciamento de contatos, criada para estudos de Python e Flask.

## 🚀 Como Rodar

1. **Instale as dependências:**
   ```bash
   pip install flask
````

2.  **Rode o servidor:**
    ```bash
    python app.py
    ```

## 🔗 Rotas (Endpoints)

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `GET` | `/contatos` | Lista todos os contatos |
| `GET` | `/contatos/<id>` | Visualiza um contato único |
| `POST` | `/contatos` | Cria um novo contato |
| `PUT` | `/contatos/<id>` | Edita um contato existente |
| `DELETE` | `/contatos/<id>` | Remove um contato |

## 📄 Exemplo de JSON

Use este formato no corpo da requisição (Body) para **POST** ou **PUT**:

```json
{
  "nome": "João da Silva",
  "telefone": "(11) 99999-9999"
}
```

