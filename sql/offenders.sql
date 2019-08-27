SELECT tt1.tr_job_id FROM travistorrent_8_2_2017 as tt1
WHERE tt1.gh_project_name = 'square/okhttp'
AND EXISTS (
  SELECT 1 FROM tr_test_result as tr1 
  WHERE tr1.tr_job_id = tt1.tr_job_id
  AND (tr1.failures > 0 OR tr1.errors > 0)
) AND NOT EXISTS (
  SELECT 1 FROM travistorrent_8_2_2017 as tt2
  WHERE  tt2.gh_project_name = tt1.gh_project_name
  AND tt1.tr_build_number = tt2.tr_build_number + 1
  AND NOT EXISTS (
    SELECT 1 FROM tr_test_result AS tr2
    WHERE tr2.tr_job_id = tt2.tr_job_id
    AND (tr2.failures > 0 OR tr2.errors > 0)
  )
);