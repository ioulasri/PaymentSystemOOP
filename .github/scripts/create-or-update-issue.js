/**
 * Create or update a GitHub issue for CI failure with detailed information
 * @param {object} github - GitHub API client
 * @param {object} context - GitHub Actions context
 * @param {object} params - Issue parameters
 * @param {string} params.branch - Branch name
 * @param {string} params.sha - Commit SHA (short)
 * @param {string} params.runUrl - Workflow run URL
 * @param {string} params.runNumber - Workflow run number
 * @param {string} params.actor - Triggering actor username
 * @param {Array} params.failedSteps - Array of failed steps
 * @param {boolean} params.issueExists - Whether issue already exists
 * @param {number} params.issueNumber - Existing issue number (if exists)
 */
module.exports = async ({ github, context, params }) => {
  const { branch, sha, runUrl, runNumber, actor, failedSteps, issueExists, issueNumber } = params;

  // Categorize failures by job type
  const jobCategories = {
    critical: [],
    quality: [],
    other: []
  };

  const uniqueJobs = [...new Set(failedSteps.map(s => s.job))];
  uniqueJobs.forEach(job => {
    const jobLower = job.toLowerCase();
    if (jobLower.includes('test') || jobLower.includes('security')) {
      jobCategories.critical.push(job);
    } else if (jobLower.includes('lint') || jobLower.includes('format')) {
      jobCategories.quality.push(job);
    } else {
      jobCategories.other.push(job);
    }
  });

  const priorityEmoji = jobCategories.critical.length > 0 ? '🔴' : '🟡';
  const priorityLabel = jobCategories.critical.length > 0 ? 'HIGH PRIORITY' : 'MEDIUM PRIORITY';

  // Build metadata section
  const metadata = `
<details>
<summary>📋 CI Run Metadata</summary>

| Key | Value |
|-----|-------|
| **Run Number** | [#${runNumber}](${runUrl}) |
| **Branch** | \`${branch}\` |
| **Commit** | \`${sha}\` |
| **Author** | @${actor} |
| **Timestamp** | ${new Date().toISOString()} |
| **Priority** | ${priorityEmoji} **${priorityLabel}** |
| **Failed Jobs** | ${uniqueJobs.length} |
| **Failed Steps** | ${failedSteps.length} |

</details>
`;

  // Group failed steps by job
  const stepsByJob = {};
  failedSteps.forEach(step => {
    if (!stepsByJob[step.job]) {
      stepsByJob[step.job] = [];
    }
    stepsByJob[step.job].push(step);
  });

  // Format failed steps table with grouping
  let stepsTable = '';
  Object.entries(stepsByJob).forEach(([job, steps]) => {
    const jobEmoji = jobCategories.critical.includes(job) ? '🔴' :
                     jobCategories.quality.includes(job) ? '🟡' : '🔵';
    stepsTable += `\n#### ${jobEmoji} ${job}\n\n`;
    stepsTable += '| Step Name | Status | Logs |\n|-----------|--------|------|\n';
    steps.forEach(step => {
      stepsTable += `| ${step.step} | ❌ Failed | [View](${step.url}) |\n`;
    });
  });

  // Build detailed error analysis
  let errorAnalysis = '\n### � Detailed Analysis\n';

  if (jobCategories.critical.length > 0) {
    errorAnalysis += `\n#### 🔴 Critical Failures (${jobCategories.critical.length} jobs)\n\n`;
    errorAnalysis += '**These must be fixed before merging:**\n\n';
    jobCategories.critical.forEach(job => {
      const steps = stepsByJob[job];
      errorAnalysis += `- **${job}**: ${steps.length} step(s) failed\n`;
      steps.forEach(step => {
        errorAnalysis += `  - ❌ ${step.step}\n`;
      });
    });
  }

  if (jobCategories.quality.length > 0) {
    errorAnalysis += `\n#### 🟡 Code Quality Issues (${jobCategories.quality.length} jobs)\n\n`;
    jobCategories.quality.forEach(job => {
      const steps = stepsByJob[job];
      errorAnalysis += `- **${job}**: ${steps.length} step(s) failed\n`;
      steps.forEach(step => {
        errorAnalysis += `  - ⚠️ ${step.step}\n`;
      });
    });
  }

  if (jobCategories.other.length > 0) {
    errorAnalysis += `\n#### 🔵 Other Issues (${jobCategories.other.length} jobs)\n\n`;
    jobCategories.other.forEach(job => {
      const steps = stepsByJob[job];
      errorAnalysis += `- **${job}**: ${steps.length} step(s) failed\n`;
    });
  }

  // Build comprehensive action items
  const actionItems = `
### ✅ Action Plan

**1. Investigation:**
- [ ] Review the [complete workflow logs](${runUrl})
- [ ] Check each failed step listed above
- [ ] Identify root cause of failures

**2. Local Reproduction:**
\`\`\`bash
# Pull latest changes
git pull origin ${branch}

# Run full CI test suite
make ci-test

# Or run specific checks:
${jobCategories.critical.some(j => j.toLowerCase().includes('test')) ? 'make test        # Run tests\n' : ''}${jobCategories.critical.some(j => j.toLowerCase().includes('security')) ? 'bandit -r src/  # Security scan\n' : ''}${jobCategories.quality.some(j => j.toLowerCase().includes('lint')) ? 'make lint       # Linting checks\n' : ''}\`\`\`

**3. Fix Issues:**
${jobCategories.critical.length > 0 ? '- [ ] Fix all critical failures (tests, security)\n' : ''}${jobCategories.quality.length > 0 ? '- [ ] Resolve code quality issues (linting, formatting)\n' : ''}${jobCategories.other.length > 0 ? '- [ ] Address other failures\n' : ''}- [ ] Verify all checks pass locally

**4. Validation:**
- [ ] Commit fixes with descriptive message
- [ ] Push to \`${branch}\` to trigger new CI run
- [ ] Monitor new CI run for success
- [ ] Verify this issue auto-closes
`;

  // Helpful commands section
  const commands = `
<details>
<summary>🛠️ Quick Fix Commands</summary>

\`\`\`bash
# Auto-fix common issues
black src/ tests/          # Format code
isort src/ tests/          # Sort imports
flake8 src/ tests/         # Check style
mypy src/                  # Type check

# Run tests with verbose output
pytest tests/ -v --tb=short

# Security scan
bandit -r src/ -ll

# Run everything at once
make ci-test
\`\`\`

</details>
`;

  // Build issue summary
  const summary = `${priorityEmoji} **${priorityLabel}** - CI Pipeline Failed on ${branch}

**Quick Stats:**
- ❌ ${failedSteps.length} failed step(s) across ${uniqueJobs.length} job(s)
- 🔴 ${jobCategories.critical.length} critical failure(s)
- 🟡 ${jobCategories.quality.length} quality issue(s)
`;

  // Combine all sections
  const issueBody = `${summary}

${metadata}

### 📊 Failed Steps by Job

${stepsTable}

${errorAnalysis}

${actionItems}

${commands}

---
<sub>🤖 Automatically created by CI failure workflow | Will auto-close when CI passes | [View Run #${runNumber}](${runUrl})</sub>
`;

  if (issueExists) {
    // Update existing issue
    await github.rest.issues.createComment({
      owner: context.repo.owner,
      repo: context.repo.repo,
      issue_number: issueNumber,
      body: `## 🔄 CI Still Failing (Attempt #${runNumber})

${issueBody}`
    });

    console.log(`✅ Updated existing issue #${issueNumber}`);
    console.log(`   Failed steps: ${failedSteps.length}`);
    console.log(`   Priority: ${priorityLabel}`);
  } else {
    // Determine labels
    const labels = ['ci-failure', 'automated'];
    if (jobCategories.critical.length > 0) {
      labels.push('priority: high', 'bug');
    } else {
      labels.push('priority: medium', 'code-quality');
    }

    // Add specific labels
    if (uniqueJobs.some(j => j.toLowerCase().includes('test'))) labels.push('tests');
    if (uniqueJobs.some(j => j.toLowerCase().includes('security'))) labels.push('security');
    if (uniqueJobs.some(j => j.toLowerCase().includes('lint'))) labels.push('linting');

    // Create new issue with enhanced title
    const failedJobsList = uniqueJobs.slice(0, 2).join(', ') +
                          (uniqueJobs.length > 2 ? ` +${uniqueJobs.length - 2} more` : '');

    const issue = await github.rest.issues.create({
      owner: context.repo.owner,
      repo: context.repo.repo,
      title: `${priorityEmoji} CI Failure: ${failedJobsList} on ${branch} (${sha})`,
      body: issueBody,
      labels: labels,
      assignees: [actor]
    });

    console.log(`✅ Created new issue #${issue.data.number}`);
    console.log(`   Title: ${issue.data.title}`);
    console.log(`   Priority: ${priorityLabel}`);
    console.log(`   Labels: ${labels.join(', ')}`);
  }
};
