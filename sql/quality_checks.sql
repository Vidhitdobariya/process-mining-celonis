-- sql/quality_checks.sql
-- Validates the cleaned event log after clean_data.py has run.
-- Run this directly in MySQL Workbench against the event_log table.
-- All checks should return PASS if clean_data.py ran successfully.

-- ============================================================
-- CHECK 1: Missing timestamps
-- Expected result: count = 0
-- ============================================================
SELECT
    'CHECK 1 - Missing Timestamps' AS check_name,
    COUNT(*) AS issue_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS result
FROM event_log
WHERE timestamp IS NULL;

-- ============================================================
-- CHECK 2: Future timestamps (anything beyond today)
-- Expected result: count = 0
-- ============================================================
SELECT
    'CHECK 2 - Future Timestamps' AS check_name,
    COUNT(*) AS issue_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS result
FROM event_log
WHERE timestamp > NOW();

-- ============================================================
-- CHECK 3: Duplicate events
-- Same order + same activity + same timestamp = duplicate
-- Expected result: count = 0
-- ============================================================
SELECT
    'CHECK 3 - Duplicate Events' AS check_name,
    COUNT(*) AS issue_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS result
FROM (
    SELECT case_id, activity, timestamp, COUNT(*) AS cnt
    FROM event_log
    GROUP BY case_id, activity, timestamp
    HAVING COUNT(*) > 1
) duplicates;

-- ============================================================
-- CHECK 4: Null resources
-- Expected result: count = 0
-- ============================================================
SELECT
    'CHECK 4 - Null Resources' AS check_name,
    COUNT(*) AS issue_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS result
FROM event_log
WHERE resource IS NULL;

-- ============================================================
-- CHECK 5: Overall data quality score
-- Formula: (clean rows / total rows) * 100
-- Expected result: 100.0
-- ============================================================
SELECT
    'CHECK 5 - Overall Quality Score' AS check_name,
    ROUND(
        (1.0 - (
            SUM(CASE WHEN timestamp IS NULL THEN 1 ELSE 0 END) +
            SUM(CASE WHEN resource IS NULL THEN 1 ELSE 0 END)
        ) / COUNT(*)
        ) * 100, 2
    ) AS quality_score_pct,
    CASE
        WHEN ROUND(
            (1.0 - (
                SUM(CASE WHEN timestamp IS NULL THEN 1 ELSE 0 END) +
                SUM(CASE WHEN resource IS NULL THEN 1 ELSE 0 END)
            ) / COUNT(*)
            ) * 100, 2
        ) = 100.0 THEN 'PASS'
        ELSE 'FAIL'
    END AS result
FROM event_log;

-- ============================================================
-- BONUS: Summary of all events per channel
-- ============================================================
SELECT
    channel,
    COUNT(DISTINCT case_id) AS total_orders,
    COUNT(*) AS total_events,
    ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT case_id), 1) AS avg_events_per_order
FROM event_log
GROUP BY channel
ORDER BY total_orders DESC;
