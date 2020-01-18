FROM nginx
COPY nginx.conf /etc/nginx/nginx.conf
COPY server.company.com.crt /etc/nginx/server.company.com.crt
COPY server.company.com.key /etc/nginx/server.company.com.key
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

## Launch the wait tool and then your application
CMD /wait && nginx -g "daemon off;"


