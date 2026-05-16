"""Tests for Bloco 14 offline, cache and storage policy."""

from __future__ import annotations

from dataclasses import asdict

import inspect

import noqlen_aria.offline_cache as oc
from noqlen_aria.contracts import AriaError, safe_serialize
from noqlen_aria.offline_cache import (
    CacheBlockedReason,
    CacheCleanupItem,
    CacheCleanupPolicy,
    CacheCleanupPreview,
    CacheCleanupPreviewService,
    CacheConfirmationState,
    CacheEligibilityState,
    CacheItemId,
    CacheOperationIntent,
    CacheOperationPreview,
    CacheOperationResult,
    CacheOperationType,
    CachePolicyMode,
    CachePolicyState,
    CacheSourceId,
    OfflineAvailabilityReason,
    OfflineAvailabilityState,
    OfflineCachePolicyService,
    PendingCacheOperation,
    PendingOperationId,
    StorageBudget,
    StoragePressureLevel,
    StoragePressureService,
    StoragePressureState,
)


def _data(result):
    assert result.ok, result.error
    assert result.data is not None
    return result.data


def _err(result):
    assert result.is_err()
    assert result.error is not None
    return result.error


_policy_service = OfflineCachePolicyService()
_pressure_service = StoragePressureService()
_cleanup_service = CacheCleanupPreviewService()


# ═══════════════════════════════════════════════════════════════
# Model defaults and serialization
# ═══════════════════════════════════════════════════════════════

def test_offline_availability_state_is_enum() -> None:
    assert isinstance(OfflineAvailabilityState.AVAILABLE, OfflineAvailabilityState)
    assert len(OfflineAvailabilityState) == 3


def test_offline_availability_reason_is_enum() -> None:
    assert isinstance(OfflineAvailabilityReason.SUPPORTED, OfflineAvailabilityReason)
    assert len(OfflineAvailabilityReason) == 5


def test_cache_policy_state_is_enum() -> None:
    assert isinstance(CachePolicyState.ALLOWED, CachePolicyState)
    assert len(CachePolicyState) == 4


def test_cache_policy_mode_is_enum() -> None:
    assert isinstance(CachePolicyMode.CONSERVATIVE, CachePolicyMode)
    assert len(CachePolicyMode) == 3


def test_cache_eligibility_state_is_enum() -> None:
    assert isinstance(CacheEligibilityState.ELIGIBLE, CacheEligibilityState)
    assert len(CacheEligibilityState) == 5


def test_cache_operation_type_is_enum() -> None:
    assert isinstance(CacheOperationType.ADD_TO_CACHE, CacheOperationType)
    assert CacheOperationType.ADD_TO_CACHE != CacheOperationType.CLEAR_CACHE


def test_storage_pressure_level_is_enum() -> None:
    assert isinstance(StoragePressureLevel.NONE, StoragePressureLevel)
    assert len(StoragePressureLevel) == 5


def test_cache_confirmation_state_is_enum() -> None:
    assert isinstance(CacheConfirmationState.NOT_REQUIRED, CacheConfirmationState)
    assert len(CacheConfirmationState) == 2


def test_cache_blocked_reason_is_enum() -> None:
    assert isinstance(CacheBlockedReason.NONE, CacheBlockedReason)
    assert len(CacheBlockedReason) == 8


def test_storage_budget_defaults() -> None:
    budget = StorageBudget(max_bytes=1000)
    assert budget.max_bytes == 1000
    assert budget.used_bytes == 0
    assert budget.reserved_bytes == 0


def test_cache_operation_intent_defaults() -> None:
    intent = CacheOperationIntent(
        operation_type=CacheOperationType.ADD_TO_CACHE,
        item_id=CacheItemId("item-1"),
        source_id=CacheSourceId("src-1"),
    )
    assert intent.estimated_size_bytes == 0


def test_cache_operation_preview_defaults() -> None:
    intent = CacheOperationIntent(
        operation_type=CacheOperationType.ADD_TO_CACHE,
        item_id=CacheItemId("item-1"),
        source_id=CacheSourceId("src-1"),
    )
    preview = CacheOperationPreview(intent=intent, allowed=True)
    assert preview.summary == ""
    assert preview.confirmation_state == CacheConfirmationState.NOT_REQUIRED
    assert preview.blocked_reason == CacheBlockedReason.NONE


def test_cache_operation_result_defaults() -> None:
    intent = CacheOperationIntent(
        operation_type=CacheOperationType.ADD_TO_CACHE,
        item_id=CacheItemId("item-1"),
        source_id=CacheSourceId("src-1"),
    )
    preview = CacheOperationPreview(intent=intent, allowed=True)
    result = CacheOperationResult(allowed=True, intent=intent, preview=preview)
    assert result.blocked_reason == CacheBlockedReason.NONE
    assert result.issues == ()


