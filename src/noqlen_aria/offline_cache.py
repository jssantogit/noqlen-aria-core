"""Aria Core offline, cache and storage policy — models, intents, previews and deterministic local services.

Bloco 14 — Offline, Cache and Storage Policy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import NewType

from noqlen_aria.contracts import AriaError, AriaResult

CacheItemId = NewType("CacheItemId", str)
CacheSourceId = NewType("CacheSourceId", str)
PendingOperationId = NewType("PendingOperationId", str)


class OfflineAvailabilityState(Enum):
    AVAILABLE = auto()
    UNAVAILABLE = auto()
    UNKNOWN = auto()


class OfflineAvailabilityReason(Enum):
    SUPPORTED = auto()
    UNSUPPORTED_SOURCE = auto()
    NO_CACHE_CAPABILITY = auto()
    ITEM_NOT_CACHEABLE = auto()
    UNKNOWN = auto()


class CachePolicyState(Enum):
    ALLOWED = auto()
    BLOCKED = auto()
    REQUIRES_CONFIRMATION = auto()
    UNKNOWN = auto()


class CachePolicyMode(Enum):
    CONSERVATIVE = auto()
    BALANCED = auto()
    AGGRESSIVE = auto()


class CacheEligibilityState(Enum):
    ELIGIBLE = auto()
    INELIGIBLE_FORMAT = auto()
    INELIGIBLE_SOURCE = auto()
    INELIGIBLE_UNSUPPORTED = auto()
    UNKNOWN = auto()


class CacheOperationType(Enum):
    ADD_TO_CACHE = auto()
    REMOVE_FROM_CACHE = auto()
    CLEAR_CACHE = auto()


class StoragePressureLevel(Enum):
    NONE = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


class CacheConfirmationState(Enum):
    NOT_REQUIRED = auto()
    REQUIRED = auto()


class CacheBlockedReason(Enum):
    NONE = auto()
    SOURCE_UNAVAILABLE = auto()
    ITEM_NOT_CACHEABLE = auto()
    STORAGE_PRESSURE_CRITICAL = auto()
    STORAGE_PRESSURE_HIGH = auto()
    BUDGET_EXCEEDED = auto()
    INVALID_BUDGET = auto()
    OPERATION_UNSUPPORTED = auto()


@dataclass(frozen=True)
class StorageBudget:
    max_bytes: int
    used_bytes: int = 0
    reserved_bytes: int = 0


@dataclass(frozen=True)
class StoragePressureState:
    level: StoragePressureLevel
    free_bytes: int
    max_bytes: int = 0
    used_bytes: int = 0
    reserved_bytes: int = 0
    summary: str = ""


@dataclass(frozen=True)
class CacheOperationIntent:
    operation_type: CacheOperationType
    item_id: CacheItemId
    source_id: CacheSourceId
    estimated_size_bytes: int = 0


@dataclass(frozen=True)
class CacheOperationPreview:
    intent: CacheOperationIntent
    allowed: bool
    summary: str = ""
    confirmation_state: CacheConfirmationState = CacheConfirmationState.NOT_REQUIRED
    blocked_reason: CacheBlockedReason = CacheBlockedReason.NONE
    estimated_impact_bytes: int = 0


@dataclass(frozen=True)
class CacheOperationResult:
    allowed: bool
    intent: CacheOperationIntent
    preview: CacheOperationPreview
    blocked_reason: CacheBlockedReason = CacheBlockedReason.NONE
    issues: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class PendingCacheOperation:
    operation_id: PendingOperationId
    intent: CacheOperationIntent
    status_summary: str = ""


@dataclass(frozen=True)
class CacheCleanupItem:
    item_id: CacheItemId
    source_id: CacheSourceId
    estimated_size_bytes: int = 0
    age_days: int = 0


@dataclass(frozen=True)
class CacheCleanupPolicy:
    min_age_days: int = 0
    max_candidates: int = 0
    target_bytes: int = 0


@dataclass(frozen=True)
class CacheCleanupPreview:
    candidates: tuple[CacheCleanupItem, ...] = field(default_factory=tuple)
    total_items: int = 0
    estimated_bytes_freed: int = 0
    confirmation_required: bool = False
    summary: str = ""


# ── Offline Cache Policy Service ───────────────────────────────

class OfflineCachePolicyService:
    """Evaluate offline availability, cache eligibility, and preview cache operations.

    No real download, cache write/delete, filesystem access, or network access.
    """

    def evaluate_offline_availability(
        self,
        *,
        source_supports_cache: bool = True,
        item_is_cacheable: bool = True,
        source_available: bool = True,
    ) -> AriaResult[tuple[OfflineAvailabilityState, OfflineAvailabilityReason]]:
        if not source_available:
            return self._ok(
                (OfflineAvailabilityState.UNAVAILABLE, OfflineAvailabilityReason.UNSUPPORTED_SOURCE)
            )
        if not source_supports_cache:
            return self._ok(
                (OfflineAvailabilityState.UNAVAILABLE, OfflineAvailabilityReason.NO_CACHE_CAPABILITY)
            )
        if not item_is_cacheable:
            return self._ok(
                (OfflineAvailabilityState.UNAVAILABLE, OfflineAvailabilityReason.ITEM_NOT_CACHEABLE)
            )
        return self._ok(
            (OfflineAvailabilityState.AVAILABLE, OfflineAvailabilityReason.SUPPORTED)
        )

    def evaluate_cache_eligibility(
        self,
        *,
        source_supports_cache: bool = True,
        item_format_cacheable: bool = True,
        source_available: bool = True,
    ) -> AriaResult[CacheEligibilityState]:
        if not source_available:
            return self._ok(CacheEligibilityState.INELIGIBLE_SOURCE)
        if not source_supports_cache:
            return self._ok(CacheEligibilityState.INELIGIBLE_UNSUPPORTED)
        if not item_format_cacheable:
            return self._ok(CacheEligibilityState.INELIGIBLE_FORMAT)
        return self._ok(CacheEligibilityState.ELIGIBLE)

    def preview_cache_operation(
        self,
        intent: CacheOperationIntent,
        *,
        cache_policy_mode: CachePolicyMode = CachePolicyMode.BALANCED,
        eligibility: CacheEligibilityState = CacheEligibilityState.ELIGIBLE,
        budget: StorageBudget | None = None,
    ) -> AriaResult[CacheOperationResult]:
        if intent.estimated_size_bytes < 0:
            preview = CacheOperationPreview(
                intent=intent,
                allowed=False,
                summary="Invalid estimated size: must not be negative",
                confirmation_state=CacheConfirmationState.NOT_REQUIRED,
                blocked_reason=CacheBlockedReason.INVALID_BUDGET,
            )
            return self._ok(CacheOperationResult(
                allowed=False,
                intent=intent,
                preview=preview,
                blocked_reason=CacheBlockedReason.INVALID_BUDGET,
                issues=("INVALID_ESTIMATED_SIZE",),
            ))

        if eligibility == CacheEligibilityState.INELIGIBLE_SOURCE:
            preview = CacheOperationPreview(
                intent=intent,
                allowed=False,
                summary="Source is unavailable or does not support caching",
                confirmation_state=CacheConfirmationState.NOT_REQUIRED,
                blocked_reason=CacheBlockedReason.SOURCE_UNAVAILABLE,
            )
            return self._ok(CacheOperationResult(
                allowed=False,
                intent=intent,
                preview=preview,
                blocked_reason=CacheBlockedReason.SOURCE_UNAVAILABLE,
            ))

        if eligibility in {CacheEligibilityState.INELIGIBLE_FORMAT, CacheEligibilityState.INELIGIBLE_UNSUPPORTED}:
            preview = CacheOperationPreview(
                intent=intent,
                allowed=False,
                summary="Item is not cacheable",
                confirmation_state=CacheConfirmationState.NOT_REQUIRED,
                blocked_reason=CacheBlockedReason.ITEM_NOT_CACHEABLE,
            )
            return self._ok(CacheOperationResult(
                allowed=False,
                intent=intent,
                preview=preview,
                blocked_reason=CacheBlockedReason.ITEM_NOT_CACHEABLE,
            ))

        if intent.operation_type == CacheOperationType.REMOVE_FROM_CACHE:
            preview = CacheOperationPreview(
                intent=intent,
                allowed=True,
                summary="Remove operation always allowed",
                confirmation_state=CacheConfirmationState.NOT_REQUIRED,
                estimated_impact_bytes=-intent.estimated_size_bytes,
            )
            return self._ok(CacheOperationResult(
                allowed=True,
                intent=intent,
                preview=preview,
            ))

        if intent.operation_type == CacheOperationType.CLEAR_CACHE:
            preview = CacheOperationPreview(
                intent=intent,
                allowed=True,
                summary="Clear cache requires confirmation",
                confirmation_state=CacheConfirmationState.REQUIRED,
                estimated_impact_bytes=-intent.estimated_size_bytes,
            )
            return self._ok(CacheOperationResult(
                allowed=True,
                intent=intent,
                preview=preview,
            ))

        if budget is not None:
            budget_result = self._check_budget(intent, budget, cache_policy_mode)
            if budget_result is not None:
                return budget_result

        preview = CacheOperationPreview(
            intent=intent,
            allowed=True,
            summary="Cache operation allowed",
            confirmation_state=CacheConfirmationState.NOT_REQUIRED,
            estimated_impact_bytes=intent.estimated_size_bytes,
        )
        return self._ok(CacheOperationResult(
            allowed=True,
            intent=intent,
            preview=preview,
        ))

    def _check_budget(
        self,
        intent: CacheOperationIntent,
        budget: StorageBudget,
        mode: CachePolicyMode,
    ) -> AriaResult[CacheOperationResult] | None:
        if budget.max_bytes <= 0:
            preview = CacheOperationPreview(
                intent=intent,
                allowed=False,
                summary="Invalid storage budget: max_bytes must be positive",
                confirmation_state=CacheConfirmationState.NOT_REQUIRED,
                blocked_reason=CacheBlockedReason.INVALID_BUDGET,
            )
            return self._ok(CacheOperationResult(
                allowed=False,
                intent=intent,
                preview=preview,
                blocked_reason=CacheBlockedReason.INVALID_BUDGET,
                issues=("INVALID_BUDGET_MAX_BYTES",),
            ))

        if budget.reserved_bytes < 0 or budget.reserved_bytes > budget.max_bytes:
            preview = CacheOperationPreview(
                intent=intent,
                allowed=False,
                summary="Invalid storage budget: reserved_bytes out of range",
                confirmation_state=CacheConfirmationState.NOT_REQUIRED,
                blocked_reason=CacheBlockedReason.INVALID_BUDGET,
            )
            return self._ok(CacheOperationResult(
                allowed=False,
                intent=intent,
                preview=preview,
                blocked_reason=CacheBlockedReason.INVALID_BUDGET,
                issues=("INVALID_BUDGET_RESERVED",),
            ))

        free_bytes = budget.max_bytes - budget.used_bytes
        if free_bytes < 0 or budget.used_bytes > budget.max_bytes:
            pressure = StoragePressureLevel.CRITICAL
        elif free_bytes <= budget.reserved_bytes:
            pressure = StoragePressureLevel.CRITICAL
        elif free_bytes <= budget.max_bytes * 0.10:
            pressure = StoragePressureLevel.HIGH
        elif free_bytes <= budget.max_bytes * 0.25:
            pressure = StoragePressureLevel.MEDIUM
        elif free_bytes <= budget.max_bytes * 0.50:
            pressure = StoragePressureLevel.LOW
        else:
            pressure = StoragePressureLevel.NONE

        cache_allowed: bool
        needs_confirmation: bool

        if pressure == StoragePressureLevel.CRITICAL:
            cache_allowed = False
            needs_confirmation = False
        elif pressure == StoragePressureLevel.HIGH:
            if mode == CachePolicyMode.AGGRESSIVE:
                cache_allowed = True
                needs_confirmation = True
            else:
                cache_allowed = False
                needs_confirmation = False
        elif pressure == StoragePressureLevel.MEDIUM:
            if mode == CachePolicyMode.AGGRESSIVE:
                cache_allowed = True
                needs_confirmation = False
            elif mode == CachePolicyMode.BALANCED:
                cache_allowed = True
                needs_confirmation = True
            else:
                cache_allowed = False
                needs_confirmation = False
        elif pressure == StoragePressureLevel.LOW:
            if mode == CachePolicyMode.CONSERVATIVE:
                cache_allowed = True
                needs_confirmation = True
            else:
                cache_allowed = True
                needs_confirmation = False
        else:
            cache_allowed = True
            needs_confirmation = False

        if cache_allowed and intent.operation_type == CacheOperationType.ADD_TO_CACHE:
            available = free_bytes - budget.reserved_bytes
            if intent.estimated_size_bytes > available:
                cache_allowed = False
                needs_confirmation = False

        if not cache_allowed:
            blocked = CacheBlockedReason.STORAGE_PRESSURE_CRITICAL if pressure == StoragePressureLevel.CRITICAL else (
                CacheBlockedReason.STORAGE_PRESSURE_HIGH if pressure == StoragePressureLevel.HIGH else CacheBlockedReason.BUDGET_EXCEEDED
            )
            preview = CacheOperationPreview(
                intent=intent,
                allowed=False,
                summary=f"Cache operation blocked due to storage pressure ({pressure.name})",
                confirmation_state=CacheConfirmationState.NOT_REQUIRED,
                blocked_reason=blocked,
            )
            return self._ok(CacheOperationResult(
                allowed=False,
                intent=intent,
                preview=preview,
                blocked_reason=blocked,
            ))

        preview = CacheOperationPreview(
            intent=intent,
            allowed=True,
            summary="Cache operation allowed",
            confirmation_state=CacheConfirmationState.REQUIRED if needs_confirmation else CacheConfirmationState.NOT_REQUIRED,
            estimated_impact_bytes=intent.estimated_size_bytes,
        )
        return self._ok(CacheOperationResult(
            allowed=True,
            intent=intent,
            preview=preview,
        ))

    def _ok(self, data):
        return AriaResult(ok=True, data=data)

    def _err(self, code, message):
        return AriaResult(ok=False, error=AriaError(code=code, message=message))


# ── Storage Pressure Service ───────────────────────────────────

class StoragePressureService:
    """Evaluate storage pressure from explicit budget values only.

    No filesystem traversal or device storage inspection.
    """

    def evaluate_pressure(self, budget: StorageBudget) -> AriaResult[StoragePressureState]:
        if budget.max_bytes <= 0:
            return self._err(
                "INVALID_BUDGET",
                "max_bytes must be positive",
            )

        if budget.reserved_bytes < 0:
            return self._err(
                "INVALID_BUDGET",
                "reserved_bytes must not be negative",
            )

        if budget.reserved_bytes > budget.max_bytes:
            return self._err(
                "INVALID_BUDGET",
                "reserved_bytes exceeds max_bytes",
            )

        if budget.used_bytes < 0:
            return self._err(
                "INVALID_BUDGET",
                "used_bytes must not be negative",
            )

        free_bytes = budget.max_bytes - budget.used_bytes

        if budget.used_bytes > budget.max_bytes:
            return self._ok(StoragePressureState(
                level=StoragePressureLevel.CRITICAL,
                free_bytes=free_bytes,
                max_bytes=budget.max_bytes,
                used_bytes=budget.used_bytes,
                reserved_bytes=budget.reserved_bytes,
                summary="Storage critically full: used_bytes exceeds max_bytes",
            ))

        if free_bytes <= budget.reserved_bytes:
            return self._ok(StoragePressureState(
                level=StoragePressureLevel.CRITICAL,
                free_bytes=free_bytes,
                max_bytes=budget.max_bytes,
                used_bytes=budget.used_bytes,
                reserved_bytes=budget.reserved_bytes,
                summary="Storage critical: free space at or below reserved threshold",
            ))

        if free_bytes <= budget.max_bytes * 0.10:
            return self._ok(StoragePressureState(
                level=StoragePressureLevel.HIGH,
                free_bytes=free_bytes,
                max_bytes=budget.max_bytes,
                used_bytes=budget.used_bytes,
                reserved_bytes=budget.reserved_bytes,
                summary="Storage pressure high: 10% or less free",
            ))

        if free_bytes <= budget.max_bytes * 0.25:
            return self._ok(StoragePressureState(
                level=StoragePressureLevel.MEDIUM,
                free_bytes=free_bytes,
                max_bytes=budget.max_bytes,
                used_bytes=budget.used_bytes,
                reserved_bytes=budget.reserved_bytes,
                summary="Storage pressure medium: 25% or less free",
            ))

        if free_bytes <= budget.max_bytes * 0.50:
            return self._ok(StoragePressureState(
                level=StoragePressureLevel.LOW,
                free_bytes=free_bytes,
                max_bytes=budget.max_bytes,
                used_bytes=budget.used_bytes,
                reserved_bytes=budget.reserved_bytes,
                summary="Storage pressure low: less than 50% free",
            ))

        return self._ok(StoragePressureState(
            level=StoragePressureLevel.NONE,
            free_bytes=free_bytes,
            max_bytes=budget.max_bytes,
            used_bytes=budget.used_bytes,
            reserved_bytes=budget.reserved_bytes,
            summary="No storage pressure detected",
        ))

    def can_accept_operation(
        self,
        budget: StorageBudget,
        estimated_size_bytes: int,
    ) -> AriaResult[bool]:
        if estimated_size_bytes < 0:
            return self._ok(False)

        if budget.max_bytes <= 0:
            return self._ok(False)

        if budget.used_bytes < 0:
            return self._ok(False)

        free_bytes = budget.max_bytes - budget.used_bytes
        if free_bytes <= budget.reserved_bytes:
            return self._ok(False)

        if budget.used_bytes > budget.max_bytes:
            return self._ok(False)

        if estimated_size_bytes > free_bytes - budget.reserved_bytes:
            return self._ok(False)

        return self._ok(True)

    def _ok(self, data):
        return AriaResult(ok=True, data=data)

    def _err(self, code, message):
        return AriaResult(ok=False, error=AriaError(code=code, message=message))


# ── Cache Cleanup Preview Service ──────────────────────────────

class CacheCleanupPreviewService:
    """Preview cache cleanup without deleting files.

    No destructive cleanup, no filesystem access.
    """

    def preview_cleanup(
        self,
        policy: CacheCleanupPolicy,
        budget: StorageBudget,
        candidates: tuple[CacheCleanupItem, ...] = (),
    ) -> AriaResult[CacheCleanupPreview]:
        if budget.max_bytes <= 0:
            return self._err(
                "INVALID_BUDGET",
                "max_bytes must be positive for cleanup preview",
            )

        if policy.max_candidates < 0:
            return self._err(
                "INVALID_POLICY",
                "max_candidates must not be negative",
            )

        if policy.min_age_days < 0:
            return self._err(
                "INVALID_POLICY",
                "min_age_days must not be negative",
            )

        matching = [
            c for c in candidates
            if c.age_days >= policy.min_age_days
        ]

        matching.sort(key=lambda c: (-c.age_days, -c.estimated_size_bytes))

        selected: list[CacheCleanupItem] = []
        total_freed = 0

        for candidate in matching:
            if policy.max_candidates > 0 and len(selected) >= policy.max_candidates:
                break
            if policy.target_bytes > 0 and total_freed >= policy.target_bytes:
                break
            selected.append(candidate)
            total_freed += candidate.estimated_size_bytes

        confirmation_required = total_freed > 0 and policy.target_bytes > 0

        summary = (
            f"Cleanup preview: {len(selected)} item(s), "
            f"~{total_freed} bytes freed"
        ) if selected else "No cleanup candidates match policy"

        return self._ok(CacheCleanupPreview(
            candidates=tuple(selected),
            total_items=len(selected),
            estimated_bytes_freed=total_freed,
            confirmation_required=confirmation_required,
            summary=summary,
        ))

    def evaluate_cleanup_candidates(
        self,
        policy: CacheCleanupPolicy,
        candidates: tuple[CacheCleanupItem, ...] = (),
    ) -> AriaResult[tuple[CacheCleanupItem, ...]]:
        if policy.min_age_days < 0:
            return self._err(
                "INVALID_POLICY",
                "min_age_days must not be negative",
            )

        matching = (
            c for c in candidates
            if c.age_days >= policy.min_age_days
        )

        return self._ok(tuple(matching))

    def _ok(self, data):
        return AriaResult(ok=True, data=data)

    def _err(self, code, message):
        return AriaResult(ok=False, error=AriaError(code=code, message=message))


__all__ = [
    "CacheBlockedReason",
    "CacheCleanupItem",
    "CacheCleanupPolicy",
    "CacheCleanupPreview",
    "CacheCleanupPreviewService",
    "CacheConfirmationState",
    "CacheEligibilityState",
    "CacheItemId",
    "CacheOperationIntent",
    "CacheOperationPreview",
    "CacheOperationResult",
    "CacheOperationType",
    "CachePolicyMode",
    "CachePolicyState",
    "CacheSourceId",
    "OfflineAvailabilityReason",
    "OfflineAvailabilityState",
    "OfflineCachePolicyService",
    "PendingCacheOperation",
    "PendingOperationId",
    "StorageBudget",
    "StoragePressureLevel",
    "StoragePressureService",
    "StoragePressureState",
]
