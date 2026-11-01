# The web app, built into plain files and served by the gateway's nginx.
# Stage 1 needs Node to build; stage 2 is only nginx and the built files, so no Node in the image that runs.
FROM node:22.23.4-alpine3.24 AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npx ng build

FROM nginx:1.30.6-alpine3.24
COPY --from=build /app/dist/taskboard-web/browser /usr/share/nginx/html