def test_pending_cache_operation_defaults() -> None:
    intent = CacheOperationIntent(
        operation_type=CacheOperationType.ADD_TO_CACHE,
        item_id=CacheItemId("item-1"),
        source_id=CacheSourceId("src-1"),
    )
    pending = PendingCacheOperation(
        operation_id=PendingOperationId("op-1"),
        intent=intent,
    )
    assert pending.status_summary == ""


def test_cache_cleanup_item_defaults() -> None:
    item = CacheCleanupItem(
        item_id=CacheItemId("item-1"),
        source_id=CacheSourceId("src-1"),
    )
    assert item.estimated_size_bytes == 0
    assert item.age_days == 0


def test_cache_cleanup_policy_defaults() -> None:
    policy = CacheCleanupPolicy()
    assert policy.min_age_days == 0
    assert policy.max_candidates == 0
    assert policy.target_bytes == 0


def test_cache_cleanup_preview_defaults() -> None:
    preview = CacheCleanupPreview()
    assert preview.candidates == ()
    assert preview.total_items == 0
    assert preview.estimated_bytes_freed == 0
    assert preview.confirmation_required is False


def test_models_are_serializable() -> None:
    budget = StorageBudget(max_bytes=1000, used_bytes=200)
    serialized = safe_serialize(budget)
    assert isinstance(serialized, dict)
    assert serialized["max_bytes"] == 1000
    assert serialized["used_bytes"] == 200
    assert serialized["reserved_bytes"] == 0


def test_all_public_names_in_all() -> None:
    module_vars = {k: v for k, v in vars(oc).items()}
    public_names = {
        n for n, v in vars(oc).items()
        if not n.startswith("_") and n[0].isupper() and getattr(v, "__module__", "") == oc.__name__
    }
    missing = public_names - set(oc.__all__)
    assert not missing, f"Missing from __all__: {missing}"


# ═══════════════════════════════════════════════════════════════
# Offline availability (CE-01)
# ═══════════════════════════════════════════════════════════════

def test_offline_available_when_source_supports_and_cacheable() -> None:
    state, reason = _data(_policy_service.evaluate_offline_availability(
        source_supports_cache=True,
        item_is_cacheable=True,
        source_available=True,
    ))
    assert state == OfflineAvailabilityState.AVAILABLE
    assert reason == OfflineAvailabilityReason.SUPPORTED


def test_offline_unavailable_when_source_missing() -> None:
    state, reason = _data(_policy_service.evaluate_offline_availability(
        source_supports_cache=True,
        item_is_cacheable=True,
        source_available=False,
    ))
    assert state == OfflineAvailabilityState.UNAVAILABLE
    assert reason == OfflineAvailabilityReason.UNSUPPORTED_SOURCE


def test_offline_unavailable_when_no_cache_capability() -> None:
    state, reason = _data(_policy_service.evaluate_offline_availability(
        source_supports_cache=False,
        item_is_cacheable=True,
        source_available=True,
    ))
    assert state == OfflineAvailabilityState.UNAVAILABLE
    assert reason == OfflineAvailabilityReason.NO_CACHE_CAPABILITY


def test_offline_unavailable_when_item_not_cacheable() -> None:
    state, reason = _data(_policy_service.evaluate_offline_availability(
        source_supports_cache=True,
        item_is_cacheable=False,
        source_available=True,
    ))
    assert state == OfflineAvailabilityState.UNAVAILABLE
    assert reason == OfflineAvailabilityReason.ITEM_NOT_CACHEABLE


def test_offline_availability_default_to_all_false_is_unavailable() -> None:
    state, reason = _data(_policy_service.evaluate_offline_availability(
        source_supports_cache=False,
        item_is_cacheable=False,
        source_available=False,
    ))
    assert state == OfflineAvailabilityState.UNAVAILABLE


# ═══════════════════════════════════════════════════════════════
# Cache eligibility (CE-02)
# ═══════════════════════════════════════════════════════════════

def test_cache_eligible() -> None:
    result = _data(_policy_service.evaluate_cache_eligibility(
        source_supports_cache=True,
        item_format_cacheable=True,
        source_available=True,
    ))
    assert result == CacheEligibilityState.ELIGIBLE


def test_cache_ineligible_source_unavailable() -> None:
    result = _data(_policy_service.evaluate_cache_eligibility(
        source_supports_cache=True,
        item_format_cacheable=True,
        source_available=False,
    ))
    assert result == CacheEligibilityState.INELIGIBLE_SOURCE


