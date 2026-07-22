FROM node:20-alpine
WORKDIR /app
COPY package.json server.js ./
COPY public ./public
RUN npm install --omit=dev 2>/dev/null || true
ENV PORT=3000
ENV PASSCODE=
ENV DATA_DIR=/data
VOLUME /data
EXPOSE 3000
# 数据持久化：把 DATA_DIR(/data) 挂载到持久盘，否则重启会重置
CMD ["node", "server.js"]
