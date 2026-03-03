# SDwC


> Survey-driven project documentation generator optimized for AI-assisted development with Claude Code

---

## 1. 개요

SDwC automates the creation of CLAUDE.md, project docs, and coding skills from a single YAML survey. Developers fill in a structured template, and SDwC generates a complete documentation package that enables Claude Code to understand project context from day one.

---

## 2. 문제 정의

### 2.1 핵심 문제

Developers using Claude Code lack structured project documentation, leading to wasted time on rework and inability to leverage AI collaboration features effectively

### 2.2 이 문제를 겪는 사람

Developers who use or want to use Claude Code for software development

- **심각도**: high
- **빈도**: daily

### 2.3 현재 해결 방법과 한계

Copy-paste community CLAUDE.md templates or start coding without documentation

**문제점:**

- Copied templates lack project-specific context, making Claude ineffective
- Without upfront design, rework costs accumulate as the project grows
- CLAUDE.md and skills features require learning time that many developers skip
- Without clear task units, developers cannot keep pace with AI output and lose control of the project direction


---

## 3. 왜 지금인가

Claude Code adoption is growing rapidly, but most developers struggle to set up proper AI collaboration environments

- **트리거**: Personal experience with excessive rework due to insufficient initial design when developing with Claude Code

### 기회비용

Every new project without SDwC repeats the same painful initialization process


---

## 4. 핵심 가치 제안

- **핵심 가치**: Fill in a survey once, get a complete AI-ready project documentation package instantly
- **차별점**: Generates not just documentation but also CLAUDE.md and framework-specific coding skills tailored to the project, covering 34 frameworks

- **가설**: Developers who start with structured documentation will experience significantly less rework and maintain better control over AI-assisted development

---

## 5. 대상 사용자

### 5.1 사용자 페르소나

#### Newcomer (핵심)

- **설명**: Developer who is new to Claude Code and wants to start a project with proper AI collaboration setup
- **핵심 목표**: Set up a well-structured project environment for Claude Code without learning CLAUDE.md and skills syntax
- **페인 포인트**:
  - Doesn't know how to write CLAUDE.md or configure skills
  - Spends too much time on initial project setup instead of actual development
  - Copies community templates that don't fit their specific project
- **기술 수준**: intermediate
- **사용 빈도**: monthly

#### Experienced Dev

- **설명**: Developer already using Claude Code but without systematic documentation
- **핵심 목표**: Get consistent, high-quality project documentation to improve AI collaboration efficiency
- **페인 포인트**:
  - Rework from insufficient initial design accumulates over time
  - Without task-level structure, cannot keep pace with AI output
  - Each new project requires re-creating documentation from scratch
- **기술 수준**: expert
- **사용 빈도**: monthly


### 5.2 안티 페르소나

| 이름 | 대상이 아닌 이유 |
|------|----------------|
| Non-developer | SDwC generates developer-oriented technical documentation. Non-technical users cannot fill in intake_template |
| Developer not using Claude Code | Generated CLAUDE.md and skills are specifically designed for Claude Code workflows |

### 5.3 이해관계자

| 역할 | 주요 관심사 | 영향력 |
|------|-----------|--------|
| AI Agent (Claude Code) | Needs clear, structured documentation to provide effective development assistance | high |

<!-- Claude: 수정/추가 시 기존 섹션 구조와 형식을 유지. -->
