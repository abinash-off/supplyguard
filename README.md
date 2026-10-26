# supplyguard
Open:

    App: http://127.0.0.1:5050/
    Prometheus: http://127.0.0.1:9090/
    Grafana: http://127.0.0.1:3000/ (local demo login admin / supplyguard-demo, change via GRAFANA_PASSWORD)

Grafana provisions the SupplyGuard Prometheus datasource and dashboard automatically. To follow service logs use docker compose logs -f supplyguard; stop the stack with docker compose down. Use PORT, PROMETHEUS_PORT, or GRAFANA_PORT to select different host ports. The frontend is also runnable without Docker using the Python steps above; Prometheus/Grafana are available in the Compose stack.
