# Kubernetes demo deployment

1. Build and push the Docker image to a registry your cluster can pull from.
2. Copy `secret.example.yaml` to `secret.yaml`, set a unique `SECRET_KEY`, and keep the real secret file out of Git.
3. Replace `ghcr.io/OWNER/supplyguard:latest` in `app.yaml` with your image reference and `supplyguard.example.com` with a DNS name routed to your ingress controller.
4. Apply the resources:

   ```bash
   kubectl apply -f infra/kubernetes/namespace.yaml
   kubectl apply -f infra/kubernetes/secret.yaml
   kubectl apply -f infra/kubernetes/app.yaml
   kubectl -n supplyguard rollout status deployment/supplyguard
   kubectl -n supplyguard port-forward service/supplyguard 5050:5050
   ```

5. For local cluster verification, open <http://127.0.0.1:5050/>. For public access, configure DNS and TLS on the ingress controller before exposing the host.

The PVC keeps the optional SQLite scanner data. The browser-only CI/CD and supply network simulations need no persistent backend state. Prometheus scrape annotations expose the app's `/metrics` endpoint to a compatible cluster Prometheus deployment.
