Build
docker build -t climbbot:latest .


Run
docker run -i climbbot

Run an interactive terminal
docker run -it --entrypoint /bin/bash climbbot


Run a one-liner
 - docker run -it --rm --name hellopython --mount type=bind,source=${PWD},destination=/usr/src/myapp -w /usr/src/myapp python:3 "mkdir test"
 - docker run -it --rm --name hellopython --mount type=bind,source=${PWD},destination=/usr/src/myapp -w /usr/src/myapp python:3 python -c "print('hello')"


