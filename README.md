Parte 04 — CI/CD com GitHub Actions, Docker e AWS (To‑Do List)

Esta pasta contém um exemplo mínimo para a Parte 04 descrita em `TRABALHO_PARTE_04.md` — AGORA AUTOCONTIDA — incluindo aplicação, IaC (Terraform + Ansible) e um modelo de CI/CD:

- Aplicação web de To‑Do (Flask + SQLAlchemy/Postgres) em `app/`.
- `Dockerfile` e `docker-compose.yml` para conteinerização.
- IaC completa em `iac/`: `terraform/` (EC2 + Security Group + RDS) e `ansible/` (inventário dinâmico AWS, playbook e role `docker` para instalar Docker/Compose e implantar a app).
- Gerenciamento de secrets com Ansible Vault via template `iac/ansible/templates/env.j2` e variáveis em `iac/ansible/group_vars/all/vault.yml` (use o arquivo de exemplo `vault.yml.example`).
- Modelo de workflow do GitHub Actions em `.github/workflows/deploy.yml` que faz deploy via SSH em uma EC2 (exemplo didático).
- `.env.example` com as variáveis esperadas para conectar no RDS (não versionar `.env`).

Importante: para o workflow ser executado pelo GitHub, ele deve estar na pasta raiz do repositório em `.github/workflows/`. Nesta prática, o arquivo está aninhado em `parte_04/` apenas como referência; ao ativar, copie-o para a localização correta.

1) Pré‑requisitos

- AWS CLI configurado localmente (ou variáveis `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`).
- Terraform 1.2+ e Ansible 9+ locais OU uso do container dev do projeto raiz (`docker-compose.yml` na raiz tem serviço `iac`).
- Par de chaves SSH existente na conta AWS (veja `variables.tf` → `nome_chave`).

2) Variáveis de ambiente esperadas (.env)

```
DB_HOST=<endpoint do RDS>
DB_NAME=<nome da base>
DB_USER=<usuário>
DB_PASSWORD=<senha>
# Opcional:
SQLALCHEMY_ECHO=false
```

3) Provisionar INFRA com Terraform (dentro desta pasta)

Abra um terminal nesta pasta e execute:

```
cd iac/terraform
terraform init
terraform plan
export TF_VAR_db_password="<senha-postgres>"
terraform apply
```

Ao final, anote:

- `ip_nginx` → IP público da EC2
- `endpoint_postgres` → endpoint do RDS (use no Vault abaixo)

4) Configurar e rodar o Ansible (instala Docker/Compose e implanta a app)

No primeiro uso, instale as coleções necessárias:

```
cd iac/ansible
ansible-galaxy collection install -r collections/requirements.yml
```

Crie o arquivo de secrets do Vault (NÃO versionar):

```
cd iac/ansible/group_vars/all
cp vault.yml.example vault.yml
# Edite os valores (use o endpoint do RDS de `terraform output`)
```

Opcional recomendado — criptografar o `vault.yml`:

```
ansible-vault encrypt group_vars/all/vault.yml
# Para executar pedirá a senha, ou use --vault-password-file
```

Execute o playbook (inventário dinâmico AWS baseado em tags criadas pelo Terraform):

```
cd iac/ansible
export AWS_REGION=us-east-1
ansible-playbook -i aws_ec2.yaml playbook.yml  # adicione --ask-vault-pass se criptografou
```

Ao final, acesse: `http://<ip_nginx>/`.

5) Subir a aplicação manualmente na EC2 (sanidade — alternativo ao Ansible)

```
ssh ubuntu@<ip_nginx>
cd ~/todo-app/parte_04
docker compose build
docker compose up -d
```

6) Workflow do GitHub Actions (deploy automático — exemplo)

O arquivo `parte_04/.github/workflows/deploy.yml` exemplifica um pipeline com:

- `on: push: branches: [ main ]` (gatilho apenas no main);
- `actions/checkout@v4` para obter o código (opcional);
- `appleboy/ssh-action@v1` para conectar na EC2 com `secrets`:
  - `EC2_HOST` (IP/DNS), `EC2_USER` (ex.: `ubuntu`), `EC2_SSH_KEY` (chave privada).

Script de implantação (resumo):

```
cd ~/todo-app/parte_04
git pull
docker compose build
docker compose up -d
docker image prune -f
```

Para ativar de fato, mova o arquivo para `.github/workflows/deploy.yml` na raiz do repo e crie os `Secrets` em Settings → Secrets and variables → Actions. Alternativamente, você pode orquestrar o deploy via Ansible diretamente no pipeline (não incluído aqui para manter o foco no exemplo didático).

7) O que mostrar no vídeo (resumo do enunciado)

- Estrutura IaC dentro de `parte_04/` (Terraform + Ansible) e explicação das mudanças.
- Execução do `terraform apply` e coleta dos outputs (`ip_nginx`, `endpoint_postgres`).
- Execução do `ansible-playbook` instalando Docker/Compose e implantando a aplicação.
- `http://<ip>/app` (raiz) respondendo e persistindo no banco (RDS) — as variáveis vêm do `.env` gerado via Vault.
- Explicação do workflow do Actions e do uso de `secrets` no GitHub.
