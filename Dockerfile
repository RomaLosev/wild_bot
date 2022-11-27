FROM python:3.11
WORKDIR /app
COPY pyproject.toml/ ./
RUN pip install --upgrade pip && pip --no-cache-dir install poetry
RUN poetry config virtualenvs.create false
COPY ./ .
RUN poetry install
CMD ["python3", "src/bot.py"]