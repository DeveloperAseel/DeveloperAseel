PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS findings;
DROP TABLE IF EXISTS audits;

CREATE TABLE audits (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_name TEXT NOT NULL,
    department TEXT NOT NULL,
    start_date DATE NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('Planned', 'In Progress', 'Completed'))
);

CREATE TABLE findings (
    finding_id INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_id INTEGER NOT NULL,
    finding_title TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('Low', 'Medium', 'High', 'Critical')),
    owner TEXT NOT NULL,
    due_date DATE NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('Open', 'In Progress', 'Closed')),
    created_at DATE NOT NULL DEFAULT CURRENT_DATE,
    FOREIGN KEY (audit_id) REFERENCES audits(audit_id) ON DELETE CASCADE
);

INSERT INTO audits (audit_name, department, start_date, status) VALUES
('Access Control Review', 'Information Technology', '2026-07-01', 'In Progress'),
('Backup and Recovery Audit', 'IT Operations', '2026-08-10', 'Completed');

INSERT INTO findings (audit_id, finding_title, severity, owner, due_date, status) VALUES
(1, 'Shared administrator accounts', 'High', 'Infrastructure Team', '2026-09-30', 'In Progress'),
(1, 'Inactive accounts not disabled', 'Medium', 'Identity Team', '2026-09-15', 'Open'),
(1, 'Audit log retention is insufficient', 'High', 'Security Operations', '2026-09-25', 'Open'),
(2, 'Backup restoration test is missing', 'Critical', 'IT Operations', '2026-09-05', 'Closed'),
(2, 'Recovery contact list is outdated', 'Low', 'Continuity Team', '2026-10-01', 'Open');
