-- Table: domain
CREATE TABLE domain (
    domain_id SERIAL PRIMARY KEY,
    domain_name VARCHAR(255) NOT NULL UNIQUE,
    registered_at TIMESTAMP NOT NULL,
    unregistered_at TIMESTAMP DEFAULT NULL,
    -- Check that registered_at is before unregistered_at
    CONSTRAINT registration_before_unregistration
        CHECK (domain.registered_at < COALESCE(domain.unregistered_at, now()))
);

CREATE INDEX domain_registered_at_unregistered_at_index
    ON domain (registered_at, unregistered_at);

-- Domain flags
CREATE TYPE flag_state AS ENUM ('EXPIRED', 'OUTZONE', 'DELETE_CANDIDATE');
CREATE TYPE flag_range AS RANGE (SUBTYPE = tsrange);
-- Table: domain_flag
CREATE TABLE domain_flag (
    flag_id SERIAL PRIMARY KEY,
    domain_id INT REFERENCES domain(domain_id) ON DELETE CASCADE,
    flag_name flag_state NOT NULL,
    valid_from TIMESTAMP NOT NULL,
    valid_to TIMESTAMP,
    -- Check valid_from is before valid_to
    CONSTRAINT valid_from_before_valid_to
        CHECK (valid_to IS NULL OR valid_from < valid_to)
    -- Check overlapping flag validity intervals for the same domain and flag.
    -- Impossible to implement because postgres cant create subqueries in CHECK constraints
);

-- Insert example data
INSERT INTO domain (domain_name, registered_at, unregistered_at) VALUES
    ('example1.com', '2022-01-01', NULL),  -- Registered and active domain without expiration flag
    ('example2.com', '2023-05-01', '2024-01-01'),  -- Registered and expired domain
    ('example3.com', '2024-03-01', NULL); -- Registered and active domain without expiration flag

-- Insert new example data for domain_flag
INSERT INTO domain_flag (domain_id, flag_name, valid_from, valid_to) VALUES
    (1, 'OUTZONE', '2022-06-01', NULL),  -- Outzone flag for example1.com (currently valid)
    (2, 'EXPIRED', '2023-01-01', '2024-01-01'),  -- Expired flag for example2.com
    (3, 'DELETE_CANDIDATE', '2024-06-01', NULL), -- Delete candidate flag for example3.com (currently valid)
    (1, 'EXPIRED', '2023-01-01', '2023-02-01'),  -- Expired flag for example1.com in the past
    (1, 'OUTZONE', '2023-02-01', '2023-03-01'),  -- Outzone flag for example1.com in the past
    (2, 'EXPIRED', '2024-03-01', '2024-04-01'),  -- Expired flag for example2.com in the past
    (2, 'OUTZONE', '2024-02-01', '2024-03-01');  -- Outzone flag for example2.com in the past


-- Query which will return fully qualified domain name of domains which are currently (at the time query is run) registered and do not have and active (valid) expiration (EXPIRED) flag.
SELECT DISTINCT d.domain_name
FROM domain d
LEFT JOIN domain_flag df ON d.domain_id = df.domain_id
WHERE d.unregistered_at IS NULL
  AND df.flag_name != 'EXPIRED'
  AND df.valid_from <= NOW()
  AND (df.valid_to IS NULL OR df.valid_to > NOW());

-- Query which will return fully qualified domain name of domains which have had active (valid) EXPIRED and OUTZONE flags (means both flags and not necessarily at the same time) in the past (relative to the query run time).
SELECT DISTINCT d.*
FROM domain d
    JOIN domain_flag df_expired ON d.domain_id = df_expired.domain_id
    JOIN domain_flag df_outzone ON d.domain_id = df_outzone.domain_id
WHERE (df_expired.flag_name = 'EXPIRED' AND df_expired.valid_from <= NOW() AND (df_expired.valid_to <= NOW() OR df_expired.valid_to IS NULL))
    AND (df_outzone.flag_name = 'OUTZONE' AND df_outzone.valid_from <= NOW() AND df_outzone.valid_to <= NOW() OR df_outzone.valid_to IS NULL);