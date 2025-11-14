# DROID System Guide for Claude Code

**DROIDs** (Specialized Development Agents) are reusable, customizable AI subagents that help you with specific tasks in your development workflow.

## What are DROIDs?

DROIDs are specialized AI assistants with:
- **Custom system prompts** - Tailored expertise and instructions
- **Tool restrictions** - Limited to specific tools for safety
- **Model flexibility** - Can use different AI models
- **Proactive activation** - Auto-suggested based on context
- **Reusability** - Define once, use everywhere

Think of DROIDs as expert consultants you can call upon for specific tasks.

## Pre-built DROIDs

Your Claude Code installation includes these DROIDs:

### 🔒 security-auditor
Reviews code for OWASP Top 10 vulnerabilities and security best practices.
- **Tools**: Read, Grep, Glob (read-only)
- **Triggers**: security, vulnerability, audit, XSS, injection
- **Use when**: Reviewing code for security issues, compliance audits

### 👀 code-reviewer
Comprehensive code review focusing on quality, patterns, and maintainability.
- **Tools**: Read, Grep, Glob (read-only)
- **Triggers**: review, PR, pull request, code quality
- **Use when**: Reviewing pull requests, code quality assessments

### 🧪 test-writer
Generates comprehensive test suites with edge cases and coverage.
- **Tools**: Read, Write, Edit, Grep, Glob
- **Triggers**: test, testing, unit test, coverage
- **Use when**: Writing tests, improving test coverage

### 🐛 debugger
Systematic debugging and root cause analysis.
- **Tools**: Read, Grep, Glob, Bash
- **Triggers**: bug, error, exception, crash, debug
- **Use when**: Investigating bugs, analyzing stack traces

### ♻️ refactoring-specialist
Safe refactoring to improve code structure while preserving behavior.
- **Tools**: Read, Edit, Grep, Glob, Bash
- **Triggers**: refactor, cleanup, technical debt, code smell
- **Use when**: Refactoring code, reducing technical debt

### 📚 documentation-writer
Creates comprehensive documentation, READMEs, and API docs.
- **Tools**: Read, Write, Edit, Grep, Glob
- **Triggers**: document, documentation, readme, API docs
- **Use when**: Writing documentation, creating guides

## How to Use DROIDs

### Method 1: Explicit Request
Ask Claude to use a specific DROID:

```
"Use the security-auditor DROID to review src/auth.ts"
"Have the code-reviewer DROID check my PR"
"Let the test-writer DROID create tests for this function"
```

### Method 2: Proactive Activation
DROIDs with `proactive: true` auto-activate when you mention their triggers:

```
"Can you review this code for security issues?"
→ Claude suggests using security-auditor DROID

"I need help debugging this error"
→ Claude suggests using debugger DROID
```

### Method 3: Context-Based
Claude automatically selects appropriate DROIDs based on your task.

## Creating Custom DROIDs

### Quick Start

Create a new DROID:
```bash
python3 ~/.claude/droid_cli.py create my-droid
```

This creates a template at `~/.claude/droids/my-droid.md`

### DROID Configuration Format

DROIDs are Markdown files with YAML frontmatter:

```markdown
---
name: my-droid
description: Brief description of what this DROID does
model: inherit  # or sonnet, opus, haiku
tools: ["Read", "Grep", "Glob"]  # or omit for all tools
proactive: true  # Auto-suggest when triggers match
triggers: ["keyword1", "keyword2"]  # Context keywords
---

You are a specialized assistant for [specific task].

Your responsibilities:
- [Responsibility 1]
- [Responsibility 2]

Guidelines:
- [Guideline 1]
- [Guideline 2]

## Example Output Format
[Show how DROID should structure responses]
```

