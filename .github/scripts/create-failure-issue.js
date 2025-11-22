/**
 * Create or update GitHub issue when CI fails
 * @param {object} github - GitHub API client
 * @param {object} context - GitHub Actions context
 * @param {object} needs - Job results from GitHub Actions
 */
module.exports = async ({ github, context, needs }) => {
  const branch = process.env.GITHUB_REF_NAME;
  const sha = process.env.GITHUB_SHA.substring(0, 7);
  const runUrl = `${process.env.GITHUB_SERVER_URL}/${process.env.GITHUB_REPOSITORY}/actions/runs/${process.env.GITHUB_RUN_ID}`;
  const runNumber = process.env.GITHUB_RUN_NUMBER;
  const actor = process.env.GITHUB_ACTOR;

  // Collect failed jobs
  const failedJobs = [];
  if (needs.lint.result === 'failure') failedJobs.push('Lint');
  if (needs.test.result === 'failure') failedJobs.push('Test');
  if (needs['test-runner'].result === 'failure') failedJobs.push('Test Runner');
  if (needs.security.result === 'failure') failedJobs.push('Security');

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

  // Format failed jobs table
  let jobsTable = '| Job | Status | Logs |\n|-----|--------|------|\n';
  jobsTable += `| Lint | ${needs.lint.result} | [View logs](${runUrl}) |\n`;
  jobsTable += `| Test | ${needs.test.result} | [View logs](${runUrl}) |\n`;
  jobsTable += `| Test Runner | ${needs['test-runner'].result} | [View logs](${runUrl}) |\n`;
  jobsTable += `| Security | ${needs.security.result} | [View logs](${runUrl}) |\n`;

  const issueBody = `## 🚨 CI Pipeline Failed

**Branch:** \`${branch}\`
**Commit:** \`${sha}\`
**Triggered by:** @${actor}
**Run:** [#${runNumber}](${runUrl})
**Date:** ${new Date().toISOString().split('T')[0]}

### Failed Jobs

${jobsTable}

### Action Required

Please review the failed jobs and fix the issues. Check the logs above for details.

### How to Fix

1. Pull the latest changes from ${branch}
2. Run checks locally: \`make ci-test\`
3. Fix the errors shown in the logs above
4. Commit and push your fixes

---
*This issue was automatically created and will be closed when CI passes.*`;

  if (existingIssue) {
    // Update existing issue with comment
    await github.rest.issues.createComment({
      owner: context.repo.owner,
      repo: context.repo.repo,
      issue_number: existingIssue.number,
      body: `## 🔄 CI Still Failing\n\n${issueBody}`
    });
    console.log(`✅ Updated existing issue #${existingIssue.number}`);
  } else {
    // Create new issue
    const issue = await github.rest.issues.create({
      owner: context.repo.owner,
      repo: context.repo.repo,
      title: `🚨 CI Failure on ${branch} (${sha})`,
      body: issueBody,
      labels: ['ci-failure', 'automated', 'bug']
    });
    console.log(`✅ Created new issue #${issue.data.number}`);
  }
};
