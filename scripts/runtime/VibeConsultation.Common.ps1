Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script:VibeConsultationCompatibilityBoundary = 'retired_old_routing_compat'

function Invoke-VibeRetiredConsultationCompatibility {
    throw 'Old specialist consultation compatibility is retired. Current runtime uses work_binding as bounded-work truth, keeps skill_routing.selected only as an optional compatibility mirror when present, and records execution evidence in skill_usage.'
}
