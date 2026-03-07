"""Phase 7 models: Process, Code Quality, Testing, Version Control (HOW-TO-WORK)."""

from pydantic import BaseModel, Field

from sdwc_api.schemas.enums import (
    BranchStrategy,
    CommitConvention,
    DbTestStrategy,
    ExternalServiceStrategy,
    Methodology,
    PrCreatedBy,
    RepoStructure,
    TestApproach,
    TestDataStrategy,
    TestFrameworkEnum,
    TestLevel,
)

# --- Process ---


class Process(BaseModel):
    """Development process configuration.

    CRITICAL: The `methodology` field controls CLAUDE.md branching.
    """

    methodology: Methodology
    sprint_length: str | None = None
    wip_limit: str | None = None
    task_review_minutes: str | None = None
    definition_of_done: list[str] | None = None


# --- Code Quality ---


class CodingStandard(BaseModel):
    """Coding standard for a language."""

    language: str
    style_guide: str
    linter: str
    formatter: str


class CodeReview(BaseModel):
    """Code review policy."""

    required: bool = True
    min_reviewers: int = 1
    auto_merge_allowed: bool = False


class Documentation(BaseModel):
    """Documentation policy."""

    code_comments: str | None = None
    adr_usage: str | None = None
    changelog_policy: str | None = None


class CodeQuality(BaseModel):
    """Code quality configuration."""

    coding_standards: list[CodingStandard] | None = None
    code_review: CodeReview | None = None
    documentation: Documentation | None = None


# --- Testing ---


class TestLevelConfig(BaseModel):
    """Configuration for a specific test level."""

    level: TestLevel
    framework: TestFrameworkEnum
    coverage_target: str | None = None
    approach: str | None = None


class TestEnvironment(BaseModel):
    """Test environment configuration."""

    db_strategy: DbTestStrategy | None = None
    external_service_strategy: ExternalServiceStrategy | None = None


class Testing(BaseModel):
    """Testing configuration."""

    approach: TestApproach
    levels: list[TestLevelConfig] = Field(min_length=1)
    test_data_strategy: TestDataStrategy | None = None
    test_environment: TestEnvironment | None = None


# --- Version Control ---


class PrPolicy(BaseModel):
    """Pull request policy."""

    created_by: PrCreatedBy | None = None
    template_required: bool = True
    squash_merge: bool = True


class VersionControl(BaseModel):
    """Version control configuration."""

    branch_strategy: BranchStrategy
    branch_strategy_description: str | None = None
    commit_convention: CommitConvention | None = None
    monorepo_or_polyrepo: RepoStructure | None = None
    pr_policy: PrPolicy | None = None
