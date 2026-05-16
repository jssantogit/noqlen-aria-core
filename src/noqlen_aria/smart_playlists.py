"""Smart playlist, saved filter, and smart mix foundations for Aria Core.

Bloco 19 is local-only and evaluates caller-provided app-facing candidates. It
does not create provider playlists, mutate queues, start playback, scan files,
or call network/provider/UI APIs.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, NewType

from noqlen_aria.contracts import AriaError, AriaResult
from noqlen_aria.library import LibraryItemSummary

SmartPlaylistId = NewType("SmartPlaylistId", str)
SavedFilterId = NewType("SavedFilterId", str)
SmartMixSeed = NewType("SmartMixSeed", str)


class SmartPlaylistRuleOperator(Enum):
    EQUALS = auto()
    NOT_EQUALS = auto()
    CONTAINS = auto()
    NOT_CONTAINS = auto()
    GREATER_THAN = auto()
    LESS_THAN = auto()
    IS_TRUE = auto()
    IS_FALSE = auto()
    IS_PRESENT = auto()
    IS_MISSING = auto()
    UNSUPPORTED = auto()


class SmartPlaylistValidationIssue(Enum):
    EMPTY_RULE_GROUP = auto()
    UNSUPPORTED_FIELD = auto()
    UNSUPPORTED_OPERATOR = auto()
    MISSING_RULE_VALUE = auto()
    INVALID_LIMIT = auto()
    UNSUPPORTED_SORT_FIELD = auto()
    MISSING_METADATA = auto()


class SmartPlaylistUnavailableReason(Enum):
    NONE = auto()
    INVALID_DEFINITION = auto()
    UNSUPPORTED_FIELD = auto()
    UNSUPPORTED_OPERATOR = auto()
    MISSING_METADATA = auto()
    PROVIDER_WRITE_UNSUPPORTED = auto()


class SmartMixStrategy(Enum):
    PRESERVE_ORDER = auto()
    DETERMINISTIC_SHUFFLE = auto()
    MOST_RECENTLY_ADDED = auto()
    MOST_RECENTLY_PLAYED = auto()


class SavedFilterValidationIssue(Enum):
    INVALID_RULE_GROUP = auto()
    UNSUPPORTED_FIELD = auto()
    UNSUPPORTED_OPERATOR = auto()
    INVALID_LIMIT = auto()
    UNSUPPORTED_SORT_FIELD = auto()
    MISSING_METADATA = auto()


@dataclass(frozen=True)
class SmartPlaylistRule:
    field: str
    operator: SmartPlaylistRuleOperator
    value: Any = None
    required: bool = True


@dataclass(frozen=True)
class SmartPlaylistRuleGroup:
    rules: tuple[SmartPlaylistRule, ...] = field(default_factory=tuple)
    groups: tuple["SmartPlaylistRuleGroup", ...] = field(default_factory=tuple)
    match_all: bool = True


@dataclass(frozen=True)
class SmartPlaylistSortRule:
    field: str = "display_name"
    descending: bool = False


@dataclass(frozen=True)
class SmartPlaylistLimit:
    max_items: int | None = None


@dataclass(frozen=True)
class SmartPlaylistItemCandidate:
    item: LibraryItemSummary
    artist_name: str = ""
    album_name: str = ""
    genre: str = ""
    favorite: bool | None = None
    recently_added: bool | None = None
    recently_played: bool | None = None
    play_count: int | None = None
    rating: float | None = None
    duration_seconds: int | None = None
    extras: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SmartPlaylistDefinition:
    playlist_id: SmartPlaylistId
    display_name: str
    root_group: SmartPlaylistRuleGroup
    sort_rules: tuple[SmartPlaylistSortRule, ...] = field(default_factory=tuple)
    limit: SmartPlaylistLimit = field(default_factory=SmartPlaylistLimit)


@dataclass(frozen=True)
class SmartPlaylistSummary:
    playlist_id: SmartPlaylistId
    display_name: str
    rule_count: int = 0
    preview_count: int = 0
    available: bool = True


@dataclass(frozen=True)
class SmartPlaylistEvaluationContext:
    candidates: tuple[SmartPlaylistItemCandidate, ...] = field(default_factory=tuple)
    deterministic_seed: SmartMixSeed = SmartMixSeed("aria-smart-playlists")


@dataclass(frozen=True)
class SmartPlaylistEvaluationResult:
    definition: SmartPlaylistDefinition
    matched_items: tuple[SmartPlaylistItemCandidate, ...] = field(default_factory=tuple)
    available: bool = True
    partial: bool = False
    issues: tuple[SmartPlaylistValidationIssue, ...] = field(default_factory=tuple)
    unavailable_reasons: tuple[SmartPlaylistUnavailableReason, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class SmartPlaylistPreview:
    definition: SmartPlaylistDefinition
    items: tuple[LibraryItemSummary, ...] = field(default_factory=tuple)
    available: bool = True
    partial: bool = False
    issues: tuple[SmartPlaylistValidationIssue, ...] = field(default_factory=tuple)
    unavailable_reasons: tuple[SmartPlaylistUnavailableReason, ...] = field(default_factory=tuple)
    provider_playlist_created: bool = False
    queue_mutated: bool = False
    playback_started: bool = False


@dataclass(frozen=True)
class SmartMixDefinition:
    display_name: str
    root_group: SmartPlaylistRuleGroup = field(default_factory=SmartPlaylistRuleGroup)
    strategy: SmartMixStrategy = SmartMixStrategy.DETERMINISTIC_SHUFFLE
    seed: SmartMixSeed = SmartMixSeed("aria-smart-mix")
    limit: SmartPlaylistLimit = field(default_factory=SmartPlaylistLimit)


@dataclass(frozen=True)
class SmartMixPreview:
    definition: SmartMixDefinition
    items: tuple[LibraryItemSummary, ...] = field(default_factory=tuple)
    available: bool = True
    partial: bool = False
    issues: tuple[SmartPlaylistValidationIssue, ...] = field(default_factory=tuple)
    unavailable_reasons: tuple[SmartPlaylistUnavailableReason, ...] = field(default_factory=tuple)
    queue_mutated: bool = False
    playback_started: bool = False


@dataclass(frozen=True)
class SavedFilterDefinition:
    filter_id: SavedFilterId
    display_name: str
    root_group: SmartPlaylistRuleGroup
    sort_rules: tuple[SmartPlaylistSortRule, ...] = field(default_factory=tuple)
    limit: SmartPlaylistLimit = field(default_factory=SmartPlaylistLimit)


@dataclass(frozen=True)
class SavedFilterPreview:
    definition: SavedFilterDefinition
    items: tuple[LibraryItemSummary, ...] = field(default_factory=tuple)
    available: bool = True
    partial: bool = False
    issues: tuple[SavedFilterValidationIssue, ...] = field(default_factory=tuple)


class SmartPlaylistService:
    _SUPPORTED_FIELDS = frozenset({
        "display_name",
        "subtitle",
        "item_kind",
        "artist_name",
        "album_name",
        "genre",
        "favorite",
        "recently_added",
        "recently_played",
        "play_count",
        "rating",
        "duration_seconds",
    })
    _VALUE_OPERATORS = frozenset({
        SmartPlaylistRuleOperator.EQUALS,
        SmartPlaylistRuleOperator.NOT_EQUALS,
        SmartPlaylistRuleOperator.CONTAINS,
        SmartPlaylistRuleOperator.NOT_CONTAINS,
        SmartPlaylistRuleOperator.GREATER_THAN,
        SmartPlaylistRuleOperator.LESS_THAN,
    })

    def validate_definition(self, definition: SmartPlaylistDefinition) -> tuple[SmartPlaylistValidationIssue, ...]:
        issues = self.validate_rule_group(definition.root_group)
        issues += self._validate_sort_and_limit(definition.sort_rules, definition.limit)
        return _dedupe_issues(issues)

    def validate_rule_group(self, group: SmartPlaylistRuleGroup) -> tuple[SmartPlaylistValidationIssue, ...]:
        issues: tuple[SmartPlaylistValidationIssue, ...] = ()
        if not group.rules and not group.groups:
            issues += (SmartPlaylistValidationIssue.EMPTY_RULE_GROUP,)
        for rule in group.rules:
            issues += self._validate_rule(rule)
        for child in group.groups:
            issues += self.validate_rule_group(child)
        return issues

    def evaluate(
        self,
        definition: SmartPlaylistDefinition,
        context: SmartPlaylistEvaluationContext,
    ) -> AriaResult[SmartPlaylistEvaluationResult]:
        validation_issues = self.validate_definition(definition)
        blocking_issues = tuple(
            issue for issue in validation_issues
            if issue != SmartPlaylistValidationIssue.MISSING_METADATA
        )
        if blocking_issues:
            return AriaResult(
                ok=True,
                data=SmartPlaylistEvaluationResult(
                    definition=definition,
                    available=False,
                    issues=validation_issues,
                    unavailable_reasons=_reasons_for_issues(validation_issues),
                ),
            )

        matched: list[SmartPlaylistItemCandidate] = []
        runtime_issues: tuple[SmartPlaylistValidationIssue, ...] = ()
        for candidate in context.candidates:
            matches, issues = self._matches_group(candidate, definition.root_group)
            runtime_issues += issues
            if matches:
                matched.append(candidate)
        all_issues = _dedupe_issues(validation_issues + runtime_issues)
        items = self._sort_items(tuple(matched), definition.sort_rules)
        items = self._apply_limit(items, definition.limit)
        return AriaResult(
            ok=True,
            data=SmartPlaylistEvaluationResult(
                definition=definition,
                matched_items=items,
                available=SmartPlaylistValidationIssue.MISSING_METADATA not in all_issues,
                partial=SmartPlaylistValidationIssue.MISSING_METADATA in all_issues,
                issues=all_issues,
                unavailable_reasons=_reasons_for_issues(all_issues),
            ),
        )

    def build_preview(
        self,
        definition: SmartPlaylistDefinition,
        context: SmartPlaylistEvaluationContext,
    ) -> AriaResult[SmartPlaylistPreview]:
        result = self.evaluate(definition, context)
        if result.is_err():
            return AriaResult(ok=False, error=result.error)
        assert result.data is not None
        return AriaResult(
            ok=True,
            data=SmartPlaylistPreview(
                definition=definition,
                items=tuple(candidate.item for candidate in result.data.matched_items),
                available=result.data.available,
                partial=result.data.partial,
                issues=result.data.issues,
                unavailable_reasons=result.data.unavailable_reasons,
            ),
        )

    def build_smart_mix_preview(
        self,
        definition: SmartMixDefinition,
        context: SmartPlaylistEvaluationContext,
    ) -> AriaResult[SmartMixPreview]:
        playlist_definition = SmartPlaylistDefinition(
            playlist_id=SmartPlaylistId("smart-mix-preview"),
            display_name=definition.display_name,
            root_group=definition.root_group,
            limit=SmartPlaylistLimit(),
        )
        evaluation = self.evaluate(playlist_definition, context)
        if evaluation.is_err():
            return AriaResult(ok=False, error=evaluation.error)
        assert evaluation.data is not None
        items = evaluation.data.matched_items
        if definition.strategy == SmartMixStrategy.DETERMINISTIC_SHUFFLE:
            items = self._deterministic_shuffle(items, definition.seed)
        elif definition.strategy == SmartMixStrategy.MOST_RECENTLY_ADDED:
            items = self._sort_items(items, (SmartPlaylistSortRule("recently_added", descending=True),))
        elif definition.strategy == SmartMixStrategy.MOST_RECENTLY_PLAYED:
            items = self._sort_items(items, (SmartPlaylistSortRule("recently_played", descending=True),))
        items = self._apply_limit(items, definition.limit)
        return AriaResult(
            ok=True,
            data=SmartMixPreview(
                definition=definition,
                items=tuple(candidate.item for candidate in items),
                available=evaluation.data.available,
                partial=evaluation.data.partial,
                issues=evaluation.data.issues,
                unavailable_reasons=evaluation.data.unavailable_reasons,
            ),
        )

    def request_provider_playlist_creation(self, preview: SmartPlaylistPreview) -> AriaResult[bool]:
        _ = preview
        return AriaResult(
            ok=False,
            error=AriaError(
                code="PROVIDER_PLAYLIST_CREATION_UNSUPPORTED",
                message="Smart playlist provider creation is a future intent and is not performed by Aria Core",
            ),
        )

    def summary_from_preview(self, preview: SmartPlaylistPreview) -> SmartPlaylistSummary:
        return SmartPlaylistSummary(
            playlist_id=preview.definition.playlist_id,
            display_name=preview.definition.display_name,
            rule_count=self._rule_count(preview.definition.root_group),
            preview_count=len(preview.items),
            available=preview.available,
        )

    def _validate_rule(self, rule: SmartPlaylistRule) -> tuple[SmartPlaylistValidationIssue, ...]:
        issues: tuple[SmartPlaylistValidationIssue, ...] = ()
        if rule.field not in self._SUPPORTED_FIELDS:
            issues += (SmartPlaylistValidationIssue.UNSUPPORTED_FIELD,)
        if rule.operator == SmartPlaylistRuleOperator.UNSUPPORTED:
            issues += (SmartPlaylistValidationIssue.UNSUPPORTED_OPERATOR,)
        if rule.operator in self._VALUE_OPERATORS and rule.value is None:
            issues += (SmartPlaylistValidationIssue.MISSING_RULE_VALUE,)
        return issues

    def _validate_sort_and_limit(
        self,
        sort_rules: tuple[SmartPlaylistSortRule, ...],
        limit: SmartPlaylistLimit,
    ) -> tuple[SmartPlaylistValidationIssue, ...]:
        issues: tuple[SmartPlaylistValidationIssue, ...] = ()
        for sort_rule in sort_rules:
            if sort_rule.field not in self._SUPPORTED_FIELDS:
                issues += (SmartPlaylistValidationIssue.UNSUPPORTED_SORT_FIELD,)
        if limit.max_items is not None and limit.max_items < 1:
            issues += (SmartPlaylistValidationIssue.INVALID_LIMIT,)
        return issues

    def _matches_group(
        self,
        candidate: SmartPlaylistItemCandidate,
        group: SmartPlaylistRuleGroup,
    ) -> tuple[bool, tuple[SmartPlaylistValidationIssue, ...]]:
        results: list[bool] = []
        issues: tuple[SmartPlaylistValidationIssue, ...] = ()
        for rule in group.rules:
            matches, rule_issues = self._matches_rule(candidate, rule)
            results.append(matches)
            issues += rule_issues
        for child in group.groups:
            matches, child_issues = self._matches_group(candidate, child)
            results.append(matches)
            issues += child_issues
        if not results:
            return False, issues
        return (all(results) if group.match_all else any(results)), issues

    def _matches_rule(
        self,
        candidate: SmartPlaylistItemCandidate,
        rule: SmartPlaylistRule,
    ) -> tuple[bool, tuple[SmartPlaylistValidationIssue, ...]]:
        present, value = self._field_value(candidate, rule.field)
        if rule.operator == SmartPlaylistRuleOperator.IS_MISSING:
            return not present, ()
        if not present:
            issue = (SmartPlaylistValidationIssue.MISSING_METADATA,) if rule.required else ()
            return False, issue
        if rule.operator == SmartPlaylistRuleOperator.IS_PRESENT:
            return True, ()
        if rule.operator == SmartPlaylistRuleOperator.IS_TRUE:
            return value is True, ()
        if rule.operator == SmartPlaylistRuleOperator.IS_FALSE:
            return value is False, ()
        if rule.operator == SmartPlaylistRuleOperator.EQUALS:
            return _comparable(value) == _comparable(rule.value), ()
        if rule.operator == SmartPlaylistRuleOperator.NOT_EQUALS:
            return _comparable(value) != _comparable(rule.value), ()
        if rule.operator == SmartPlaylistRuleOperator.CONTAINS:
            return str(rule.value).casefold() in str(value).casefold(), ()
        if rule.operator == SmartPlaylistRuleOperator.NOT_CONTAINS:
            return str(rule.value).casefold() not in str(value).casefold(), ()
        if rule.operator == SmartPlaylistRuleOperator.GREATER_THAN:
            return _numeric(value) > _numeric(rule.value), ()
        if rule.operator == SmartPlaylistRuleOperator.LESS_THAN:
            return _numeric(value) < _numeric(rule.value), ()
        return False, (SmartPlaylistValidationIssue.UNSUPPORTED_OPERATOR,)

    def _field_value(self, candidate: SmartPlaylistItemCandidate, field_name: str) -> tuple[bool, Any]:
        if field_name == "display_name":
            return True, candidate.item.display_name
        if field_name == "subtitle":
            return bool(candidate.item.subtitle), candidate.item.subtitle
        if field_name == "item_kind":
            return True, candidate.item.item_kind.name
        if field_name in candidate.extras:
            return candidate.extras[field_name] is not None, candidate.extras[field_name]
        value = getattr(candidate, field_name, None)
        if isinstance(value, str):
            return bool(value), value
        return value is not None, value

    def _sort_items(
        self,
        items: tuple[SmartPlaylistItemCandidate, ...],
        sort_rules: tuple[SmartPlaylistSortRule, ...],
    ) -> tuple[SmartPlaylistItemCandidate, ...]:
        sorted_items = tuple(items)
        for sort_rule in reversed(sort_rules):
            sorted_items = tuple(
                item for _, item in sorted(
                    enumerate(sorted_items),
                    key=lambda indexed: (self._sort_value(indexed[1], sort_rule.field), indexed[0], str(indexed[1].item.item_id)),
                    reverse=sort_rule.descending,
                )
            )
        return sorted_items

    def _sort_value(self, candidate: SmartPlaylistItemCandidate, field_name: str) -> Any:
        present, value = self._field_value(candidate, field_name)
        if not present:
            return ""
        if isinstance(value, str):
            return value.casefold()
        if isinstance(value, bool):
            return int(value)
        return value

    def _apply_limit(
        self,
        items: tuple[SmartPlaylistItemCandidate, ...],
        limit: SmartPlaylistLimit,
    ) -> tuple[SmartPlaylistItemCandidate, ...]:
        if limit.max_items is None:
            return items
        return items[: limit.max_items]

    def _deterministic_shuffle(
        self,
        items: tuple[SmartPlaylistItemCandidate, ...],
        seed: SmartMixSeed,
    ) -> tuple[SmartPlaylistItemCandidate, ...]:
        return tuple(
            item for _, item in sorted(
                enumerate(items),
                key=lambda indexed: (_stable_mix_key(indexed[1], seed, indexed[0]), indexed[0]),
            )
        )

    def _rule_count(self, group: SmartPlaylistRuleGroup) -> int:
        return len(group.rules) + sum(self._rule_count(child) for child in group.groups)


class SavedFilterService:
    def __init__(self, smart_playlist_service: SmartPlaylistService | None = None) -> None:
        self._smart_playlist_service = smart_playlist_service or SmartPlaylistService()

    def validate_definition(self, definition: SavedFilterDefinition) -> tuple[SavedFilterValidationIssue, ...]:
        playlist_definition = self._as_playlist_definition(definition)
        return _saved_filter_issues(self._smart_playlist_service.validate_definition(playlist_definition))

    def build_preview(
        self,
        definition: SavedFilterDefinition,
        candidates: tuple[SmartPlaylistItemCandidate, ...],
    ) -> AriaResult[SavedFilterPreview]:
        playlist_definition = self._as_playlist_definition(definition)
        result = self._smart_playlist_service.evaluate(
            playlist_definition,
            SmartPlaylistEvaluationContext(candidates=candidates),
        )
        if result.is_err():
            return AriaResult(ok=False, error=result.error)
        assert result.data is not None
        return AriaResult(
            ok=True,
            data=SavedFilterPreview(
                definition=definition,
                items=tuple(candidate.item for candidate in result.data.matched_items),
                available=result.data.available,
                partial=result.data.partial,
                issues=_saved_filter_issues(result.data.issues),
            ),
        )

    def _as_playlist_definition(self, definition: SavedFilterDefinition) -> SmartPlaylistDefinition:
        return SmartPlaylistDefinition(
            playlist_id=SmartPlaylistId(str(definition.filter_id)),
            display_name=definition.display_name,
            root_group=definition.root_group,
            sort_rules=definition.sort_rules,
            limit=definition.limit,
        )


class FakeSmartPlaylistScenarios:
    @staticmethod
    def candidates() -> tuple[SmartPlaylistItemCandidate, ...]:
        from noqlen_aria.media_source import MediaId, MediaIdKind, MediaSourceId

        source_id = MediaSourceId("fake-source-1")
        return (
            SmartPlaylistItemCandidate(
                item=LibraryItemSummary(source_id, MediaId("track-1"), MediaIdKind.TRACK, "First Difference", "Ada Quartet"),
                artist_name="Ada Quartet",
                album_name="Analytical Engines",
                genre="Instrumental",
                favorite=True,
                recently_added=False,
                recently_played=True,
                play_count=7,
                rating=4.5,
                duration_seconds=180,
            ),
            SmartPlaylistItemCandidate(
                item=LibraryItemSummary(source_id, MediaId("track-2"), MediaIdKind.TRACK, "Safe Folder Song", "Ada Quartet"),
                artist_name="Ada Quartet",
                album_name="Analytical Engines",
                genre="Instrumental",
                favorite=False,
                recently_added=True,
                recently_played=None,
                play_count=1,
                rating=3.0,
                duration_seconds=210,
            ),
            SmartPlaylistItemCandidate(
                item=LibraryItemSummary(source_id, MediaId("track-3"), MediaIdKind.TRACK, "Quiet Validation", "Noqlen Trio"),
                artist_name="Noqlen Trio",
                album_name="Boundary Tests",
                genre="Ambient",
                favorite=True,
                recently_added=True,
                recently_played=False,
                play_count=2,
                rating=5.0,
                duration_seconds=240,
            ),
        )

    @staticmethod
    def empty_candidates() -> tuple[SmartPlaylistItemCandidate, ...]:
        return ()

    @staticmethod
    def favorite_tracks_definition() -> SmartPlaylistDefinition:
        return SmartPlaylistDefinition(
            playlist_id=SmartPlaylistId("favorites"),
            display_name="Favorite Tracks",
            root_group=SmartPlaylistRuleGroup((SmartPlaylistRule("favorite", SmartPlaylistRuleOperator.IS_TRUE),)),
        )


def _dedupe_issues(issues: tuple[SmartPlaylistValidationIssue, ...]) -> tuple[SmartPlaylistValidationIssue, ...]:
    output: tuple[SmartPlaylistValidationIssue, ...] = ()
    for issue in issues:
        if issue not in output:
            output += (issue,)
    return output


def _reasons_for_issues(issues: tuple[SmartPlaylistValidationIssue, ...]) -> tuple[SmartPlaylistUnavailableReason, ...]:
    mapping = {
        SmartPlaylistValidationIssue.EMPTY_RULE_GROUP: SmartPlaylistUnavailableReason.INVALID_DEFINITION,
        SmartPlaylistValidationIssue.UNSUPPORTED_FIELD: SmartPlaylistUnavailableReason.UNSUPPORTED_FIELD,
        SmartPlaylistValidationIssue.UNSUPPORTED_OPERATOR: SmartPlaylistUnavailableReason.UNSUPPORTED_OPERATOR,
        SmartPlaylistValidationIssue.MISSING_RULE_VALUE: SmartPlaylistUnavailableReason.INVALID_DEFINITION,
        SmartPlaylistValidationIssue.INVALID_LIMIT: SmartPlaylistUnavailableReason.INVALID_DEFINITION,
        SmartPlaylistValidationIssue.UNSUPPORTED_SORT_FIELD: SmartPlaylistUnavailableReason.UNSUPPORTED_FIELD,
        SmartPlaylistValidationIssue.MISSING_METADATA: SmartPlaylistUnavailableReason.MISSING_METADATA,
    }
    output: tuple[SmartPlaylistUnavailableReason, ...] = ()
    for issue in issues:
        reason = mapping[issue]
        if reason not in output:
            output += (reason,)
    return output or (SmartPlaylistUnavailableReason.NONE,)


def _saved_filter_issues(issues: tuple[SmartPlaylistValidationIssue, ...]) -> tuple[SavedFilterValidationIssue, ...]:
    mapping = {
        SmartPlaylistValidationIssue.EMPTY_RULE_GROUP: SavedFilterValidationIssue.INVALID_RULE_GROUP,
        SmartPlaylistValidationIssue.UNSUPPORTED_FIELD: SavedFilterValidationIssue.UNSUPPORTED_FIELD,
        SmartPlaylistValidationIssue.UNSUPPORTED_OPERATOR: SavedFilterValidationIssue.UNSUPPORTED_OPERATOR,
        SmartPlaylistValidationIssue.MISSING_RULE_VALUE: SavedFilterValidationIssue.INVALID_RULE_GROUP,
        SmartPlaylistValidationIssue.INVALID_LIMIT: SavedFilterValidationIssue.INVALID_LIMIT,
        SmartPlaylistValidationIssue.UNSUPPORTED_SORT_FIELD: SavedFilterValidationIssue.UNSUPPORTED_SORT_FIELD,
        SmartPlaylistValidationIssue.MISSING_METADATA: SavedFilterValidationIssue.MISSING_METADATA,
    }
    output: tuple[SavedFilterValidationIssue, ...] = ()
    for issue in issues:
        saved_issue = mapping[issue]
        if saved_issue not in output:
            output += (saved_issue,)
    return output


def _comparable(value: Any) -> Any:
    return value.casefold() if isinstance(value, str) else value


def _numeric(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _stable_mix_key(candidate: SmartPlaylistItemCandidate, seed: SmartMixSeed, index: int) -> str:
    text = "|".join((str(seed), str(candidate.item.source_id), str(candidate.item.item_id), candidate.item.display_name, str(index)))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


__all__ = [
    "FakeSmartPlaylistScenarios",
    "SavedFilterDefinition",
    "SavedFilterId",
    "SavedFilterPreview",
    "SavedFilterService",
    "SavedFilterValidationIssue",
    "SmartMixDefinition",
    "SmartMixPreview",
    "SmartMixSeed",
    "SmartMixStrategy",
    "SmartPlaylistDefinition",
    "SmartPlaylistEvaluationContext",
    "SmartPlaylistEvaluationResult",
    "SmartPlaylistId",
    "SmartPlaylistItemCandidate",
    "SmartPlaylistLimit",
    "SmartPlaylistPreview",
    "SmartPlaylistRule",
    "SmartPlaylistRuleGroup",
    "SmartPlaylistRuleOperator",
    "SmartPlaylistService",
    "SmartPlaylistSortRule",
    "SmartPlaylistSummary",
    "SmartPlaylistUnavailableReason",
    "SmartPlaylistValidationIssue",
]
