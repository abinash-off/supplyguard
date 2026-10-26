# supplyguard

### 🚀 Local Access & Dashboards

Once the application is up and running, you can access the services using the links below:

* **Web Application:** [http://127.0.0.1:5050/](http://127.0.0.1:5050/)
* **Prometheus Dashboard:** [http://127.0.0.1:9090/](http://127.0.0.1:9090/)
* **Grafana Metrics:** [http://127.0.0.1:3000/](http://127.0.0.1:3000/)
  * **Username:** `admin`
  * **Password:** `supplyguard-demo` *(Note: You can customize this by updating the `GRAFANA_PASSWORD` environment variable)*


Grafana provisions the SupplyGuard Prometheus datasource and dashboard automatically. To follow service logs use docker compose logs -f supplyguard; stop the stack with docker compose down. Use PORT, PROMETHEUS_PORT, or GRAFANA_PORT to select different host ports. The frontend is also runnable without Docker using the Python steps above; Prometheus/Grafana are available in the Compose stack.
