FROM node:15 as env
RUN npm set strict-ssl false
RUN npm install -g node-sass@5

#Ветка для сборки
FROM env as PROD_build
RUN yarn config set "strict-ssl" false
WORKDIR /opt/src
COPY . .
RUN yarn install
RUN yarn run build

##Ветка для запуска
FROM nginx:1.19-alpine as PROD
COPY --from=PROD_build /opt/src/build /usr/share/nginx/html
#COPY ./nginx.conf.template /nginx.conf.template
COPY config/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
#CMD ["/bin/sh" , "-c" ,"envsubst < /nginx.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
CMD ["nginx", "-g", "daemon off;"]

#Ветка для дева
FROM env as DEV
RUN yarn config set "strict-ssl" false
RUN mkdir /opt/src-dev
WORKDIR /opt/src-dev
COPY . .
RUN yarn install
CMD ["yarn", "dev"]
EXPOSE 3000




