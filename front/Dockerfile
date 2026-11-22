# ── Dockerfile do Frontend (React + Vite) ──
# Multi-stage: build com Node, serve com Nginx.

# ── Stage 1: Build da aplicação ──
FROM node:22-alpine AS builder

WORKDIR /app

# Copia arquivos de dependência primeiro (cache de camadas Docker)
COPY package.json package-lock.json ./

# Instala dependências
RUN npm ci

# Copia o restante do código
COPY . .

# Variável de ambiente para a URL da API em produção.
# Pode ser sobrescrita no docker-compose ou no build.
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

# Build de produção
RUN npm run build

# ── Stage 2: Servir com Nginx ──
FROM nginx:alpine

# Copia o build para o diretório do Nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Configuração customizada do Nginx para SPA (redireciona rotas para index.html)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
