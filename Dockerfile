FROM ubuntu:latest

WORKDIR /project/tasks


LABEL authors="Heinz Preisig"
WORKDIR /project/tasks
COPY . /project
COPY tasks /project/tasks
COPY packages /project/packages



CMD ["python", "/project/tasks/run.py"]

EXPOSE 8000