### Configuration Fields

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| `name` | Yes | Lowercase name with hyphens/underscores | `api-tester` |
| `description` | No | Brief description (max 500 chars) | "Tests API endpoints" |
| `model` | No | AI model to use | `sonnet`, `opus`, `haiku`, `inherit` |
| `tools` | No | Allowed tools (omit for all) | `["Read", "Bash", "Grep"]` |
| `proactive` | No | Auto-suggest based on triggers | `true` or `false` |
| `triggers` | No | Keywords for proactive activation | `["api", "endpoint", "test"]` |

### Available Tools

**Read-only**:
- `Read` - Read files
- `Grep` - Search code
- `Glob` - Find files by pattern

**Write**:
- `Write` - Create new files
- `Edit` - Modify existing files

**Execution**:
- `Bash` - Run commands
- `Task` - Launch other agents

**Other**:
- `WebFetch`, `WebSearch`, `TodoWrite`, `AskUserQuestion`

### Example Custom DROID

Create an API tester DROID:

```markdown
---
name: api-tester
description: Tests REST API endpoints with various scenarios
model: sonnet
tools: ["Read", "Write", "Bash", "Grep", "Glob"]
proactive: true
triggers: ["api", "endpoint", "rest", "test api"]
---

You are an **API Testing DROID** specializing in comprehensive API endpoint testing.

## Your Mission
Test REST APIs thoroughly with happy paths, edge cases, and error scenarios.

## Testing Strategy

### 1. Discover Endpoints
- Scan route definitions
- Check API documentation
- List all HTTP methods (GET, POST, PUT, DELETE, PATCH)

### 2. Test Scenarios

**Happy Path**:
- Valid inputs
- Successful responses (200, 201, 204)
- Correct response format

**Edge Cases**:
- Empty payloads
- Maximum values
- Special characters
- Pagination limits

**Error Cases**:
- Invalid authentication (401)
- Missing permissions (403)
- Not found (404)
- Validation errors (400)
- Server errors (500)

### 3. Generate Test Code

Use appropriate testing framework:
- JavaScript: Jest + Supertest
- Python: pytest + requests
- Go: testing + httptest

## Example Output

```javascript
describe('POST /api/users', () => {
  it('should create user with valid data', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ name: 'Test', email: 'test@example.com' })
      .expect(201);

    expect(response.body.email).toBe('test@example.com');
  });

  it('should return 400 for invalid email', async () => {
    await request(app)
      .post('/api/users')
      .send({ name: 'Test', email: 'invalid' })
      .expect(400);
  });
});
```

## Guidelines
- Test all endpoints systematically
- Check response codes and formats
- Verify error handling
- Test authentication/authorization
- Document test coverage
```

## DROID Scopes

### User-level DROIDs
**Location**: `~/.claude/droids/`
- Personal DROIDs that follow you across projects
- Not shared with team
- Good for personal workflows and preferences

### Project-level DROIDs
**Location**: `.claude/droids/` (in project root)
- Shared via git with your team
- Project-specific expertise
- Good for team standards and conventions

**Priority**: Project DROIDs override user DROIDs with the same name.

## Managing DROIDs

### List all DROIDs
```bash
python3 ~/.claude/droid_cli.py list
```

### Show DROID details
```bash
python3 ~/.claude/droid_cli.py info security-auditor
```

### Create new DROID
```bash
# User-level
python3 ~/.claude/droid_cli.py create my-droid

# Project-level
python3 ~/.claude/droid_cli.py create team-droid --project
```

### Edit DROID
```bash
python3 ~/.claude/droid_cli.py edit my-droid
```

### Delete DROID
```bash
python3 ~/.claude/droid_cli.py delete my-droid
```

### Get suggestions
```bash
python3 ~/.claude/droid_cli.py suggest "security review"
```

## Best Practices

### 1. Single Responsibility
Each DROID should have one clear purpose.
- ✅ `security-auditor` - Security reviews only
- ❌ `code-helper` - Too vague, does everything

### 2. Clear Instructions
Write detailed system prompts with:
- Mission statement
- Specific responsibilities
- Output format examples
- Guidelines and constraints

