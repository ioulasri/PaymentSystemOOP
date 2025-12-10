/**
 * Download workflow artifacts from a workflow run
 * @param {object} github - GitHub API client
 * @param {object} context - GitHub Actions context
 * @param {string} runId - Workflow run ID
 */
module.exports = async ({ github, context, runId }) => {
  const artifacts = await github.rest.actions.listWorkflowRunArtifacts({
    owner: context.repo.owner,
    repo: context.repo.repo,
    run_id: runId,
  });
  console.log('Artifacts:', artifacts.data);
  return artifacts.data;
};
