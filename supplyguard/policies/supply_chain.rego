package supplyguard

import rego.v1

default decision := "passed"

decision := "blocked" if {
  some finding in input.findings
  finding.severity == "critical"
}

decision := "attention" if {
  not has_critical
  some finding in input.findings
  finding.severity == "high"
}

has_critical if {
  some finding in input.findings
  finding.severity == "critical"
}

deny contains finding if {
  some finding in input.findings
  finding.severity == "critical"
}

warn contains finding if {
  some finding in input.findings
  finding.severity in {"high", "medium"}
}