def test_cache_ineligible_unsupported() -> None:
    result = _data(_policy_service.evaluate_cache_eligibility(
        source_supports_cache=False,
        item_format_cacheable=True,
        source_available=True,
    ))
    assert result == CacheEligibilityState.INELIGIBLE_UNSUPPORTED


def test_cache_ineligible_format() -> None:
    result = _data(_policy_service.evaluate_cache_eligibility(
        source_supports_cache=True,
        item_format_cacheable=False,
        source_available=True,
    ))
    assert result == CacheEligibilityState.INELIGIBLE_FORMAT


def test_cache_eligibility_defaults_to_eligible() -> None:
    result = _data(_policy_service.evaluate_cache_eligibility())
    assert result == CacheEligibilityState.ELIGIBLE


# ═══════════════════════════════════════════════════════════════
# Cache operation preview (CE-03, CE-04, CE-07)
# ═══════════════════════════════════════════════════════════════

def _add_intent(size: int = 100) -> CacheOperationIntent:
    return CacheOperationIntent(
        operation_type=CacheOperationType.ADD_TO_CACHE,
        item_id=CacheItemId("item-1"),
        source_id=CacheSourceId("src-1"),
        estimated_size_bytes=size,
    )


def _remove_intent(size: int = 100) -> CacheOperationIntent:
    return CacheOperationIntent(
        operation_type=CacheOperationType.REMOVE_FROM_CACHE,
        item_id=CacheItemId("item-1"),
        source_id=CacheSourceId("src-1"),
        estimated_size_bytes=size,
    )


def _clear_intent(size: int = 500) -> CacheOperationIntent:
    return CacheOperationIntent(
        operation_type=CacheOperationType.CLEAR_CACHE,
        item_id=CacheItemId(""),
        source_id=CacheSourceId("src-1"),
        estimated_size_bytes=size,
    )


def test_preview_add_allowed_with_plenty_of_space() -> None:
    result = _data(_policy_service.preview_cache_operation(
        _add_intent(100),
        budget=StorageBudget(max_bytes=10000, used_bytes=1000),
    ))
    assert result.allowed
    assert result.preview.confirmation_state == CacheConfirmationState.NOT_REQUIRED


def test_preview_add_blocked_under_high_pressure_conservative() -> None:
    result = _data(_policy_service.preview_cache_operation(
        _add_intent(100),
        cache_policy_mode=CachePolicyMode.CONSERVATIVE,
        budget=StorageBudget(max_bytes=10000, used_bytes=9500),
    ))
    assert not result.allowed
    assert result.blocked_reason == CacheBlockedReason.STORAGE_PRESSURE_HIGH


def test_preview_add_blocked_under_high_pressure_balanced() -> None:
    result = _data(_policy_service.preview_cache_operation(
        _add_intent(100),
        cache_policy_mode=CachePolicyMode.BALANCED,
        budget=StorageBudget(max_bytes=10000, used_bytes=9500),
    ))
    assert not result.allowed
    assert result.blocked_reason == CacheBlockedReason.STORAGE_PRESSURE_HIGH


def test_preview_add_allowed_aggressive_high_pressure_requires_confirmation() -> None:
    result = _data(_policy_service.preview_cache_operation(
        _add_intent(100),
        cache_policy_mode=CachePolicyMode.AGGRESSIVE,
        budget=StorageBudget(max_bytes=10000, used_bytes=9500),
    ))
    assert result.allowed
    assert result.preview.confirmation_state == CacheConfirmationState.REQUIRED


def test_preview_add_blocked_critical_pressure_any_mode() -> None:
    for mode in CachePolicyMode:
        result = _data(_policy_service.preview_cache_operation(
            _add_intent(100),
            cache_policy_mode=mode,
            budget=StorageBudget(max_bytes=10000, used_bytes=11000),
        ))
        assert not result.allowed, f"Should be blocked under {mode}"
        assert result.blocked_reason == CacheBlockedReason.STORAGE_PRESSURE_CRITICAL


def test_preview_add_blocked_medium_pressure_conservative() -> None:
    result = _data(_policy_service.preview_cache_operation(
        _add_intent(100),
        cache_policy_mode=CachePolicyMode.CONSERVATIVE,
        budget=StorageBudget(max_bytes=10000, used_bytes=8000),
    ))
    assert not result.allowed
    assert result.blocked_reason == CacheBlockedReason.BUDGET_EXCEEDED


