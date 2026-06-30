Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script:VibeConsultationCompatibilityBoundary = 'retired_old_routing_compat'

function Invoke-VibeRetiredConsultationCompatibility {
    throw 'Old specialist consultation compatibility is retired. Current runtime uses work_binding plus skill_usage.used / skill_usage.unused.'
}
