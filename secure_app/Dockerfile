FROM chaberb/uwsgi-flask
RUN pip install --upgrade pip
RUN pip install redis
RUN pip install requests
RUN pip install pyjwt
RUN pip install pymongo
RUN pip install Flask-PyMongo
RUN pip install py-bcrypt
RUN pip install dateutils
## THE LIFE SAVER
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

## Launch the wait tool and then your application
CMD /wait && uwsgi --ini uwsgi.ini

