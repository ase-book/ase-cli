# scaffold-command Specification

## Purpose
Define the Intent Engineering project structure created and maintained by `iec init`.
## Requirements
### Requirement: Init creates canonical directory structure
The `iec init` command SHALL create the full canonical Intent Engineering directory structure in the target directory, including all subdirectories and stub files.

#### Scenario: Init in empty directory [SCAFFOLD-001]

Test-type: integration

- **WHEN** `iec init` is run in a directory with no Intent Engineering structure
- **THEN** all directories are created: `docs/architecture/`, `docs/decisions/`, `docs/design/`, `openspec/changes/archive/`, `openspec/specs/`, `.agents/instructions/`, `.agents/commands/`, `.agents/skills/`, `.agents/hooks/`
- **AND** all stub files are created: `AGENTS.md`, `docs/README.md`, `docs/INDEX.md`, `docs/decisions/README.md`, `docs/design/README.md`
- **AND** `docs/testing-convention.md` is created with full Intent Engineering testing convention content
- **AND** `docs/testing-strategy.md` is created as a stub referencing `testing-convention.md`

#### Scenario: Init in directory with partial structure [SCAFFOLD-002]

Test-type: integration

- **WHEN** `iec init` is run where some Intent Engineering directories already exist but others are missing
- **THEN** missing directories and files are created
- **AND** existing files are NOT overwritten

#### Scenario: Init in fully initialized directory [SCAFFOLD-003]

Test-type: integration

- **WHEN** `iec init` is run in a directory that already has the full Intent Engineering structure
- **THEN** no files are created or overwritten
- **AND** the command reports that the directory is already initialized

### Requirement: AGENTS.md skeleton follows TOC pattern
The generated `AGENTS.md` SHALL follow the TOC pattern: a short header (project name, language, framework), an instructions section linking to `.agents/instructions/` files, and a reference to `docs/INDEX.md`.

#### Scenario: AGENTS.md content structure [SCAFFOLD-004]

Test-type: unit

- **WHEN** `iec init` creates `AGENTS.md`
- **THEN** the file contains a project section with placeholder for name/language/framework
- **AND** contains a link to `docs/INDEX.md` as the full documentation map
- **AND** the file is under 25 lines

### Requirement: Init respects --dry-run
The `--dry-run` flag SHALL print all files and directories that would be created without touching the filesystem.

#### Scenario: Dry run on empty directory [SCAFFOLD-005]

Test-type: integration

- **WHEN** `iec init --dry-run` is run in an empty directory
- **THEN** all directories and files that would be created are listed in the output
- **AND** no files or directories are actually created

#### Scenario: Dry run on partially initialized directory [SCAFFOLD-006]

Test-type: integration

- **WHEN** `iec init --dry-run` is run where some Intent Engineering directories exist
- **THEN** only the missing directories and files are listed
- **AND** existing items are noted as "already exists" or omitted

### Requirement: Init respects --force
The `--force` flag SHALL overwrite existing Intent Engineering files with fresh generated content.

#### Scenario: Force overwrite of existing AGENTS.md [SCAFFOLD-007]

Test-type: integration

- **WHEN** `iec init --force` is run and `AGENTS.md` already exists
- **THEN** the existing `AGENTS.md` is overwritten with the generated skeleton
- **AND** directories that exist are not recreated (only files are overwritten)

#### Scenario: Force on fully initialized directory [SCAFFOLD-008]

Test-type: integration

- **WHEN** `iec init --force` is run in a fully initialized directory
- **THEN** all stub files are overwritten with fresh content
- **AND** directory structure is verified but not recreated

### Requirement: Init supports --path targeting
The `--path` flag SHALL target a specific directory for initialization instead of the current working directory.

#### Scenario: Init with explicit path [SCAFFOLD-009]

Test-type: integration

- **WHEN** `iec init --path /tmp/my-project` is run
- **THEN** the Intent Engineering structure is created under `/tmp/my-project/`
- **AND** the current working directory is unaffected

#### Scenario: Init with relative path [SCAFFOLD-010]

Test-type: integration

- **WHEN** `iec init --path ../other-repo` is run
- **THEN** the Intent Engineering structure is created under the resolved `../other-repo/` path

#### Scenario: Init with non-existent path [SCAFFOLD-011]

Test-type: integration

- **WHEN** `iec init --path /nonexistent/dir` is run
- **THEN** the target directory is created first, then the Intent Engineering structure is scaffolded inside it

### Requirement: Testing convention and strategy are scaffolded
The `iec init` command SHALL create `docs/testing-convention.md` with the full generic Intent Engineering testing conventions and `docs/testing-strategy.md` as a project-specific stub.

#### Scenario: testing-convention.md contains canonical content [SCAFFOLD-012]

Test-type: unit

- **WHEN** `iec init` creates `docs/testing-convention.md`
- **THEN** the content defines the test layer taxonomy (Unit, Slice, Integration, E2E, Performance, Baseline, Architectural, Manual, Sanity)
- **AND** defines the AC ID format (`[PREFIX-NNN]`)
- **AND** defines the `Test-type:` field contract
- **AND** defines positive and negative evidence requirements
- **AND** defines traceability marker conventions
- **AND** is under 300 lines

#### Scenario: testing-strategy.md is a project stub [SCAFFOLD-013]

Test-type: unit

- **WHEN** `iec init` creates `docs/testing-strategy.md`
- **THEN** the stub references `testing-convention.md`
- **AND** includes placeholder sections for test tools, CI wiring, and directory layout

### Requirement: Empty directories contain .gitkeep files
The `iec init` command SHALL place `.gitkeep` files in directories that would otherwise be empty after scaffolding, so they are tracked by Git.

#### Scenario: .gitkeep placed in empty directories [SCAFFOLD-014]

Test-type: integration

- **WHEN** `iec init` is run in an empty directory
- **THEN** `.gitkeep` files are created in: `docs/architecture/`, `openspec/changes/archive/`, `openspec/specs/`, `.agents/instructions/`, `.agents/commands/`, `.agents/skills/`, `.agents/hooks/`
- **AND** directories that contain stub files (e.g., `docs/decisions/` with README.md) do NOT get a `.gitkeep`

### Requirement: CLI provides --help and --version
The `iec` CLI SHALL display usage via `--help` and version via `--version`.

#### Scenario: --help shows command reference [SCAFFOLD-015]

Test-type: integration

- **WHEN** `iec --help` is run
- **THEN** the output lists available commands including `init`
- **AND** describes each command's purpose

#### Scenario: --version shows version number [SCAFFOLD-016]

Test-type: integration

- **WHEN** `iec --version` is run
- **THEN** the output matches the version in `pyproject.toml`
- **AND** the command exits with code 0