def test_preview_add_allowed_medium_pressure_balanced_with_confirmation() -> None:
    result = _data(_policy_service.preview_cache_operation(
        _add_intent(100),
        cache_policy_mode=CachePolicyMode.BALANCED,
        budget=StorageBudget(max_bytes=10000, used_bytes=8000),
    ))
    assert result.allowed
    assert result.preview.confirmation_state == CacheConfirmationState.REQUIRED


def test_preview_add_allowed_medium_pressure_aggressive_no_confirmation() -> None:
    result = _data(_policy_service.preview_cache_operation(
        _add_intent(100),
        cache_policy_mode=CachePolicyMode.AGGRESSIVE,
        budget=StorageBudget(max_bytes=10000, used_bytes=8000),
    ))
    assert result.allowed
    assert result.preview.confirmation_state == CacheConfirmationState.NOT_REQUIRED


def test_preview_add_allowed_low_pressure_conservative_with_confirmation() -> None:
    result = _data(_policy_service.preview_cache_operation(
        _add_intent(100),
        cache_policy_mode=CachePolicyMode.CONSERVATIVE,
        budget=StorageBudget(max_bytes=10000, used_bytes=5500),
    ))
    assert result.allowed
    assert result.preview.confirmation_state == CacheConfirmationState.REQUIRED


def test_preview_add_allowed_low_pressure_balanced_no_confirmation() -> None:
    result = _data(_policy_service.preview_cache_operation(
        _add_intent(100),
        cache_policy_mode=CachePolicyMode.BALANCED,
        budget=StorageBudget(max_bytes=10000, used_bytes=5500),
    ))
    assert result.allowed
    assert result.preview.confirmation_state == CacheConfirmationState.NOT_REQUIRED


def test_preview_add_blocked_estimated_size_exceeds_available() -> None:
    result = _data(_policy_service.preview_cache_operation(
        _add_intent(2000),
        budget=StorageBudget(max_bytes=10000, used_bytes=8000, reserved_bytes=1000),
    ))
    assert not result.allowed
    assert result.blocked_reason == CacheBlockedReason.BUDGET_EXCEEDED


def test_preview_ineligible_source_blocks_operation() -> None:
    result = _data(_policy_service.preview_cache_operation(
        _add_intent(100),
        eligibility=CacheEligibilityState.INELIGIBLE_SOURCE,
    ))
    assert not result.allowed
    assert result.blocked_reason == CacheBlockedReason.SOURCE_UNAVAILABLE


def test_preview_ineligible_format_blocks_operation() -> None:
    result = _data(_policy_service.preview_cache_operation(
        _add_intent(100),
        eligibility=CacheEligibilityState.INELIGIBLE_FORMAT,
    ))
    assert not result.allowed
    assert result.blocked_reason == CacheBlockedReason.ITEM_NOT_CACHEABLE


def test_preview_ineligible_unsupported_blocks_operation() -> None:
    result = _data(_policy_service.preview_cache_operation(
        _add_intent(100),
        eligibility=CacheEligibilityState.INELIGIBLE_UNSUPPORTED,
    ))
    assert not result.allowed
    assert result.blocked_reason == CacheBlockedReason.ITEM_NOT_CACHEABLE


def test_preview_remove_always_allowed() -> None:
    result = _data(_policy_service.preview_cache_operation(
        _remove_intent(100),
        budget=StorageBudget(max_bytes=10000, used_bytes=9900),
    ))
    assert result.allowed
    assert result.preview.confirmation_state == CacheConfirmationState.NOT_REQUIRED


def test_preview_clear_requires_confirmation() -> None:
    result = _data(_policy_service.preview_cache_operation(
        _clear_intent(500),
    ))
    assert result.allowed
    assert result.preview.confirmation_state == CacheConfirmationState.REQUIRED


# ═══════════════════════════════════════════════════════════════
# Invalid budget/size validation (CE-06, CE-07)
# ═══════════════════════════════════════════════════════════════

def test_negative_estimated_size_blocks_operation() -> None:
    result = _data(_policy_service.preview_cache_operation(
        _add_intent(-500),
    ))
    assert not result.allowed
    assert result.blocked_reason == CacheBlockedReason.INVALID_BUDGET
    assert "INVALID_ESTIMATED_SIZE" in result.issues


def test_zero_max_bytes_blocks_operation() -> None:
    result = _data(_policy_service.preview_cache_operation(
        _add_intent(100),
        budget=StorageBudget(max_bytes=0, used_bytes=0),
    ))
    assert not result.allowed
    assert result.blocked_reason == CacheBlockedReason.INVALID_BUDGET
    assert "INVALID_BUDGET_MAX_BYTES" in result.issues


