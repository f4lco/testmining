CREATE MATERIALIZED VIEW tr_all_built_commits AS (SELECT tr_job_id, unnest(string_to_array(git_all_built_commits, '#')) AS git_commit_id FROM travistorrent_8_2_2017 );
