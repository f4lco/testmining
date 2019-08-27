--WITH
--     jobs AS (SELECT tr_job_id, git_all_built_commits FROM travistorrent_8_2_2017 WHERE gh_project_name = 'google/guava'),
--     commits AS (SELECT tr_job_id, unnest(string_to_array(git_all_built_commits, '#')) AS git_commit_id FROM jobs)
--
--SELECT (tr_job_id, git_commit_id, "name") FROM commits, raw_patches WHERE commits.git_commit_id = raw_patches.sha LIMIT 5;


SELECT commits.tr_job_id, commits.git_commit_id, raw_patches."name"
FROM
     (SELECT tr_job_id, unnest(string_to_array(git_all_built_commits, '#')) FROM travistorrent_8_2_2017 WHERE gh_project_name = 'google/guava') AS commits(tr_job_id, git_commit_id),
     raw_patches
WHERE commits.git_commit_id = raw_patches.sha;