def test_negative_max_bytes_blocks_operation() -> None:
    result = _data(_policy_service.preview_cache_operation(
        _add_intent(100),
        budget=StorageBudget(max_bytes=-1, used_bytes=0),
    ))
    assert not result.allowed
    assert result.blocked_reason == CacheBlockedReason.INVALID_BUDGET


def test_negative_reserved_bytes_blocks_operation() -> None:
    result = _data(_policy_service.preview_cache_operation(
        _add_intent(100),
        budget=StorageBudget(max_bytes=1000, used_bytes=0, reserved_bytes=-1),
    ))
    assert not result.allowed
    assert result.blocked_reason == CacheBlockedReason.INVALID_BUDGET
    assert "INVALID_BUDGET_RESERVED" in result.issues


def test_reserved_exceeds_max_bytes_blocks_operation() -> None:
    result = _data(_policy_service.preview_cache_operation(
        _add_intent(100),
        budget=StorageBudget(max_bytes=1000, used_bytes=0, reserved_bytes=2000),
    ))
    assert not result.allowed
    assert result.blocked_reason == CacheBlockedReason.INVALID_BUDGET
    assert "INVALID_BUDGET_RESERVED" in result.issues


def test_operation_blocked_when_free_below_reserved() -> None:
    result = _data(_policy_service.preview_cache_operation(
        _add_intent(100),
        cache_policy_mode=CachePolicyMode.AGGRESSIVE,
        budget=StorageBudget(max_bytes=10000, used_bytes=5000, reserved_bytes=6000),
    ))
    assert not result.allowed
    assert result.blocked_reason == CacheBlockedReason.STORAGE_PRESSURE_CRITICAL


# ═══════════════════════════════════════════════════════════════
# Storage pressure service (CE-06)
# ═══════════════════════════════════════════════════════════════

def test_pressure_none_with_plenty_of_space() -> None:
    state = _data(_pressure_service.evaluate_pressure(
        StorageBudget(max_bytes=10000, used_bytes=1000),
    ))
    assert state.level == StoragePressureLevel.NONE
    assert state.free_bytes == 9000


def test_pressure_low_below_50_percent() -> None:
    state = _data(_pressure_service.evaluate_pressure(
        StorageBudget(max_bytes=10000, used_bytes=5500),
    ))
    assert state.level == StoragePressureLevel.LOW


def test_pressure_medium_below_25_percent() -> None:
    state = _data(_pressure_service.evaluate_pressure(
        StorageBudget(max_bytes=10000, used_bytes=8000),
    ))
    assert state.level == StoragePressureLevel.MEDIUM


def test_pressure_high_below_10_percent() -> None:
    state = _data(_pressure_service.evaluate_pressure(
        StorageBudget(max_bytes=10000, used_bytes=9500),
    ))
    assert state.level == StoragePressureLevel.HIGH


def test_pressure_exactly_10_percent_is_high() -> None:
    state = _data(_pressure_service.evaluate_pressure(
        StorageBudget(max_bytes=10000, used_bytes=9000),
    ))
    assert state.level == StoragePressureLevel.HIGH


def test_pressure_critical_used_exceeds_max() -> None:
    state = _data(_pressure_service.evaluate_pressure(
        StorageBudget(max_bytes=10000, used_bytes=11000),
    ))
    assert state.level == StoragePressureLevel.CRITICAL


def test_pressure_critical_free_below_reserved() -> None:
    state = _data(_pressure_service.evaluate_pressure(
        StorageBudget(max_bytes=10000, used_bytes=3000, reserved_bytes=8000),
    ))
    assert state.level == StoragePressureLevel.CRITICAL


def test_pressure_none_zero_used_zero_reserved() -> None:
    state = _data(_pressure_service.evaluate_pressure(
        StorageBudget(max_bytes=10000, used_bytes=0, reserved_bytes=0),
    ))
    assert state.level == StoragePressureLevel.NONE


def test_pressure_state_includes_all_fields() -> None:
    state = _data(_pressure_service.evaluate_pressure(
        StorageBudget(max_bytes=10000, used_bytes=3000, reserved_bytes=1000),
    ))
    assert state.max_bytes == 10000
    assert state.used_bytes == 3000
    assert state.reserved_bytes == 1000
    assert state.free_bytes == 7000
    assert len(state.summary) > 0


def test_pressure_invalid_zero_max_bytes() -> None:
    result = _pressure_service.evaluate_pressure(StorageBudget(max_bytes=0))
    assert result.is_err()


