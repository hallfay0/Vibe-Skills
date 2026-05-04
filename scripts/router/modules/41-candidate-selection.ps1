# Auto-extracted router module. Keep function bodies behavior-identical.

function Get-PackSkillCandidates {
    param(
        [object]$Pack
    )

    if (-not $Pack) { return @() }

    if (-not ($Pack.PSObject.Properties.Name -contains 'skill_candidates')) {
        return @()
    }

    $directCandidates = @($Pack.skill_candidates | ForEach-Object { ([string]$_).Trim() } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    return @($directCandidates | Select-Object -Unique)
}

function ConvertTo-PublicCandidateRanking {
    param([AllowNull()] [object[]]$Rows = @())

    $publicRows = @()
    foreach ($row in @($Rows)) {
        if ($null -eq $row) {
            continue
        }
        $public = [ordered]@{}
        foreach ($property in @($row.PSObject.Properties)) {
            if ($property.Name -in @('_candidate_usable')) {
                continue
            }
            $public[$property.Name] = $property.Value
        }
        $publicRows += [pscustomobject]$public
    }
    return @($publicRows)
}

function Test-CandidateUsable {
    param([AllowNull()] [object]$Row)

    if ($null -eq $Row) {
        return $false
    }
    if ($Row.PSObject.Properties.Name -contains '_candidate_usable') {
        return [bool]$Row._candidate_usable
    }
    return $true
}

function New-RequestedSkillSelection {
    param(
        [string]$RequestedCandidate,
        [object[]]$BlockedByTask
    )

    return [pscustomobject]@{
        selected = $RequestedCandidate
        score = 1.0
        reason = "requested_skill"
        ranking = @(ConvertTo-PublicCandidateRanking -Rows @(
            [pscustomobject]@{
                skill = $RequestedCandidate
                score = 1.0
                keyword_score = 1.0
                name_score = 1.0
                positive_score = 1.0
                negative_score = 0.0
                canonical_for_task_hit = 1.0
                _candidate_usable = $true
            }
        ))
        top1_top2_gap = 1.0
        filtered_out_by_task = @($BlockedByTask)
        _selection_usable = $true
        relevance_score = 1.0
    }
}

function Select-PackCandidate {
    param(
        [string]$PromptLower,
        [string[]]$Candidates,
        [string]$TaskType,
        [string]$RequestedCanonical,
        [object]$SkillKeywordIndex,
        [object]$RoutingRules,
        [object]$Pack,
        [object]$CandidateSelectionConfig
    )

    if (-not $Candidates -or $Candidates.Count -eq 0) {
        return [pscustomobject]@{
            selected = $null
            score = 0.0
            reason = "no_candidates"
            ranking = @()
            top1_top2_gap = 0.0
            filtered_out_by_task = @()
        }
    }

    $requestedCandidate = if ($RequestedCanonical -and ($Candidates -contains $RequestedCanonical)) { [string]$RequestedCanonical } else { $null }

    $weightKeyword = 0.8
    $weightName = 0.2
    $fallbackMin = 0.2
    if ($SkillKeywordIndex -and $SkillKeywordIndex.selection -and $SkillKeywordIndex.selection.weights) {
        if ($SkillKeywordIndex.selection.weights.keyword_match -ne $null) {
            $weightKeyword = [double]$SkillKeywordIndex.selection.weights.keyword_match
        }
        if ($SkillKeywordIndex.selection.weights.name_match -ne $null) {
            $weightName = [double]$SkillKeywordIndex.selection.weights.name_match
        }
    }
    if ($SkillKeywordIndex -and $SkillKeywordIndex.selection -and $SkillKeywordIndex.selection.fallback_to_first_when_score_below -ne $null) {
        $fallbackMin = [double]$SkillKeywordIndex.selection.fallback_to_first_when_score_below
    }

    $positiveBonus = 0.2
    $negativePenalty = 0.25
    $canonicalBonus = 0.12
    if ($CandidateSelectionConfig) {
        if ($CandidateSelectionConfig.rule_positive_keyword_bonus -ne $null) {
            $positiveBonus = [double]$CandidateSelectionConfig.rule_positive_keyword_bonus
        }
        if ($CandidateSelectionConfig.rule_negative_keyword_penalty -ne $null) {
            $negativePenalty = [double]$CandidateSelectionConfig.rule_negative_keyword_penalty
        }
        if ($CandidateSelectionConfig.canonical_for_task_bonus -ne $null) {
            $canonicalBonus = [double]$CandidateSelectionConfig.canonical_for_task_bonus
        }
    }

    $filteredCandidates = @()
    $blockedByTask = @()
    foreach ($candidate in $Candidates) {
        $rule = Get-RoutingRuleForCandidate -Candidate $candidate -RoutingRules $RoutingRules
        if (Test-RuleTaskAllowed -Rule $rule -TaskType $TaskType) {
            $filteredCandidates += $candidate
        } else {
            $blockedByTask += $candidate
        }
    }

    $defaultCandidate = Get-PackDefaultCandidate -Pack $Pack -TaskType $TaskType -PreferredCandidates $filteredCandidates -AllCandidates $Candidates

    if ($filteredCandidates.Count -eq 0) {
        if ($requestedCandidate) {
            return New-RequestedSkillSelection -RequestedCandidate $requestedCandidate -BlockedByTask @($blockedByTask)
        }
        if ($defaultCandidate) {
            return [pscustomobject]@{
                selected = $defaultCandidate
                score = 0.0
                reason = "fallback_task_default_after_task_filter"
                ranking = @()
                top1_top2_gap = 0.0
                filtered_out_by_task = @($blockedByTask)
                _selection_usable = $true
                relevance_score = 0.0
            }
        }

        return [pscustomobject]@{
            selected = $Candidates[0]
            score = 0.0
            reason = "fallback_first_candidate_after_task_filter"
            ranking = @()
            top1_top2_gap = 0.0
            filtered_out_by_task = @($blockedByTask)
            _selection_usable = $true
            relevance_score = 0.0
        }
    }

    $defaultCandidate = Get-PackDefaultCandidate -Pack $Pack -TaskType $TaskType -PreferredCandidates $filteredCandidates -AllCandidates $Candidates

    $scored = @()
    for ($i = 0; $i -lt $filteredCandidates.Count; $i++) {
        $candidate = [string]$filteredCandidates[$i]
        $rule = Get-RoutingRuleForCandidate -Candidate $candidate -RoutingRules $RoutingRules

        $keywordScore = Get-SkillKeywordScore -PromptLower $PromptLower -Candidate $candidate -SkillKeywordIndex $SkillKeywordIndex
        $nameScore = Get-CandidateNameMatchScore -PromptLower $PromptLower -Candidate $candidate

        $positiveScore = 0.0
        $negativeScore = 0.0
        $equivalentGroup = $null
        if ($rule) {
            $positiveScore = Get-KeywordRatio -PromptLower $PromptLower -Keywords @($rule.positive_keywords)
            $negativeScore = Get-KeywordRatio -PromptLower $PromptLower -Keywords @($rule.negative_keywords)
            if ($rule.equivalent_group) {
                $equivalentGroup = [string]$rule.equivalent_group
            }
        }

        $canonicalHit = Get-CanonicalForTaskHit -Rule $rule -TaskType $TaskType
        $useEligible = $true
        $requiresPositiveKeywordMatch = $false
        if ($rule -and ($rule.PSObject.Properties.Name -contains 'requires_positive_keyword_match')) {
            $requiresPositiveKeywordMatch = [bool]$rule.requires_positive_keyword_match
        }
        if ($useEligible -and $requiresPositiveKeywordMatch -and ([double]$positiveScore -le 0.0)) {
            $useEligible = $false
        }

        $score =
            ($weightKeyword * $keywordScore) +
            ($weightName * $nameScore) +
            ($positiveBonus * $positiveScore) -
            ($negativePenalty * $negativeScore) +
            ($canonicalBonus * $canonicalHit)

        $score = [Math]::Max(0.0, [Math]::Min(1.0, $score))

        $scored += [pscustomobject]@{
            skill = $candidate
            score = [Math]::Round($score, 4)
            keyword_score = [Math]::Round($keywordScore, 4)
            name_score = [Math]::Round($nameScore, 4)
            positive_score = [Math]::Round($positiveScore, 4)
            negative_score = [Math]::Round($negativeScore, 4)
            canonical_for_task_hit = [Math]::Round($canonicalHit, 4)
            _candidate_usable = [bool]$useEligible
            requires_positive_keyword_match = [bool]$requiresPositiveKeywordMatch
            equivalent_group = $equivalentGroup
            ordinal = $i
        }
    }

    $ranked = $scored | Sort-Object -Property @(
        @{ Expression = "score"; Descending = $true },
        @{ Expression = "keyword_score"; Descending = $true },
        @{ Expression = "positive_score"; Descending = $true },
        @{ Expression = "ordinal"; Descending = $false }
    )
    $overallTop = $ranked | Select-Object -First 1
    $usableRanked = @($ranked | Where-Object { Test-CandidateUsable -Row $_ })

    if ($requestedCandidate) {
        return New-RequestedSkillSelection -RequestedCandidate $requestedCandidate -BlockedByTask @($blockedByTask)
    }

    $top = $usableRanked | Select-Object -First 1
    if (-not $top) {
        return [pscustomobject]@{
            selected = $null
            score = 0.0
            reason = "no_usable_candidate"
            ranking = @()
            top1_top2_gap = 0.0
            filtered_out_by_task = @($blockedByTask)
            _selection_usable = $false
            relevance_score = if ($overallTop) { [double]$overallTop.score } else { 0.0 }
        }
    }

    $second = $usableRanked | Select-Object -Skip 1 -First 1
    $gap = if ($second) { [double]$top.score - [double]$second.score } else { [double]$top.score }
    $gap = [Math]::Max(0.0, [Math]::Round($gap, 4))

    if ([double]$top.score -lt $fallbackMin) {
        $defaultInRank = if ($defaultCandidate) { $usableRanked | Where-Object { $_.skill -eq $defaultCandidate } | Select-Object -First 1 } else { $null }
        $fallback = if ($defaultInRank) { $defaultCandidate } else { [string]$top.skill }
        $defaultScore = if ($defaultInRank) { [double]$defaultInRank.score } else { [double]$top.score }
        return [pscustomobject]@{
            selected = $fallback
            score = $defaultScore
            reason = if ($defaultInRank) { "fallback_task_default" } else { "fallback_first_candidate" }
            ranking = @(ConvertTo-PublicCandidateRanking -Rows @($usableRanked | Select-Object -First 6))
            top1_top2_gap = $gap
            filtered_out_by_task = @($blockedByTask)
            _selection_usable = $true
            relevance_score = if ($overallTop) { [double]$overallTop.score } else { 0.0 }
        }
    }

    return [pscustomobject]@{
        selected = [string]$top.skill
        score = [double]$top.score
        reason = "keyword_ranked"
        ranking = @(ConvertTo-PublicCandidateRanking -Rows @($usableRanked | Select-Object -First 6))
        top1_top2_gap = $gap
        filtered_out_by_task = @($blockedByTask)
        _selection_usable = $true
        relevance_score = if ($overallTop) { [double]$overallTop.score } else { 0.0 }
    }
}
