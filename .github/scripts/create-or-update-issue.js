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

  // Format failed steps
  let stepsTable = '| Job | Failed Step | Details |\n|-----|-------------|----------|\n';
  failedSteps.forEach(step => {
    stepsTable += `| ${step.job} | ${step.step} | [View logs](${step.url}) |\n`;
  });

  const issueBody = `## 🚨 CI Pipeline Failed

**Branch:** \`${branch}\`
**Commit:** \`${sha}\`
**Triggered by:** @${actor}
**Run:** [#${runNumber}](${runUrl})
**Date:** ${new Date().toISOString().split('T')[0]}

### Failed Steps

${stepsTable}

### Action Required

Please review the failed jobs and fix the issues. Common problems:

- [ ] Linting errors (flake8, mypy)
- [ ] Test failures
- [ ] Security issues (bandit)
- [ ] Type checking errors
- [ ] Code formatting (black, isort)

### How to Fix

1. Pull the latest changes: \`git pull origin ${branch}\`
2. Run checks locally: \`make ci-test\`
3. Fix the errors shown in the logs
4. Commit and push your fixes

---
*This issue was automatically created by the CI failure workflow.*
*The issue will be automatically closed when the CI passes.*`;

  if (issueExists) {
    // Update existing issue
    await github.rest.issues.createComment({
      owner: context.repo.owner,
      repo: context.repo.repo,
      issue_number: issueNumber,
      body: `## 🔄 CI Still Failing\n\n${issueBody}`
    });

    console.log(`✅ Updated existing issue #${issueNumber}`);
  } else {
    // Create new issue
    const issue = await github.rest.issues.create({
      owner: context.repo.owner,
      repo: context.repo.repo,
      title: `🚨 CI Failure on ${branch} (${sha})`,
      body: issueBody,
      labels: ['ci-failure', 'automated', 'bug'],
      assignees: [actor]
    });

    console.log(`✅ Created new issue #${issue.data.number}`);
  }
};
