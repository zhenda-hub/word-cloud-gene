FROM node:latest

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .
# ENTRYPOINT ["sh", "./entrypoint.sh"] 
CMD ["sh", "-c", "npm run dev -- --host 0.0.0.0"] 
# CMD ["sh", "-c", "tail -f /dev/null"] 