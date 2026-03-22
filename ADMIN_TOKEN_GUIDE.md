# Admin Token - Guia de Uso

## Configuração

O token admin foi configurado através da variável de ambiente `ADMIN_TOKEN` no arquivo `.env`:

```
ADMIN_TOKEN="admin-secret-token-12345-change-in-production"
```

**⚠️ IMPORTANTE**: Mude este token em produção para uma string segura e única.

## Funcionamento

### 1. Token Admin vs Token de Usuário Regular

**Token de Usuário Regular:**
- Gerado via endpoints `/auth/register` ou `/auth/login`
- JWT com claims: `{"sub": "uuid-do-usuario", "exp": timestamp}`
- Expira conforme `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`
- Acesso limitado aos dados do próprio usuário

**Token Admin:**
- Configurável em `.env` via `ADMIN_TOKEN`
- String simples (não é JWT)
- Nunca expira
- Pode acessar dados de qualquer usuário passando `user_id` como query parameter

### 2. Como Usar o Token Admin

#### Acessar dados de um usuário específico (com user_id):

```bash
curl -X GET "http://localhost:8000/api/categories?user_id=550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer admin-secret-token-12345-change-in-production"
```

**Resposta esperada:**
```json
{
  "categories": [...]  // Categorias do usuário específico
}
```

**Status Codes:**
- `200 OK` - Usuário encontrado, dados retornados
- `404 Not Found` - Usuário com aquele UUID não existe
- `400 Bad Request` - `user_id` não é um UUID válido
- `401 Unauthorized` - Token inválido
- `422 Unprocessable Entity` - Token admin sem `user_id` query parameter

#### Tentar usar token admin sem user_id (ERRO):

```bash
curl -X GET "http://localhost:8000/api/categories" \
  -H "Authorization: Bearer admin-secret-token-12345-change-in-production"
```

**Resposta:**
```json
{
  "detail": "Admin token requires 'user_id' query parameter to be specified"
}
```

**Status: 422 Unprocessable Entity**

#### Tentar usar token regular com user_id (ERRO):

```bash
curl -X GET "http://localhost:8000/api/categories?user_id=550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Resposta:**
```json
{
  "detail": "Only admin tokens can specify 'user_id' parameter"
}
```

**Status: 403 Forbidden**

### 3. Fluxo de Autenticação

```
Request HTTP
  ↓
1. Verificar credencial (Bearer token)
  ↓
2. Decodificar token:
   - Se igual a ADMIN_TOKEN → is_admin=True, sub=None
   - Se não → decodificar como JWT
  ↓
3. Se admin + user_id presente → buscar usuário com aquele ID
   Se admin + sem user_id → ERROR 422
   Se não-admin + user_id presente → ERROR 403
   Se não-admin + sem user_id → usar usuário do token (comportamento normal)
  ↓
4. Retornar dados do usuário ou erro
```

## Casos de Uso

### Admin acessando dados de todos os usuários:
```python
import requests

ADMIN_TOKEN = "admin-secret-token-12345-change-in-production"
BASE_URL = "http://localhost:8000"

# Lista de UUIDs dos usuários
user_ids = [
    "550e8400-e29b-41d4-a716-446655440000",
    "550e8400-e29b-41d4-a716-446655440001",
    "550e8400-e29b-41d4-a716-446655440002",
]

for user_id in user_ids:
    response = requests.get(
        f"{BASE_URL}/api/transactions",
        params={"user_id": user_id},
        headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
    )
    
    if response.status_code == 200:
        print(f"User {user_id}: {response.json()}")
    else:
        print(f"User {user_id}: Error {response.status_code} - {response.text}")
```

### Relatório consolidado de admin:
```python
# Gerar relatório de todas as transações de todos os usuários
transactions_by_user = {}

for user_id in all_user_ids:
    response = requests.get(
        f"{BASE_URL}/api/transactions",
        params={"user_id": user_id},
        headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
    )
    
    if response.status_code == 200:
        transactions_by_user[user_id] = response.json()

# Processar dados consolidados...
print(f"Transações de {len(transactions_by_user)} usuários")
```

## Segurança

### Pontos fortes:
✅ Token admin é uma string fixa, não JWT decodificável  
✅ Expiração zero = credencial permanente (esperado)  
✅ Requer `user_id` explícito para evitar acesso acidental  
✅ Usuários regulares NÃO podem usar `user_id` parameter  
✅ Isolamento mantido entre usuários normais  

### Recomendações:
- 🔐 **Produção**: Mude `ADMIN_TOKEN` para um string seguro (ex: UUID ou token gerado com `secrets.token_urlsafe()`)
- 📝 **Auditoria**: Adicionar logs quando admin acessa usuário (para rastreabilidade)
- 🔑 **Rotação**: Se token vazar, altere `.env` e reinicie serviço
- ⏰ **Monitoramento**: Alertar se admin token é usado repetidamente (possível comprometimento)

## Exemplos em Diferentes Linguagens

### JavaScript/Fetch:
```javascript
const ADMIN_TOKEN = "admin-secret-token-12345-change-in-production";
const userId = "550e8400-e29b-41d4-a716-446655440000";

fetch(`http://localhost:8000/api/categories?user_id=${userId}`, {
  headers: {
    "Authorization": `Bearer ${ADMIN_TOKEN}`
  }
})
.then(r => r.json())
.then(data => console.log(data));
```

### Python Requests:
```python
import requests

response = requests.get(
    "http://localhost:8000/api/categories",
    params={"user_id": "550e8400-e29b-41d4-a716-446655440000"},
    headers={"Authorization": "Bearer admin-secret-token-12345-change-in-production"}
)
print(response.json())
```

### cURL:
```bash
curl "http://localhost:8000/api/categories?user_id=550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer admin-secret-token-12345-change-in-production"
```

## Teste Rápido

```bash
# 1. Iniciara aplicação
uv run python main.py

# 2. Em outro terminal, criar um usuário
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","number":"123","password":"password123"}'

# Copiar o UUID retornado (ex: 550e8400-e29b-41d4-a716-446655440000)

# 3. Acessar com token admin
curl "http://localhost:8000/api/categories?user_id=550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer admin-secret-token-12345-change-in-production"
```

## Troubleshooting

| Erro | Causa | Solução |
|------|-------|---------|
| `401 Unauthorized` | Token inválido | Verificar `ADMIN_TOKEN` em `.env` |
| `422 Unprocessable Entity` | Admin sem `user_id` | Adicionar `?user_id=xxx` na URL |
| `403 Forbidden` | Token regular com `user_id` | Remover `?user_id=xxx` ou usar admin token |
| `404 Not Found` | Usuário não existe | Verificar UUID do usuário |
| `400 Bad Request` | UUID inválido | Verificar formato do `user_id` (deve ser UUID) |

