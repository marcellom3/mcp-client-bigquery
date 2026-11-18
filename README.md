# MCP BigQuery: guia do cliente

Conecte o seu Claude ao **Google BigQuery** para consultar seus dados conversando, em modo **somente leitura**.

Você **não instala servidor, Python nem credenciais do Google**. O administrador da CLI Consultoria envia duas informações, e você as configura no seu Claude:

| Você recebe | Exemplo |
|---|---|
| **URL do servidor** | `https://<endereço-informado>/mcp` |
| **Chave de API** (pessoal, intransferível) | `mcpbq_1a2b3c4d_...` |

A chave já define **qual BigQuery** você acessa (o da CLI ou o da sua empresa) e **quais datasets** (o projeto inteiro ou só alguns).

---

## 1. Antes de começar: o que pedir ao administrador

Envie ao administrador:

- **Quem vai usar:** nome e e-mail de cada pessoa. Cada pessoa recebe a própria chave.
- **Qual BigQuery:**
    - **o da CLI**: só informe quais dados precisa acessar;
    - **o da sua empresa**: siga antes o [passo 4](#4-usando-o-bigquery-da-sua-empresa) e informe o **ID do projeto** GCP.
- **Escopo:** o **projeto inteiro** ou só os **datasets** (liste os nomes).
- **Validade** desejada (opcional), por exemplo 30 dias para um consultor.

Você recebe de volta a **URL** e a **chave**. Guarde a chave como uma senha.

---

## 2. Configurar no Claude Code (recomendado)

Requisito: [Claude Code](https://code.claude.com/docs) instalado e logado.

No terminal (PowerShell, CMD, bash ou zsh), rode o comando abaixo trocando a URL e a chave:

```bash
claude mcp add --transport http --scope user bigquery https://<endereço-informado>/mcp --header "Authorization: Bearer mcpbq_SUA_CHAVE"
```

- `--scope user` deixa o BigQuery disponível em todos os seus projetos. Para usar só na pasta atual, troque por `--scope local`.
- Para conferir, rode `claude mcp list`. Deve aparecer `bigquery ... ✓ Connected`. Dentro do Claude Code, o comando `/mcp` mostra o servidor e as ferramentas.

### Alternativa: chave em variável de ambiente (sem gravá-la em arquivo)

Crie a variável `MCP_BIGQUERY_KEY` com a sua chave.

Windows (PowerShell):

```powershell
setx MCP_BIGQUERY_KEY "mcpbq_SUA_CHAVE"
```

macOS/Linux:

```bash
echo 'export MCP_BIGQUERY_KEY="mcpbq_SUA_CHAVE"' >> ~/.zshrc
```

Depois, crie o arquivo `.mcp.json` na pasta do projeto:

```json
{
  "mcpServers": {
    "bigquery": {
      "type": "http",
      "url": "https://<endereço-informado>/mcp",
      "headers": { "Authorization": "Bearer ${MCP_BIGQUERY_KEY}" }
    }
  }
}
```

Abra um terminal novo para a variável valer.

---

## 3. Configurar no Claude Desktop (app de chat)

### Opção A: arquivo de configuração + `mcp-remote` (funciona hoje, em qualquer plano)

Requisito: [Node.js](https://nodejs.org) 18 ou mais recente instalado.

1. No Claude Desktop, abra **Configurações → Desenvolvedor → Editar configuração**. Isso abre o `claude_desktop_config.json`.
2. Adicione o bloco abaixo, trocando a URL e a chave. Se já existir um `"mcpServers"`, inclua só o item `"bigquery"`.

    ```json
    {
      "mcpServers": {
        "bigquery": {
          "command": "npx",
          "args": ["-y", "mcp-remote", "https://<endereço-informado>/mcp", "--header", "Authorization:${MCP_BIGQUERY_AUTH}"],
          "env": { "MCP_BIGQUERY_AUTH": "Bearer mcpbq_SUA_CHAVE" }
        }
      }
    }
    ```

    > A chave fica no `env`, e não direto nos `args`, porque no Windows espaços dentro dos argumentos quebram o cabeçalho.

3. **Feche o Claude Desktop pela bandeja do sistema** e abra de novo. O BigQuery aparece no menu **+ → Conectores** de cada conversa.

### Opção B: conector personalizado (sem Node.js)

Em **Configurações → Conectores → Adicionar conector personalizado**, informe a URL. O que fazer em seguida depende da sua conta:

- **Se a sua conta mostrar "Request headers"/"Cabeçalhos de requisição":**
    1. Escolha **No sign-in**.
    2. Adicione o cabeçalho `authorization` com o valor `Bearer mcpbq_SUA_CHAVE`.
- **Se não mostrar:** esse recurso ainda está em liberação gradual pela Anthropic. Use a opção A. O login por OAuth está no roadmap do servidor e vai dispensar o `mcp-remote`.
- **Planos Team e Enterprise:** só o Owner da organização adiciona conectores personalizados.

---

## 4. Usando o BigQuery da sua empresa

Pule este passo se você vai consultar dados que já estão no BigQuery da CLI.

### Opção 1 (recomendada): conceder acesso à Service Account da CLI

Nenhuma chave privada da sua empresa sai do seu ambiente, e você pode revogar o acesso quando quiser. O administrador informa o e-mail da Service Account da CLI (`<sa-da-cli>@...iam.gserviceaccount.com`).

No projeto GCP da sua empresa, conceda os dois acessos abaixo.

**1. Permissão para executar consultas no projeto.** Pelo console: **IAM → Conceder acesso** → papel **BigQuery Job User**. Ou pelo gcloud:

```bash
gcloud projects add-iam-policy-binding SEU_PROJETO \
  --member="serviceAccount:<sa-da-cli>" --role="roles/bigquery.jobUser"
```

**2. Leitura só dos datasets que você quer liberar.** Repita para cada dataset. Pode ser pelo editor SQL do BigQuery:

```sql
GRANT `roles/bigquery.dataViewer`
ON SCHEMA `SEU_PROJETO.SEU_DATASET`
TO "serviceAccount:<sa-da-cli>";
```

Ou pelo console: dataset → **Compartilhamento → Permissões → Adicionar principal** → **BigQuery Data Viewer**.

Por fim, envie ao administrador o **ID do projeto**, os **datasets** liberados e a **região** dos dados (ex.: `US`, `southamerica-east1`).

> As consultas são cobradas no **seu** projeto GCP. O servidor limita cada consulta (padrão de 10 GB processados) e aceita só `SELECT`.

### Opção 2: enviar uma Service Account da sua empresa

1. Crie uma Service Account com os mesmos dois papéis da opção 1 (**Job User** no projeto, **Data Viewer** só nos datasets).
2. Gere a chave JSON.
3. Envie ao administrador **por um canal seguro, nunca por e-mail aberto ou chat**.

---

## 5. Usando

Converse normalmente. Exemplos:

- "Quais datasets e tabelas eu tenho no BigQuery?"
- "Mostre o schema da tabela `vendas.pedidos`."
- "Quanto custaria consultar o faturamento de 2025 por mês?" (estimativa com `dry_run_query`, sem executar)
- "Qual foi o faturamento por mês em 2025?"

O Claude tem estas ferramentas: `list_datasets`, `list_tables`, `get_table_schema`, `dry_run_query` e `run_query`.

**Limites:**
- só leitura (`SELECT`);
- até 1.000 linhas por resposta;
- teto de bytes processados por consulta;
- consultas longas são canceladas após 5 minutos.

---

## 6. Problemas comuns

| Sintoma | Causa provável e solução |
|---|---|
| `401 Unauthorized` / "Failed to connect" | Chave errada, expirada ou revogada. Confira se o valor começa com `Bearer mcpbq_`. Se o erro continuar, peça uma nova chave ao administrador. |
| `ScopeError: Dataset 'x' não está liberado` | A sua chave não inclui esse dataset. Peça a inclusão ao administrador. |
| `Forbidden` / `Access Denied` vindo do BigQuery | Falta permissão IAM para a Service Account no projeto ou no dataset (passo 4). |
| `NotFound` | Nome da tabela ou dataset errado, ou região diferente. Use `list_tables` para conferir. |
| Claude Desktop não mostra o BigQuery | O JSON da configuração está inválido, ou o app não foi fechado pela bandeja. Veja os logs em **Configurações → Desenvolvedor**. |
| `npx` não encontrado | Instale o Node.js e reinicie o computador ou o Claude Desktop. |

## Segurança

- A chave é **pessoal**. Não a compartilhe nem a coloque em repositórios.
- Perdeu a chave ou suspeita de vazamento? Peça a **revogação** ao administrador. O acesso é cortado na hora.
- Para remover do Claude Code: `claude mcp remove bigquery`. No Claude Desktop, apague o bloco `"bigquery"` da configuração.
