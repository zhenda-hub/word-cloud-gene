FROM python:3.11-slim

WORKDIR /app

# 安装中文字体
RUN apt-get update && \
    apt-get install -y fonts-wqy-microhei && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
# ENTRYPOINT ["sh", "./entrypoint.sh"] 
CMD ["sh", "-c", "tail -f /dev/null"] 