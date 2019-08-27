
-- Check if the Travis job id is sorted in the same order as the build number

SELECT A.tr_job_id
FROM travistorrent_8_2_2017 A, travistorrent_8_2_2017 B
WHERE A.tr_build_number = B.tr_build_number + 1
AND A.tr_job_id < B.tr_job_id;