### 3. Appropriate Tool Restrictions
Limit tools based on DROID's role:
- **Read-only DROIDs** (reviewers, auditors): `["Read", "Grep", "Glob"]`
- **Writer DROIDs** (documenters, test-writers): Add `"Write", "Edit"`
- **Executor DROIDs** (testers, debuggers): Add `"Bash"`

### 4. Meaningful Triggers
Choose triggers that match natural language:
- Security DROID: `["security", "vulnerability", "audit"]`
- Not: `["sec", "vuln", "check"]` (too cryptic)

### 5. Test Your DROIDs
Before sharing project DROIDs:
- Test with various inputs
- Verify tool restrictions work
- Check output quality
- Get team feedback

## Advanced Usage

### DROID Chaining
DROIDs can invoke other DROIDs:

```markdown
You are a deployment DROID.

Before deployment:
1. Use security-auditor to check for vulnerabilities
2. Use test-writer to ensure test coverage > 80%
3. Use code-reviewer to verify code quality
4. Then proceed with deployment
```

### Conditional Activation
Use triggers strategically:

```markdown
triggers: ["performance", "optimization", "slow", "bottleneck"]
```

Now mentioning "This code is slow" auto-activates the performance DROID.

### Team Conventions
Create DROIDs for team-specific standards:

```markdown
---
name: style-enforcer
description: Enforces team code style and conventions
---

You enforce our team's coding standards:
- 2 spaces for indentation (never tabs)
- ESLint rules in .eslintrc
- Max function length: 50 lines
- Always use TypeScript strict mode
- Prefer functional programming style
```

## Troubleshooting

### DROID not showing up
```bash
# Reload DROIDs
python3 ~/.claude/droid_cli.py reload
```

### DROID not being suggested
Check:
- `proactive: true` in frontmatter
- Triggers match your keywords
- No YAML syntax errors

### DROID using wrong tools
Verify `tools` array in frontmatter:
```yaml
tools: ["Read", "Grep", "Glob"]  # Explicit list
# or omit for all tools
```

### Editing doesn't take effect
DROIDs are loaded at session start. Reload or restart Claude Code.

## Examples by Use Case

### Code Review Workflow
```
User: "Review this PR for security and code quality"
→ security-auditor checks for vulnerabilities
→ code-reviewer checks for best practices
→ Combined comprehensive review
```

### Bug Fixing Workflow
```
User: "This function crashes with large inputs"
→ debugger analyzes the issue
→ test-writer creates reproduction test
→ refactoring-specialist suggests fix
→ security-auditor checks if fix is secure
```

### Documentation Workflow
```
User: "Document this new API module"
→ documentation-writer creates README
→ documentation-writer generates API docs
→ code-reviewer checks doc accuracy
```

## Creating a DROID Library

Build a collection of DROIDs for your tech stack:

**Frontend**:
- `react-reviewer` - React best practices
- `accessibility-checker` - WCAG compliance
- `performance-auditor` - Frontend performance

**Backend**:
- `api-designer` - REST/GraphQL design
- `database-optimizer` - Query optimization
- `auth-specialist` - Authentication/authorization

**DevOps**:
- `docker-helper` - Dockerfile best practices
- `ci-cd-builder` - Pipeline configuration
- `deployment-checker` - Pre-deployment validation

## Resources

- **DROID Loader**: `~/.claude/droid_loader.py`
- **DROID CLI**: `~/.claude/droid_cli.py`
- **User DROIDs**: `~/.claude/droids/`
- **Project DROIDs**: `.claude/droids/`

## Contributing DROIDs

Share your useful DROIDs with the community:
1. Test thoroughly
2. Document clearly
3. Add examples
4. Share on GitHub or team wiki

---

**Remember**: DROIDs are your specialized AI team members. Build them, customize them, and deploy them to supercharge your development workflow!

For more information: https://docs.claude.com
