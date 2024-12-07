FROM node:latest

WORKDIR /app

COPY package.json .

COPY . .
ENTRYPOINT ["sh", "./entrypoint.sh"] 
CMD ["tail", "-f", "/dev/null"] 