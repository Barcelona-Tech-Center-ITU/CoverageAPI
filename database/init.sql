-- GIGA Coverage Database Initialization Script

-- Create the API keys table for phone_identifier to API key mapping
CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    phone_identifier VARCHAR(255) UNIQUE NOT NULL,
    api_key VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the coverage measurements table
CREATE TABLE IF NOT EXISTS coverage_measurements (
    id SERIAL PRIMARY KEY,
    api_key VARCHAR(255) NOT NULL,
    phone_identifier VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Location data
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    gps_accuracy DOUBLE PRECISION,
    
    -- Signal strength data
    signal_strength_dbm INTEGER,
    signal_strength_asu INTEGER,
    
    -- Network information
    network_type VARCHAR(50),
    mcc INTEGER,  -- Mobile Country Code
    mnc INTEGER,  -- Mobile Network Code
    cell_id BIGINT,
    
    -- Device information
    app_name VARCHAR(255),
    app_version VARCHAR(100),
    library_version VARCHAR(100),
    
    -- Performance data
    download_speed_kbps DOUBLE PRECISION,
    
    -- Foreign key constraint
    CONSTRAINT fk_api_key FOREIGN KEY (api_key) REFERENCES api_keys(api_key) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_api_keys_phone_identifier ON api_keys(phone_identifier);
CREATE INDEX IF NOT EXISTS idx_api_keys_api_key ON api_keys(api_key);

CREATE INDEX IF NOT EXISTS idx_coverage_phone_identifier ON coverage_measurements(phone_identifier);
CREATE INDEX IF NOT EXISTS idx_coverage_timestamp ON coverage_measurements(timestamp);
CREATE INDEX IF NOT EXISTS idx_coverage_location ON coverage_measurements(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_coverage_network_type ON coverage_measurements(network_type);
CREATE INDEX IF NOT EXISTS idx_coverage_mcc_mnc ON coverage_measurements(mcc, mnc);
CREATE INDEX IF NOT EXISTS idx_coverage_api_key ON coverage_measurements(api_key);

-- Create a view for basic statistics
CREATE OR REPLACE VIEW coverage_stats AS
SELECT 
    COUNT(*) as total_measurements,
    COUNT(DISTINCT phone_identifier) as unique_devices,
    COUNT(DISTINCT network_type) as network_types,
    AVG(signal_strength_dbm) as avg_signal_dbm,
    AVG(download_speed_kbps) as avg_download_speed_kbps,
    MIN(timestamp) as first_measurement,
    MAX(timestamp) as last_measurement
FROM coverage_measurements;

-- Create a view for network type distribution
CREATE OR REPLACE VIEW network_type_distribution AS
SELECT 
    network_type,
    COUNT(*) as measurement_count,
    COUNT(DISTINCT phone_identifier) as unique_devices,
    AVG(signal_strength_dbm) as avg_signal_dbm,
    AVG(download_speed_kbps) as avg_download_speed_kbps
FROM coverage_measurements 
WHERE network_type IS NOT NULL
GROUP BY network_type
ORDER BY measurement_count DESC;

-- Create a view for geographic distribution
CREATE OR REPLACE VIEW geographic_distribution AS
SELECT 
    ROUND(latitude::numeric, 2) as lat_rounded,
    ROUND(longitude::numeric, 2) as lng_rounded,
    COUNT(*) as measurement_count,
    COUNT(DISTINCT phone_identifier) as unique_devices,
    AVG(signal_strength_dbm) as avg_signal_dbm
FROM coverage_measurements 
WHERE latitude IS NOT NULL AND longitude IS NOT NULL
GROUP BY lat_rounded, lng_rounded
ORDER BY measurement_count DESC;

-- Create a view for API key statistics
CREATE OR REPLACE VIEW api_key_stats AS
SELECT 
    COUNT(*) as total_api_keys,
    MIN(created_at) as first_key_created,
    MAX(created_at) as last_key_created
FROM api_keys;

-- Grant permissions to the coverage user
GRANT ALL PRIVILEGES ON TABLE api_keys TO coverage;
GRANT ALL PRIVILEGES ON SEQUENCE api_keys_id_seq TO coverage;
GRANT ALL PRIVILEGES ON TABLE coverage_measurements TO coverage;
GRANT ALL PRIVILEGES ON SEQUENCE coverage_measurements_id_seq TO coverage;
GRANT SELECT ON coverage_stats TO coverage;
GRANT SELECT ON network_type_distribution TO coverage;
GRANT SELECT ON geographic_distribution TO coverage;
GRANT SELECT ON api_key_stats TO coverage;