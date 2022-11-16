FROM python:3.7
WORKDIR /usr/src/personalised_nudges
COPY ./app ./app
# COPY requirements.txt requirements.txt
COPY pyproject.toml pyproject.toml
# RUN pip3 install -r requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry add fastapi uvicorn SQLAlchemy pydantic psycopg2-binary passlib   
# RUN poetry install --no-interaction --no-ansi -vvv


#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]