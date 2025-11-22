/**
 * Close GitHub issues related to CI failure when CI passes
 * @param {object} github - GitHub API client
 * @param {object} context - GitHub Actions context
 * @param {string} branch - Branch name
 */
module.exports = async ({ github, context, branch }) => {
  const issues = await github.rest.issues.listForRepo({
    owner: context.repo.owner,
    repo: context.repo.repo,
    state: 'open',
    labels: 'ci-failure,automated',
    per_page: 100
  });

  let closedCount = 0;

  for (const issue of issues.data) {
    if (issue.title.includes(branch) || issue.body.includes(`Branch: \`${branch}\``)) {
      await github.rest.issues.update({
        owner: context.repo.owner,
        repo: context.repo.repo,
        issue_number: issue.number,
        state: 'closed'
      });

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
