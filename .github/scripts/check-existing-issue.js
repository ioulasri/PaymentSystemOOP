/**
 * Check if an issue already exists for this CI failure
 * @param {object} github - GitHub API client
 * @param {object} context - GitHub Actions context
 * @param {object} core - GitHub Actions core utilities
 * @param {string} branch - Branch name
 */
module.exports = async ({ github, context, core, branch }) => {
  const issueTitle = `CI Failure on ${branch}`;

  const issues = await github.rest.issues.listForRepo({
    owner: context.repo.owner,
    repo: context.repo.repo,
    state: 'open',
    labels: 'ci-failure,automated',
    per_page: 100
  });

  const existingIssue = issues.data.find(issue =>
    issue.title.includes(issueTitle) ||
    issue.body.includes(`Branch: \`${branch}\``)
  );

  if (existingIssue) {
    core.setOutput('issue_exists', 'true');
    core.setOutput('issue_number', existingIssue.number);
  } else {
    core.setOutput('issue_exists', 'false');
  }

  return existingIssue;
};