def test_pressure_invalid_negative_max_bytes() -> None:
    result = _pressure_service.evaluate_pressure(StorageBudget(max_bytes=-1))
    assert result.is_err()


def test_pressure_invalid_negative_reserved() -> None:
    result = _pressure_service.evaluate_pressure(StorageBudget(max_bytes=1000, reserved_bytes=-1))
    assert result.is_err()


def test_pressure_invalid_reserved_exceeds_max() -> None:
    result = _pressure_service.evaluate_pressure(StorageBudget(max_bytes=1000, reserved_bytes=2000))
    assert result.is_err()


def test_pressure_invalid_negative_used() -> None:
    result = _pressure_service.evaluate_pressure(StorageBudget(max_bytes=1000, used_bytes=-1))
    assert result.is_err()


def test_can_accept_operation_fits() -> None:
    assert _data(_pressure_service.can_accept_operation(
        StorageBudget(max_bytes=10000, used_bytes=1000), 500,
    ))


def test_can_accept_operation_exceeds_budget() -> None:
    assert not _data(_pressure_service.can_accept_operation(
        StorageBudget(max_bytes=10000, used_bytes=8000, reserved_bytes=1000), 2000,
    ))


def test_can_accept_operation_negative_size() -> None:
    assert not _data(_pressure_service.can_accept_operation(
        StorageBudget(max_bytes=10000, used_bytes=1000), -500,
    ))


def test_can_accept_operation_invalid_budget() -> None:
    assert not _data(_pressure_service.can_accept_operation(
        StorageBudget(max_bytes=0, used_bytes=0), 100,
    ))


def test_can_accept_operation_negative_used() -> None:
    assert not _data(_pressure_service.can_accept_operation(
        StorageBudget(max_bytes=1000, used_bytes=-1), 100,
    ))


def test_can_accept_operation_used_exceeds_max() -> None:
    assert not _data(_pressure_service.can_accept_operation(
        StorageBudget(max_bytes=1000, used_bytes=2000), 100,
    ))


def test_can_accept_operation_free_below_reserved() -> None:
    assert not _data(_pressure_service.can_accept_operation(
        StorageBudget(max_bytes=10000, used_bytes=3000, reserved_bytes=8000), 100,
    ))


# ═══════════════════════════════════════════════════════════════
# Cleanup preview (CE-05)
# ═══════════════════════════════════════════════════════════════

def _make_cleanup_candidates() -> tuple[CacheCleanupItem, ...]:
    return (
        CacheCleanupItem(CacheItemId("old-1"), CacheSourceId("src-1"), 1000, 60),
        CacheCleanupItem(CacheItemId("old-2"), CacheSourceId("src-1"), 500, 45),
        CacheCleanupItem(CacheItemId("recent-1"), CacheSourceId("src-1"), 800, 10),
        CacheCleanupItem(CacheItemId("recent-2"), CacheSourceId("src-1"), 200, 5),
    )


def test_cleanup_preview_filters_by_min_age() -> None:
    result = _data(_cleanup_service.preview_cleanup(
        CacheCleanupPolicy(min_age_days=30, max_candidates=10),
        StorageBudget(max_bytes=10000, used_bytes=5000),
        _make_cleanup_candidates(),
    ))
    assert result.total_items == 2
    assert result.estimated_bytes_freed == 1500
    assert all(c.age_days >= 30 for c in result.candidates)


def test_cleanup_preview_respects_max_candidates() -> None:
    result = _data(_cleanup_service.preview_cleanup(
        CacheCleanupPolicy(min_age_days=0, max_candidates=1),
        StorageBudget(max_bytes=10000, used_bytes=5000),
        _make_cleanup_candidates(),
    ))
    assert result.total_items == 1


def test_cleanup_preview_respects_target_bytes() -> None:
    result = _data(_cleanup_service.preview_cleanup(
        CacheCleanupPolicy(min_age_days=0, max_candidates=10, target_bytes=800),
        StorageBudget(max_bytes=10000, used_bytes=5000),
        _make_cleanup_candidates(),
    ))
    assert result.estimated_bytes_freed >= 800


def test_cleanup_preview_empty_candidates() -> None:
    result = _data(_cleanup_service.preview_cleanup(
        CacheCleanupPolicy(min_age_days=30, max_candidates=10),
        StorageBudget(max_bytes=10000, used_bytes=5000),
        (),
    ))
    assert result.total_items == 0
    assert result.estimated_bytes_freed == 0
    assert not result.confirmation_required


def test_cleanup_preview_invalid_max_bytes() -> None:
    result = _cleanup_service.preview_cleanup(
        CacheCleanupPolicy(min_age_days=30),
        StorageBudget(max_bytes=0),
    )
    assert result.is_err()


