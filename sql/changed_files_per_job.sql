SELECT tt.tr_build_id, count(tp.filename)
FROM travistorrent_8_2_2017 tt, tr_all_built_commits commits, tr_patches tp
WHERE tt.gh_project_name = 'square/okhttp'
AND tt.tr_job_id = commits.tr_job_id
AND commits.git_commit_id = tp.sha
GROUP BY tt.tr_build_id