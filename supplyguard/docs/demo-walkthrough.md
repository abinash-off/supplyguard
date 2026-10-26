# SupplyGuard demo walkthrough

Target length: 2–3 minutes. For the browser-only dashboard, open <https://supplyguard-cloud-simulator.vercel.app/>. To show the local API and monitoring services too, run `docker compose up --build -d` and open `http://127.0.0.1:5050/`.

1. **Overview (15 seconds):** introduce the three connected controls: software delivery, operational health, and supply-chain risk. Point out the digital supply-network summary.
2. **CI/CD simulator (35 seconds):** choose “Successful deployment”, run the pipeline, and show the stage timeline, logs, commit, build, and deployment summary. Mention all services are simulated.
3. **Security scenario (25 seconds):** select “Supply-chain attack”, run it, and show the provenance/security gate blocking the release with a root cause and remediation.
4. **Supply network (40 seconds):** open “Supply Network Simulator”. Trigger a shipment delay, then a stock shortage. Show the affected shipment ETA, inventory reorder alert, supplier panel, and event stream. Trigger a replenishment to show recovery.
5. **DevOps and monitoring (25 seconds):** simulate an infrastructure incident and show production health, latency/error changes, and the active alert.
6. **Cloud operations (15 seconds):** show Cloud Architecture, then note local Grafana/Prometheus and optional AWS/Kubernetes deployment files.

Close by stating the browser simulations need no cloud credentials. For the full stack, local Grafana and Prometheus need Docker; real AWS deployment needs an AWS account. For recording, use screen recording software of choice and note that the public Vercel URL hosts the frontend simulator; scanner API access is local-only.