def test_cleanup_preview_negative_max_candidates() -> None:
    result = _cleanup_service.preview_cleanup(
        CacheCleanupPolicy(min_age_days=0, max_candidates=-1),
        StorageBudget(max_bytes=10000),
    )
    assert result.is_err()


def test_cleanup_preview_negative_min_age() -> None:
    result = _cleanup_service.preview_cleanup(
        CacheCleanupPolicy(min_age_days=-5),
        StorageBudget(max_bytes=10000),
    )
    assert result.is_err()


def test_cleanup_preview_confirmation_when_has_candidates_and_target() -> None:
    result = _data(_cleanup_service.preview_cleanup(
        CacheCleanupPolicy(min_age_days=30, max_candidates=10, target_bytes=500),
        StorageBudget(max_bytes=10000, used_bytes=5000),
        _make_cleanup_candidates(),
    ))
    assert result.confirmation_required
    assert result.total_items > 0


def test_cleanup_preview_no_confirmation_no_target() -> None:
    result = _data(_cleanup_service.preview_cleanup(
        CacheCleanupPolicy(min_age_days=30, max_candidates=10, target_bytes=0),
        StorageBudget(max_bytes=10000, used_bytes=5000),
        _make_cleanup_candidates(),
    ))
    assert not result.confirmation_required
    assert result.total_items > 0


def test_cleanup_preview_no_confirmation_empty_result() -> None:
    result = _data(_cleanup_service.preview_cleanup(
        CacheCleanupPolicy(min_age_days=1000, max_candidates=10, target_bytes=100),
        StorageBudget(max_bytes=10000, used_bytes=5000),
        _make_cleanup_candidates(),
    ))
    assert not result.confirmation_required


def test_evaluate_cleanup_candidates_filters_by_age() -> None:
    result = _data(_cleanup_service.evaluate_cleanup_candidates(
        CacheCleanupPolicy(min_age_days=40),
        _make_cleanup_candidates(),
    ))
    assert len(result) == 2
    assert all(c.age_days >= 40 for c in result)


def test_evaluate_cleanup_candidates_error_negative_age() -> None:
    result = _cleanup_service.evaluate_cleanup_candidates(
        CacheCleanupPolicy(min_age_days=-1),
    )
    assert result.is_err()


# ═══════════════════════════════════════════════════════════════
# Determinism
# ═══════════════════════════════════════════════════════════════

def test_policy_service_deterministic() -> None:
    s = OfflineCachePolicyService()
    r1 = _data(s.evaluate_offline_availability(source_supports_cache=True, item_is_cacheable=True))
    r2 = _data(s.evaluate_offline_availability(source_supports_cache=True, item_is_cacheable=True))
    assert r1 == r2


def test_pressure_service_deterministic() -> None:
    result1 = _data(_pressure_service.evaluate_pressure(StorageBudget(max_bytes=10000, used_bytes=5000)))
    result2 = _data(_pressure_service.evaluate_pressure(StorageBudget(max_bytes=10000, used_bytes=5000)))
    assert result1 == result2


def test_cleanup_service_deterministic() -> None:
    r1 = _data(_cleanup_service.preview_cleanup(
        CacheCleanupPolicy(min_age_days=30),
        StorageBudget(max_bytes=10000),
        _make_cleanup_candidates(),
    ))
    r2 = _data(_cleanup_service.preview_cleanup(
        CacheCleanupPolicy(min_age_days=30),
        StorageBudget(max_bytes=10000),
        _make_cleanup_candidates(),
    ))
    assert r1 == r2


def test_no_external_modules_imported() -> None:
    source = inspect.getsource(oc)
    for forbidden in ("os.path", "pathlib", "glob", "shutil", "urllib", "http",
                      "requests", "aiohttp", "socket", "subprocess"):
        assert forbidden not in source, f"Found forbidden import: {forbidden}"


# ═══════════════════════════════════════════════════════════════
# No real filesystem/provider/network/Android behavior
# ═══════════════════════════════════════════════════════════════

def test_services_do_not_access_filesystem() -> None:
    methods = inspect.getsource(OfflineCachePolicyService)
    for forbidden in ("os.walk", "glob.glob", "iterdir", "scandir", "unlink", "rmtree", "remove(", "open("):
        assert forbidden not in methods, f"Found filesystem access: {forbidden}"


def test_services_do_not_access_network() -> None:
    methods = inspect.getsource(OfflineCachePolicyService)
    assert "request" not in methods.lower() or "request" in methods.lower() and "requests." not in methods


