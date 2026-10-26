INSERT OR IGNORE INTO policies(id, name, description, severity, enabled) VALUES
('SG-SECRET-001', 'Credential exposure', 'Detect likely credentials committed in source files.', 'critical', 1),
('SG-DEPS-001', 'Python dependency pinning', 'Flag requirements without an explicit version.', 'medium', 1),
('SG-DEPS-002', 'Wildcard dependency versions', 'Flag JavaScript dependencies set to wildcard or latest.', 'medium', 1),
('SG-DEPS-003', 'Floating dependency ranges', 'Highlight JavaScript dependencies using floating ranges.', 'low', 1),
('SG-LOCK-001', 'Reproducible dependency graph', 'Require a recognized package lock file alongside manifests.', 'medium', 1),
('SG-DOCKER-001', 'Non-root container', 'Flag Dockerfiles without a USER instruction.', 'medium', 1),
('SG-DOCKER-002', 'Pinned container base image', 'Flag Docker base images without an explicit tag.', 'low', 1),
('SG-MANIFEST-001', 'Manifest integrity', 'Validate package.json syntax.', 'low', 1);
