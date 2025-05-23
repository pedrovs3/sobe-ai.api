# 📦 sobe-ai.api

**sobe-ai.api** é a API responsável por alimentar a plataforma [Sobe Aí](https://sobe-ai.pedrovs.dev), um serviço simples e gratuito para **upload temporário de imagens e vídeos sem compressão**.

Ideal para quem precisa compartilhar arquivos rapidamente, sem depender de plataformas que apliquem compressão ou guardem seus dados por tempo indeterminado.

---

## ✨ Funcionalidades

* 📤 Upload de múltiplos arquivos simultaneamente
* 🗜 Compactação automática em `.zip` **sem compressão adicional**
* 🔐 Geração de link seguro e temporário para download
* ⏳ Expiração automática dos arquivos em 2 horas
* 🧹 Remoção automática dos arquivos e tokens expirados
* 💾 Armazenamento temporário no Redis
* 🔄 Tarefas agendadas com APScheduler

---

## 🖼️ Sem Perda de Qualidade

> **Nenhum arquivo é comprimido ou modificado internamente.**
> A compactação `.zip` é feita com o método `ZIP_STORED`, o que significa **zero compressão, zero perda de qualidade** — ideal para envio de imagens PNG, JPG, GIF e até vídeos curtos.

---

## 🌐 Landing Page

Confira a interface web do projeto:

📎 **[https://sobe-ai.pedrovs.dev](https://sobe-ai.pedrovs.dev)**

> Envie seus arquivos rapidamente e receba um link temporário para compartilhar.
> Interface minimalista, intuitiva e responsiva — sem login, sem anúncios, sem rastreio.

---

## 🧰 Tecnologias Utilizadas

* **Python 3.11+**
* **FastAPI** (framework da API)
* **Redis** (armazenamento temporário de tokens)
* **APScheduler** (agendamento de exclusão)
* **Docker** (opcional)
* **dotenv** (variáveis de ambiente)

---

## 🚀 Instalação Local

### 1. Pré-requisitos

* Python 3.11+
* Redis em execução

### 2. Clonar o Repositório

```bash
git clone https://github.com/pedrovs3/sobe-ai.api.git
cd sobe-ai.api
```

### 3. Configurar Variáveis

Crie um `.env` baseado em `.env.example`:

```env
REDIS_HOST=redis://localhost:6379/0
```

### 4. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 5. Executar

```bash
uvicorn main:app --reload
```

Acesse a documentação interativa em: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🐳 Executando com Docker

```bash
docker build -t sobe-ai-api .
docker run -d -p 8000:8000 --env-file .env sobe-ai-api
```

---

## 📂 Endpoints

### `POST /upload/`

Faz upload de múltiplos arquivos e retorna um link temporário.

**Exemplo de resposta:**

```json
{
  "message": "Arquivo enviado com sucesso!",
  "download_link": "https://sobe-ai.pedrovs.dev/download/abc123def456"
}
```

### `GET /download/{token}`

Faz o download do `.zip` enquanto o token ainda estiver válido.

---

## 🔒 Segurança & Expiração

* Tokens são truncados de um hash SHA-256 (16 caracteres)
* Expiração automática após 2h
* Exclusão garantida via Redis + APScheduler

---

## 📁 Estrutura

```
uploads/  → arquivos temporários
zips/     → arquivos zipados
.env      → configuração do Redis
main.py   → código principal da API
```

---

## 📜 Licença

Distribuído sob licença MIT.
