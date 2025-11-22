/**
 * Close GitHub issues when CI passes
 * @param {object} github - GitHub API client
 * @param {object} context - GitHub Actions context
 */
module.exports = async ({ github, context }) => {
  const branch = process.env.GITHUB_REF_NAME;

  // Find all open CI failure issues for this branch
  const issues = await github.rest.issues.listForRepo({
    owner: context.repo.owner,
    repo: context.repo.repo,
    state: 'open',
    labels: 'ci-failure,automated',
    per_page: 100
  });

  let closedCount = 0;

  for (const issue of issues.data) {
    if (issue.title.includes(`CI Failure on ${branch}`)) {
      // Close the issue
      await github.rest.issues.update({
        owner: context.repo.owner,
        repo: context.repo.repo,
        issue_number: issue.number,
        state: 'closed'
      });

      // Add success comment
      await github.rest.issues.createComment({
        owner: context.repo.owner,
        repo: context.repo.repo,
        issue_number: issue.number,
        body: '✅ CI is now passing! Automatically closing this issue.'
      });

      console.log(`✅ Closed issue #${issue.number}`);
      closedCount++;
    }
  }

  if (closedCount === 0) {
    console.log('ℹ️  No open CI failure issues found for this branch.');
  } else {
    console.log(`✅ Closed ${closedCount} issue(s) successfully.`);
  }
};
