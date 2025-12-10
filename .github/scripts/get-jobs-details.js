/**
 * Get jobs details from a workflow run, including failed jobs and steps
 * @param {object} github - GitHub API client
 * @param {object} context - GitHub Actions context
 * @param {object} core - GitHub Actions core utilities
 * @param {string} runId - Workflow run ID
 */
module.exports = async ({ github, context, core, runId }) => {
  const jobs = await github.rest.actions.listJobsForWorkflowRun({
    owner: context.repo.owner,
    repo: context.repo.repo,
    run_id: runId,
  });

  const failedJobs = jobs.data.jobs.filter(job => job.conclusion === 'failure');
  const failedSteps = failedJobs.flatMap(job =>
    job.steps.filter(step => step.conclusion === 'failure')
      .map(step => ({
        job: job.name,
        step: step.name,
        url: job.html_url
      }))
  );

  core.setOutput('failed_jobs', JSON.stringify(failedJobs.map(j => j.name)));
  core.setOutput('failed_steps', JSON.stringify(failedSteps));

  return failedSteps;
};
