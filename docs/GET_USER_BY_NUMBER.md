## Teste do Endpoint GET /users

### Descrição
Endpoint que retorna um usuário ao procurar pelo seu número. **Apenas admin pode acessar.**

### Endpoint
```
GET /users?number=<numero_do_usuario>
```

### Autenticação
- **Requerido**: Admin Token (do `.env` - `ADMIN_TOKEN`)
- **Header**: `Authorization: Bearer <ADMIN_TOKEN>`

### Query Parameters
| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `number` | string | ✓ | O número do usuário a buscar (1-50 caracteres) |

### Response Model (200 OK)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "testuser",
  "number": "123456",
  "created_at": "2026-03-22T10:30:00"
}
```

### Status Codes
| Código | Descrição |
|--------|-----------|
| `200 OK` | Usuário encontrado e retornado |
| `400 Bad Request` | Parâmetro `number` inválido |
| `401 Unauthorized` | Token inválido ou ausente |
| `403 Forbidden` | Token não é admin |
| `404 Not Found` | Nenhum usuário com aquele número |

### Exemplos

#### ✅ Sucesso - Admin busca usuário por número
```bash
curl -X GET "http://localhost:8000/users?number=123456" \
  -H "Authorization: Bearer admin-secret-token-12345-change-in-production" \
  -H "Content-Type: application/json"
```

**Response (200)**:
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "username": "testuser",
  "number": "123456",
  "created_at": "2026-03-22T10:30:00.123456"
}
```

#### ❌ Erro - Sem passar admin token
```bash
curl -X GET "http://localhost:8000/users?number=123456"
```

**Response (401)**:
```json
{
  "detail": "Not authenticated"
}
```

#### ❌ Erro - Token regular (não admin)
```bash
# Supondo que eyJhbGc... é um token JWT de usuário normal
curl -X GET "http://localhost:8000/users?number=123456" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response (403)**:
```json
{
  "detail": "Admin token required"
}
```

#### ❌ Erro - Usuário não encontrado
```bash
curl -X GET "http://localhost:8000/users?number=999999" \
  -H "Authorization: Bearer admin-secret-token-12345-change-in-production"
```

**Response (404)**:
```json
{
  "detail": "User with number '999999' not found"
}
```

#### ❌ Erro - número vazio
```bash
curl -X GET "http://localhost:8000/users?number=" \
  -H "Authorization: Bearer admin-secret-token-12345-change-in-production"
```

**Response (400)**:
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["query", "number"],
      "msg": "String should have at least 1 character"
    }
  ]
}
```

### Uso em Código

#### Python (requests)
```python
import requests

ADMIN_TOKEN = "admin-secret-token-12345-change-in-production"
BASE_URL = "http://localhost:8000"

response = requests.get(
    f"{BASE_URL}/users",
    params={"number": "123456"},
    headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
)

if response.status_code == 200:
    user = response.json()
    print(f"User found: {user['username']} ({user['id']})")
    print(f"Created at: {user['created_at']}")
elif response.status_code == 404:
    print("User not found")
elif response.status_code == 403:
    print("Admin token required")
else:
    print(f"Error: {response.status_code}")
```

#### JavaScript (fetch)
```javascript
const ADMIN_TOKEN = "admin-secret-token-12345-change-in-production";
const BASE_URL = "http://localhost:8000";
const number = "123456";

fetch(`${BASE_URL}/users?number=${number}`, {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${ADMIN_TOKEN}`,
    'Content-Type': 'application/json'
  }
})
.then(response => {
  if (response.status === 200) return response.json();
  throw new Error(`Status ${response.status}`);
})
.then(user => {
  console.log(`User: ${user.username}`);
  console.log(`ID: ${user.id}`);
  console.log(`Created: ${user.created_at}`);
})
.catch(error => console.error('Error:', error));
```

#### TypeScript (axios)
```typescript
import axios from 'axios';

interface User {
  id: string;
  username: string;
  number: string;
  created_at: string;
}

async function getUserByNumber(number: string): Promise<User | null> {
  const ADMIN_TOKEN = "admin-secret-token-12345-change-in-production";
  
  try {
    const response = await axios.get<User>(
      'http://localhost:8000/users',
      {
        params: { number },
        headers: {
          'Authorization': `Bearer ${ADMIN_TOKEN}`
        }
      }
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error(`API Error: ${error.response?.status} - ${error.response?.data.detail}`);
    }
    return null;
  }
}

// Usage
const user = await getUserByNumber("123456");
if (user) {
  console.log(`Found user: ${user.username}`);
}
```

### Comparação: Duas formas de acessar usuários como admin

#### 1️⃣ Via UUID (quando já se conhece o ID)
```bash
# Usando get_current_user com user_id parameter
curl "http://localhost:8000/api/categories?user_id=550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer admin-token"
```

#### 2️⃣ Via Número (quando se conhece apenas o número)
```bash
# Usando novo endpoint /users
curl "http://localhost:8000/users?number=123456" \
  -H "Authorization: Bearer admin-token"
```

**Quando usar cada um:**
- Use `/users?number=X` quando precisar descobrir o UUID de um usuário
- Use `/api/endpoint?user_id=X` quando já tiver o UUID

### Padrão Recomendado para Admin

```python
# Passo 1: Obter usuário pelo número
user = requests.get(
    f"{BASE_URL}/users?number=123456",
    headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
).json()

# Passo 2: Usar o UUID para acessar dados
user_id = user['id']
categories = requests.get(
    f"{BASE_URL}/api/categories?user_id={user_id}",
    headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
).json()

print(f"Categories for user {user['username']}: {categories}")
```

### Notas de Implementação

- ✔️ Apenas tokens admin podem acessar este endpoint
- ✔️ Retorna dados públicos do usuário (sem senha)
- ✔️ Case-sensitive para o número (exato match)
- ✔️ Validação de comprimento (1-50 caracteres)
- ✔️ Response model garante segurança de campo
