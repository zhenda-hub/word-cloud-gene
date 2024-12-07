#!/bin/sh

# 启动开发服务器
npm run dev -- --host 0.0.0.0
exec "$@"
