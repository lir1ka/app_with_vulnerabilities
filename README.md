# app_with_vulnerabilities

## Инструкция по сборке и запуску приложения

Для сборки и запуска приложения выполните следующие команды:

```bash
docker build -t app_with_vulns .
docker run -p 5000:5000 app_with_vulns
