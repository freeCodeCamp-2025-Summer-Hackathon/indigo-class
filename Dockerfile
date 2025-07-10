FROM python:3.13.5

WORKDIR /app

RUN pip install uv

COPY . .

CMD ["/bin/bash", "-c", "cp .env.example .env && uv sync && uv run main.py"]

EXPOSE 8000
