# MCP BigQuery: guia do cliente

Conecte o seu Claude ao **Google BigQuery** para consultar seus dados conversando, em modo **somente leitura**.

Você **não instala servidor, Python nem credenciais do Google**. O administrador da CLI Consultoria envia duas informações, e você as configura no seu Claude:

| Você recebe | Valor |
|---|---|
| **URL do servidor** | `https://mcp-bigquery.tsk4ad.easypanel.host/mcp` |
| **Chave de API** (pessoal, intransferível) | `mcpbq_1a2b3c4d_...` |

A chave já define **qual BigQuery** você acessa (o da CLI ou o da sua empresa) e **quais datasets** (o projeto inteiro ou só alguns).

O mesmo servidor atende vários clientes, mas cada um tem acesso **isolado**: a sua chave só alcança o seu BigQuery, e nenhum outro cliente enxerga os seus dados.

## Escolha o seu cenário

| Você usa | Siga | O que precisa instalar |
|---|---|---|
| **Claude Desktop** (app de chat), **plano grátis** | [Cenário 1](#2-cenário-1-claude-desktop-plano-grátis) | Claude Desktop + Node.js |
| **Claude Code**, **plano Pro** | [Cenário 2](#3-cenário-2-claude-code-plano-pro) | Claude Code |

A mesma chave funciona nos dois cenários, e em todos os seus computadores.

---

## 1. Antes de começar: o que pedir ao administrador

Envie ao administrador:

- **Quem vai usar:** nome e e-mail de cada pessoa. Cada pessoa recebe a própria chave.
- **Qual BigQuery:**
    - **o da CLI**: só informe quais dados precisa acessar;
    - **o da sua empresa**: siga antes o [passo 4](#4-usando-o-bigquery-da-sua-empresa) e informe o **ID do projeto** GCP.
- **Escopo:** o **projeto inteiro** ou só os **datasets** (liste os nomes).
- **Validade** desejada (opcional), por exemplo 30 dias para um consultor. A validade é contada a partir da criação da chave: 1 dia = 24 horas.

Você recebe de volta a **URL** e a **chave**. Guarde a chave como uma senha.

---

## 2. Cenário 1: Claude Desktop (plano grátis)

O Claude Desktop se conecta ao servidor por meio de uma pequena ponte, o `mcp-remote`, que roda no seu computador com o Node.js.

### Requisitos

- **Claude Desktop** instalado, com login na sua conta (o plano grátis serve).
- **[Node.js](https://nodejs.org)**, versão **LTS** (a recomendada no site). Depois de instalar, **reinicie o computador**, para o Claude Desktop encontrar o `npx`.
- **Internet liberada para o npm.** Na primeira vez, o `npx` baixa automaticamente o `mcp-remote`.

### Passo a passo

1. No Claude Desktop, abra **Configurações → Desenvolvedor → Editar configuração**. Isso mostra o arquivo `claude_desktop_config.json`. Abra-o num editor de texto (ex.: Bloco de Notas).

    Se não encontrar essa opção, abra o arquivo direto:

    | Sistema | Caminho do arquivo |
    |---|---|
    | Windows (instalador do site) | `%APPDATA%\Claude\claude_desktop_config.json` |
    | Windows (Microsoft Store) | `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json` |
    | macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |

    No Windows, cole o caminho na barra de endereço do Explorador de Arquivos. Se o arquivo não existir, crie-o com esse nome.

2. Adicione o bloco abaixo, trocando `mcpbq_SUA_CHAVE` pela chave que você recebeu (a URL já está certa). Mantenha a palavra `Bearer` e o espaço antes da chave. Se o arquivo já tiver um `"mcpServers"`, inclua só o item `"bigquery"` dentro dele, separado dos outros por vírgula.

    ```json
    {
      "mcpServers": {
        "bigquery": {
          "command": "npx",
          "args": ["-y", "mcp-remote", "https://mcp-bigquery.tsk4ad.easypanel.host/mcp", "--header", "Authorization:${MCP_BIGQUERY_AUTH}"],
          "env": { "MCP_BIGQUERY_AUTH": "Bearer mcpbq_SUA_CHAVE" }
        }
      }
    }
    ```

    > A chave fica no `env`, e não direto nos `args`, porque no Windows espaços dentro dos argumentos quebram o cabeçalho.

3. Salve o arquivo. **Feche o Claude Desktop por completo**: no Windows, clique com o botão direito no ícone da bandeja do sistema (perto do relógio) e escolha **Sair**; fechar só a janela não basta. Depois, abra o app de novo.

4. **Teste:** numa conversa nova, pergunte **"Quais datasets eu tenho no BigQuery?"**. Na primeira vez, o Claude pede autorização para usar a ferramenta do BigQuery: permita. A resposta deve listar os datasets liberados para a sua chave.

    Se não funcionar, veja **Configurações → Desenvolvedor** (o `bigquery` deve aparecer como em execução) e os [problemas comuns do Claude Desktop](#claude-desktop).

### Alternativa sem Node.js: conector personalizado

Só funciona se a sua conta tiver o recurso de cabeçalhos, que a Anthropic está liberando aos poucos e que geralmente **ainda não aparece no plano grátis**:

1. Abra **Configurações → Conectores → Adicionar conector personalizado** e informe a URL.
2. Se aparecer a seção **"Request headers"** ("Cabeçalhos de requisição"):
    1. escolha **No sign-in**;
    2. adicione o cabeçalho `authorization` com o valor `Bearer mcpbq_SUA_CHAVE`.
3. Se essa seção **não** aparecer, use o passo a passo acima. O login por OAuth está no roadmap do servidor e vai dispensar o `mcp-remote`.

O plano grátis permite **um** conector personalizado.

---

## 3. Cenário 2: Claude Code (plano Pro)

O Claude Code se conecta direto ao servidor, sem ponte e sem Node.js.

### Requisitos

- **[Claude Code](https://code.claude.com/docs)** instalado e com login na sua conta **Pro**.

### Passo a passo

1. Num terminal (PowerShell, CMD, bash ou zsh), rode o comando abaixo, trocando `mcpbq_SUA_CHAVE` pela chave que você recebeu (a URL já está certa):

    ```bash
    claude mcp add --transport http --scope user bigquery https://mcp-bigquery.tsk4ad.easypanel.host/mcp --header "Authorization: Bearer mcpbq_SUA_CHAVE"
    ```

    - `--scope user` deixa o BigQuery disponível em todos os seus projetos. Para usar só na pasta atual, troque por `--scope local`.
    - **Já tem outro servidor MCP chamado `bigquery`** (por exemplo, uma instalação local antiga)? Use outro nome, como `bigquery-remoto`, no lugar de `bigquery` no comando. Se os nomes forem iguais, a configuração de uma pasta específica (escopo `local`) tem prioridade sobre a de `--scope user`, e o Claude Code pode acabar usando o servidor antigo.

2. **Confira a conexão:**

    ```bash
    claude mcp list
    ```

    O `bigquery` deve aparecer com **✓ Connected**. Para ver os detalhes, rode `claude mcp get bigquery`: deve mostrar o tipo **http** e a URL do servidor.

3. **Teste:** abra o Claude Code (`claude`) e pergunte **"Quais datasets eu tenho no BigQuery?"**. Na primeira vez, autorize o uso da ferramenta. Dentro do Claude Code, o comando `/mcp` mostra o servidor e as ferramentas.

    Se não funcionar, veja os [problemas comuns do Claude Code](#claude-code).

### Alternativa: chave em variável de ambiente (sem gravá-la em arquivo)

Útil para não deixar a chave escrita na configuração do Claude Code.

1. Crie a variável `MCP_BIGQUERY_KEY` com a sua chave.

    Windows (PowerShell):

    ```powershell
    setx MCP_BIGQUERY_KEY "mcpbq_SUA_CHAVE"
    ```

    macOS/Linux:

    ```bash
    echo 'export MCP_BIGQUERY_KEY="mcpbq_SUA_CHAVE"' >> ~/.zshrc
    ```

2. Crie o arquivo `.mcp.json` na pasta do projeto:

    ```json
    {
      "mcpServers": {
        "bigquery": {
          "type": "http",
          "url": "https://mcp-bigquery.tsk4ad.easypanel.host/mcp",
          "headers": { "Authorization": "Bearer ${MCP_BIGQUERY_KEY}" }
        }
      }
    }
    ```

3. Abra um terminal novo, para a variável valer, e rode o Claude Code nessa pasta.

---

## 4. Usando o BigQuery da sua empresa

Pule este passo se você vai consultar dados que já estão no BigQuery da CLI. Vale para os dois cenários.

### Opção 1 (recomendada): conceder acesso à Service Account da CLI

Nenhuma chave privada da sua empresa sai do seu ambiente, e você pode revogar o acesso quando quiser.

O administrador cria uma Service Account **exclusiva para a sua empresa** e informa o e-mail dela (`<sa-da-cli>@...iam.gserviceaccount.com`). Ela não é compartilhada com nenhum outro cliente, e os dados da sua empresa só são lidos com ela.

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

Converse normalmente, nos dois cenários. Exemplos:

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

### Claude Desktop

| Sintoma | Causa provável e solução |
|---|---|
| O BigQuery não aparece | O JSON da configuração está inválido (vírgula ou chave `}` faltando), ou o app não foi fechado pela bandeja. Confira o arquivo num validador de JSON e veja os logs (linha abaixo). |
| Onde ficam os logs | Windows: `%APPDATA%\Claude\logs\mcp-server-bigquery.log`. macOS: `~/Library/Logs/Claude/mcp-server-bigquery.log`. Também em **Configurações → Desenvolvedor**. |
| `spawn npx ENOENT` ou `npx` não encontrado | O Node.js não está instalado, ou o computador não foi reiniciado depois da instalação. Se continuar no Windows, troque `"command": "npx"` por `"command": "C:\\Program Files\\nodejs\\npx.cmd"` (com as barras duplas). |
| Erro de rede ao baixar o `mcp-remote` | A rede bloqueia o npm (comum em redes corporativas com proxy). Teste em outra rede ou peça à sua TI a liberação de `registry.npmjs.org`. |
| O navegador abre pedindo autorização (OAuth) | A chave não chegou ao servidor. Confira o `env` (`"Bearer mcpbq_..."`) e o `--header` (`"Authorization:${MCP_BIGQUERY_AUTH}"`), exatamente como no passo 2. |

### Claude Code

| Sintoma | Causa provável e solução |
|---|---|
| `claude mcp list` mostra falha na conexão do `bigquery` | Chave ou URL erradas. Remova com `claude mcp remove bigquery` e adicione de novo (passo 1), conferindo `Bearer mcpbq_...` e o `/mcp` no fim da URL. |
| `claude` não é reconhecido como comando | O Claude Code não está instalado, ou o terminal foi aberto antes da instalação. Abra um terminal novo. |
| Com `.mcp.json`, o BigQuery não conecta | A variável `MCP_BIGQUERY_KEY` não está definida no terminal atual. Abra um terminal novo depois do `setx` e rode o Claude Code na pasta do `.mcp.json`. |

### Nos dois cenários

| Sintoma | Causa provável e solução |
|---|---|
| `401 Unauthorized` / "Failed to connect" | Chave errada, expirada ou revogada. Se o erro continuar depois de conferir a chave, peça uma nova ao administrador. |
| `ScopeError: Dataset 'x' não está liberado` | A sua chave não inclui esse dataset. Peça a inclusão ao administrador. |
| `Forbidden` / `Access Denied` vindo do BigQuery | Falta permissão IAM para a Service Account no projeto ou no dataset (passo 4). |
| `NotFound` | Nome da tabela ou dataset errado, ou região diferente. Use `list_tables` para conferir. |

## Segurança

- A chave é **pessoal**. Você pode usá-la em todos os seus computadores, no Claude Code e no Claude Desktop, mas não a compartilhe com outras pessoas nem a coloque em repositórios.
- Perdeu a chave ou suspeita de vazamento? Peça a **revogação** ao administrador. O acesso é cortado na hora.
- Para remover:
    - **Claude Desktop:** apague o bloco `"bigquery"` da configuração e reinicie o app;
    - **Claude Code:** `claude mcp remove bigquery`.
