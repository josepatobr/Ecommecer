FROM python:3.8-slim

WORKDIR /app

RUN pip install --upgrade pip \
    && pip install uv

COPY pyproject.toml uv.lock /app/

RUN uv sync

COPY . /app

EXPOSE 8000


ENV PATH="/app/.venv/bin:$PATH"
CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
