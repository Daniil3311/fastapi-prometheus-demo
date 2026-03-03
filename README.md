# FastAPI Prometheus Demo

Демо backend-сервиса с полным локальным observability-стеком:
- FastAPI + SQLAlchemy + PostgreSQL
- Prometheus + custom metrics + alert rules
- Node Exporter для системных метрик
- Loki + Promtail для логов
- Grafana с provisioning и готовым dashboard JSON
- Pytest (юнит и интеграционный тест для `/metrics`)

## Что реализовано

### API
- `GET /health` -> `{"status": "healthy"}`
- `GET /message/{id}` -> чтение сообщения из PostgreSQL
- `POST /process` -> обработка payload c задержкой ~0.5s, echo-ответ
- `GET /metrics` -> метрики Prometheus

### Валидация и безопасность
- Валидация входных данных через Pydantic (`min_length`, `max_length`, strip whitespace)
- Ограничение `id` в path (`ge=1`, `le=1_000_000`)
- Контейнер приложения запускается от non-root пользователя

### Логи
- Структурированные JSON-логи (`python-json-logger`)
- Логи пишутся в stdout и в файл `/var/log/app/app.log`
- Promtail читает файл и отправляет в Loki

### Метрики
Кастомные:
- `app_requests_total{endpoint,method,status}`
- `app_request_latency_seconds_bucket` (Histogram)
- `app_errors_total`
- `app_warnings_total`

Автоматические (Instrumentator):
- стандартные HTTP/latency метрики FastAPI

### Seed данных
При старте приложения автоматически создается таблица `messages` и заполняется минимум 10 mock-записями (`id=1..10`).

## Запуск локально

Требования: Docker + Docker Compose

```bash
docker compose up --build
```

Сервисы:
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (`admin/admin`)
- Loki: http://localhost:3100

## Тесты

```bash
pip install -r requirements.txt
pytest -q
```

## Grafana Dashboard

Dashboard provisioned из файла:
- `grafana/dashboards/fastapi-observability.json`

Панели:
- Requests/sec
- Latency p95
- CPU usage
- Memory usage
- Errors/sec
- Warnings/sec
- Application logs (Loki)

## Bottleneck (симуляция)

В `/process` добавлена симуляция медленной обработки: если `data` содержит `slow`, задержка увеличивается до ~1.2s.

Пример запроса:
```bash
curl -X POST http://localhost:8000/process -H "Content-Type: application/json" -d '{"data":"slow request"}'
```

Как выявить bottleneck в Grafana:
- `histogram_quantile(0.95, sum(rate(app_request_latency_seconds_bucket[5m])) by (le))`
- `sum(rate(app_warnings_total[5m]))`
- логи Loki: `{job="fastapi-app"} |= "slow_processing"`

## Alert rule

Prometheus rule (`prometheus/alerts.yml`):
- `HighLatencyP95`: p95 latency > 1s в течение 2 минут.

## Trade-offs

- Для простоты используется sync SQLAlchemy и автосоздание схемы на старте, без Alembic.
- Логи собираются из файла через общий volume (просто для локального стенда).
- Node Exporter в docker-compose дает метрики узла/контейнера для лабораторного мониторинга; для production обычно нужны дополнительные ограничения и отдельный deployment.

