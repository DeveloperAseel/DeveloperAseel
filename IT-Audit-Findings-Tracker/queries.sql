-- Open findings ordered by priority and due date
SELECT
    f.finding_id,
    a.audit_name,
    f.finding_title,
    f.severity,
    f.owner,
    f.due_date,
    f.status
FROM findings AS f
JOIN audits AS a ON a.audit_id = f.audit_id
WHERE f.status <> 'Closed'
ORDER BY
    CASE f.severity
        WHEN 'Critical' THEN 1
        WHEN 'High' THEN 2
        WHEN 'Medium' THEN 3
        ELSE 4
    END,
    f.due_date;

-- Number of findings by audit and status
SELECT
    a.audit_name,
    COUNT(f.finding_id) AS total_findings,
    SUM(CASE WHEN f.status = 'Closed' THEN 1 ELSE 0 END) AS closed_findings,
    SUM(CASE WHEN f.status <> 'Closed' THEN 1 ELSE 0 END) AS open_findings
FROM audits AS a
LEFT JOIN findings AS f ON f.audit_id = a.audit_id
GROUP BY a.audit_id, a.audit_name
ORDER BY a.audit_name;

-- Overdue findings that still require action
SELECT
    finding_title,
    severity,
    owner,
    due_date,
    status
FROM findings
WHERE status <> 'Closed'
  AND due_date < DATE('now')
ORDER BY due_date;

-- Closure percentage for each audit
SELECT
    a.audit_name,
    ROUND(
        100.0 * SUM(CASE WHEN f.status = 'Closed' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(f.finding_id), 0),
        1
    ) AS closure_percentage
FROM audits AS a
LEFT JOIN findings AS f ON f.audit_id = a.audit_id
GROUP BY a.audit_id, a.audit_name
ORDER BY closure_percentage DESC;
