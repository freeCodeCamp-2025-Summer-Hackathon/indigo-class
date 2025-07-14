FROM python:3.13.5

WORKDIR /app

RUN pip install uv

COPY . .

CMD ["/bin/bash", "-c", "uv sync && uv run main.py"]

EXPOSE 8000
