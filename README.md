# oscar tools 
Start with
```
set FLASK_APP=app.py
set FLASK_ENV=debug
flask run
```

Deploy to heroku with
```
git push heroku-staging master
git push heroku master

```

Build docker
```
docker build -t oscar-tools .
docker run --rm --name oscar-tools-container  oscar-tools
```
