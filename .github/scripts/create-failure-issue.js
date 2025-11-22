/**
 * Create or update GitHub issue when CI fails
 * @param {object} github - GitHub API client
 * @param {object} context - GitHub Actions context
 * @param {object} needs - Job results from GitHub Actions
 */
module.exports = async ({ github, context, needs }) => {
  const branch = process.env.GITHUB_REF_NAME;
  const sha = process.env.GITHUB_SHA.substring(0, 7);
  const fullSha = process.env.GITHUB_SHA;
  const runUrl = `${process.env.GITHUB_SERVER_URL}/${process.env.GITHUB_REPOSITORY}/actions/runs/${process.env.GITHUB_RUN_ID}`;
  const runNumber = process.env.GITHUB_RUN_NUMBER;
  const actor = process.env.GITHUB_ACTOR;
  const repository = process.env.GITHUB_REPOSITORY;
  const workflowName = process.env.GITHUB_WORKFLOW;
  const eventName = process.env.GITHUB_EVENT_NAME;

  // Collect detailed job information
  const failedJobs = [];
  const jobDetails = {
    lint: needs.lint.result,
    test: needs.test.result,
    'test-runner': needs['test-runner'].result,
    security: needs.security.result
  };

  // Categorize failures
  const criticalFailures = [];
  const warningFailures = [];

  Object.entries(jobDetails).forEach(([job, status]) => {
    if (status === 'failure') {
      failedJobs.push(job);
      if (job === 'test' || job === 'security') {
        criticalFailures.push(job);
      } else {
        warningFailures.push(job);
      }
    }
  });

  // Check for existing open issue
  const issues = await github.rest.issues.listForRepo({
    owner: context.repo.owner,
    repo: context.repo.repo,
    state: 'open',
    labels: 'ci-failure,automated',
    per_page: 100
  });

  const existingIssue = issues.data.find(issue =>
    issue.title.includes(`CI Failure on ${branch}`)
  );

  // Build comprehensive issue body
  const priorityEmoji = criticalFailures.length > 0 ? '🔴' : '🟡';
  const priorityLabel = criticalFailures.length > 0 ? 'HIGH PRIORITY' : 'MEDIUM PRIORITY';

  // Format metadata section
  const metadata = `
<details>
<summary>📋 CI Run Metadata</summary>

| Key | Value |
|-----|-------|
| **Workflow** | ${workflowName} |
| **Run Number** | [#${runNumber}](${runUrl}) |
| **Event** | ${eventName} |
| **Branch** | \`${branch}\` |
| **Commit** | [\`${sha}\`](${process.env.GITHUB_SERVER_URL}/${repository}/commit/${fullSha}) |
| **Author** | @${actor} |
| **Timestamp** | ${new Date().toISOString()} |
| **Priority** | ${priorityEmoji} **${priorityLabel}** |

</details>
`;

  // Format failed jobs table with status icons
  const getStatusIcon = (status) => {
    switch(status) {
      case 'success': return '✅';
      case 'failure': return '❌';
      case 'cancelled': return '🚫';
      case 'skipped': return '⏭️';
      default: return '❓';
    }
  };

  let jobsTable = '| Job | Status | Result | Details |\n|-----|--------|--------|----------|\n';
  Object.entries(jobDetails).forEach(([job, status]) => {
    const icon = getStatusIcon(status);
    const badge = status === 'failure' ? '`FAILED`' : status === 'success' ? '`PASSED`' : '`' + status.toUpperCase() + '`';
    const jobUrl = `${runUrl}/job/${context.runId}`;
    jobsTable += `| **${job}** | ${icon} | ${badge} | [View logs](${runUrl}) |\n`;
  });

  // Build error analysis section
  let errorAnalysis = '\n### 🔍 Failure Analysis\n\n';

  if (criticalFailures.length > 0) {
    errorAnalysis += `#### ${priorityEmoji} Critical Failures (${criticalFailures.length})\n\n`;
    criticalFailures.forEach(job => {
      if (job === 'test') {
        errorAnalysis += `- **Tests Failed**: Unit or integration tests are failing. This blocks deployment.\n`;
        errorAnalysis += `  - Run \`make test\` locally to reproduce\n`;
        errorAnalysis += `  - Check test output for specific failing tests\n`;
      } else if (job === 'security') {
        errorAnalysis += `- **Security Issues Detected**: Bandit found security vulnerabilities in the code.\n`;
        errorAnalysis += `  - Run \`bandit -r src/\` to see security issues\n`;
        errorAnalysis += `  - Review and fix security warnings\n`;
      }
    });
  }

  if (warningFailures.length > 0) {
    errorAnalysis += `\n#### 🟡 Code Quality Issues (${warningFailures.length})\n\n`;
    warningFailures.forEach(job => {
      if (job === 'lint') {
        errorAnalysis += `- **Linting Failed**: Code style or type checking issues detected.\n`;
        errorAnalysis += `  - Run \`flake8 src/ tests/\` for style issues\n`;
        errorAnalysis += `  - Run \`mypy src/\` for type checking\n`;
        errorAnalysis += `  - Run \`black --check src/ tests/\` for formatting\n`;
      } else if (job === 'test-runner') {
        errorAnalysis += `- **Test Runner Issues**: Custom test runner encountered problems.\n`;
        errorAnalysis += `  - Check test runner configuration\n`;
        errorAnalysis += `  - Review test execution logs\n`;
      }
    });
  }

  // Build action items with checkboxes
  const actionItems = `
### ✅ Action Items

**Quick Checks:**
- [ ] Review the [workflow run logs](${runUrl})
- [ ] Pull latest changes: \`git pull origin ${branch}\`
- [ ] Reproduce locally: \`make ci-test\`

**Fixes Required:**
${criticalFailures.includes('test') ? '- [ ] Fix failing unit/integration tests\n' : ''}${criticalFailures.includes('security') ? '- [ ] Resolve security vulnerabilities\n' : ''}${warningFailures.includes('lint') ? '- [ ] Fix linting errors (flake8, mypy, black, isort)\n' : ''}${warningFailures.includes('test-runner') ? '- [ ] Fix test runner configuration issues\n' : ''}- [ ] Verify all checks pass locally
- [ ] Commit and push fixes

**After Fixing:**
- [ ] Push changes to trigger new CI run
- [ ] Verify this issue auto-closes on success
`;

  // Build helpful commands section
  const commands = `
<details>
<summary>🛠️ Helpful Commands</summary>

\`\`\`bash
# Pull latest changes
git pull origin ${branch}

# Run all CI checks locally
make ci-test

# Run specific checks
make lint        # Linting only
make test        # Tests only
make security    # Security scan only

# Auto-fix formatting
black src/ tests/
isort src/ tests/

# View detailed test output
pytest tests/ -v --tb=short

# Check for security issues
bandit -r src/ -ll
\`\`\`

</details>
`;

  // Combine all sections
  const issueBody = `${priorityEmoji} **${priorityLabel}** - CI Pipeline Failed

${metadata}

### 📊 Job Results

${jobsTable}

${errorAnalysis}

${actionItems}

${commands}

---
<sub>🤖 This issue was automatically created by the CI failure workflow. It will be closed automatically when CI passes.</sub>
`;

  if (existingIssue) {
    // Update existing issue with comment
    await github.rest.issues.createComment({
      owner: context.repo.owner,
      repo: context.repo.repo,
      issue_number: existingIssue.number,
      body: `## 🔄 CI Still Failing (Run #${runNumber})

${issueBody}`
    });
    console.log(`✅ Updated existing issue #${existingIssue.number}`);
  } else {
    // Determine labels based on priority
    const labels = ['ci-failure', 'automated'];
    if (criticalFailures.length > 0) {
      labels.push('priority: high', 'bug');
    } else {
      labels.push('priority: medium', 'code-quality');
    }

    // Add specific labels for failure types
    if (failedJobs.includes('test')) labels.push('tests');
    if (failedJobs.includes('security')) labels.push('security');
    if (failedJobs.includes('lint')) labels.push('linting');

    // Create new issue
    const issue = await github.rest.issues.create({
      owner: context.repo.owner,
      repo: context.repo.repo,
      title: `${priorityEmoji} CI Failure on ${branch} - ${failedJobs.join(', ')} (${sha})`,
      body: issueBody,
      labels: labels,
      assignees: [actor]
    });
    console.log(`✅ Created new issue #${issue.data.number}`);
    console.log(`   Priority: ${priorityLabel}`);
    console.log(`   Failed Jobs: ${failedJobs.join(', ')}`);
  }
};
