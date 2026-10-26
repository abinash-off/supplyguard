output "application_url" {
  description = "Public URL for the SupplyGuard web dashboard."
  value       = "${var.certificate_arn == "" ? "http" : "https"}://${aws_lb.app.dns_name}"
}

output "ecr_repository_url" {
  description = "Immutable image repository for the GitHub Actions deployment workflow."
  value       = aws_ecr_repository.app.repository_url
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.app.name
}

output "ecs_service_name" {
  value = aws_ecs_service.app.name
}

output "efs_file_system_id" {
  description = "Encrypted persistent filesystem mounted at /data for SQLite scanner state."
  value       = aws_efs_file_system.app.id
}
