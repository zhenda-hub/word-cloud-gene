FROM node:latest

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .
ENTRYPOINT ["sh", "./entrypoint.sh"] 
CMD ["tail", "-f", "/dev/null"] 