def test_models_frozen_and_deterministic() -> None:
    model_classes = [v for v in vars(oc).values() if inspect.isclass(v) and hasattr(v, "__dataclass_fields__")]
    for cls in model_classes:
        # all dataclasses should be frozen
        if getattr(cls, "__dataclass_params__", None):
            assert cls.__dataclass_params__.frozen, f"{cls.__name__} is not frozen"


# ═══════════════════════════════════════════════════════════════
# Boundary enforcement: no Bloco 15 / forbidden behavior
# ═══════════════════════════════════════════════════════════════

def test_no_transcode_stream_quality_references() -> None:
    source = inspect.getsource(oc)
    forbidden = ("Transcode", "StreamQuality", "SmartPlaylist")
    for term in forbidden:
        assert term not in source, f"Found forbidden term: {term}"


def test_no_android_references() -> None:
    source = inspect.getsource(oc)
    forbidden = ("android.", "androidx.", "MediaStore", "SAF", "Media3",
                 "ExoPlayer", "Activity", "Fragment", "Compose", "Kotlin", "Gradle")
    for term in forbidden:
        assert term not in source, f"Found Android reference: {term}"


def test_no_provider_references() -> None:
    source = inspect.getsource(oc)
    forbidden = ("NavidromeProvider", "Jellyfin", "Emby", "noqlen_anchor.cli",
                 "subprocess.*noqlen-anchor")
    for term in forbidden:
        assert term not in source, f"Found provider reference: {term}"


def test_no_network_references() -> None:
    source = inspect.getsource(oc)
    forbidden = ("requests.", "httpx.", "aiohttp.", "urllib.", "socket.")
    for term in forbidden:
        assert term not in source, f"Found network reference: {term}"


# ═══════════════════════════════════════════════════════════════
# Additional edge case tests
# ═══════════════════════════════════════════════════════════════

def test_cache_operation_preview_estimated_impact_for_remove() -> None:
    result = _data(_policy_service.preview_cache_operation(
        _remove_intent(300),
    ))
    assert result.preview.estimated_impact_bytes == -300


def test_cache_operation_preview_estimated_impact_for_clear() -> None:
    result = _data(_policy_service.preview_cache_operation(
        _clear_intent(500),
    ))
    assert result.preview.estimated_impact_bytes == -500


def test_default_policy_mode_is_balanced() -> None:
    result = _data(_policy_service.preview_cache_operation(
        _add_intent(100),
        budget=StorageBudget(max_bytes=10000, used_bytes=8000),
    ))
    assert result.allowed
    assert result.preview.confirmation_state == CacheConfirmationState.REQUIRED


def test_free_exactly_at_reserved_is_critical() -> None:
    state = _data(_pressure_service.evaluate_pressure(
        StorageBudget(max_bytes=10000, used_bytes=5000, reserved_bytes=5000),
    ))
    assert state.level == StoragePressureLevel.CRITICAL


def test_exactly_25_percent_free_is_medium() -> None:
    state = _data(_pressure_service.evaluate_pressure(
        StorageBudget(max_bytes=10000, used_bytes=7500),
    ))
    assert state.level == StoragePressureLevel.MEDIUM


def test_exactly_50_percent_free_is_low() -> None:
    state = _data(_pressure_service.evaluate_pressure(
        StorageBudget(max_bytes=10000, used_bytes=5000),
    ))
    assert state.level == StoragePressureLevel.LOW


def test_cleanup_preview_sorts_oldest_first() -> None:
    candidates = (
        CacheCleanupItem(CacheItemId("c"), CacheSourceId("s"), 100, 30),
        CacheCleanupItem(CacheItemId("a"), CacheSourceId("s"), 500, 90),
        CacheCleanupItem(CacheItemId("b"), CacheSourceId("s"), 200, 60),
    )
    result = _data(_cleanup_service.preview_cleanup(
        CacheCleanupPolicy(min_age_days=10, max_candidates=3),
        StorageBudget(max_bytes=10000),
        candidates,
    ))
    ages = [c.age_days for c in result.candidates]
    assert ages == [90, 60, 30], f"Expected oldest first, got {ages}"


def test_remove_operation_allowed_even_with_invalid_budget() -> None:
    result = _data(_policy_service.preview_cache_operation(
        _remove_intent(100),
        budget=StorageBudget(max_bytes=-1),
    ))
    assert result.allowed


def test_service_methods_return_aria_result() -> None:
    from noqlen_aria.contracts import AriaResult
    r = _policy_service.evaluate_offline_availability()
    assert isinstance(r, AriaResult)
