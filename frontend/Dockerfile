# Etap build - instalacja zależności i budowa
FROM node:18-alpine AS build

# Ustaw katalog roboczy
WORKDIR /app

# Skopiuj pliki package*.json z podfolderu absurdly-correct do /app
COPY absurdly-correct/package*.json ./

# Instalacja zależności
RUN npm install

# Skopiuj resztę kodu z absurdly-correct
COPY absurdly-correct/ ./

# Budowanie aplikacji
# Jeśli używasz Create React App, powstaje folder build
# Jeśli używasz Vite, powstaje folder dist
RUN npm run build

# Etap produkcyjny - serwujemy pliki przez Nginx
FROM nginx:alpine

# Skopiuj z poprzedniego etapu (build) pliki do /usr/share/nginx/html
# Jeśli to CRA -> build, jeśli Vite -> dist
COPY --from=build /app/dist /usr/share/nginx/html

# Otwórz port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
