/**
 * Get workflow run details
 * @param {object} github - GitHub API client
 * @param {object} context - GitHub Actions context
 * @param {object} core - GitHub Actions core utilities
 * @param {string} runId - Workflow run ID
 */
module.exports = async ({ github, context, core, runId }) => {
  const run = await github.rest.actions.getWorkflowRun({
    owner: context.repo.owner,
    repo: context.repo.repo,
    run_id: runId,
  });

  core.setOutput('run_url', run.data.html_url);
  core.setOutput('run_number', run.data.run_number);
  core.setOutput('head_branch', run.data.head_branch);
  core.setOutput('head_sha', run.data.head_sha.substring(0, 7));
  core.setOutput('triggering_actor', run.data.triggering_actor.login);

  return run.data;
};
