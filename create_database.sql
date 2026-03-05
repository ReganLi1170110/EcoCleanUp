-- EcoCleanUp Hub Database Creation Script
-- COMP639 Individual Project

-- Drop tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS registrations CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create users table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('volunteer', 'event_leader', 'admin')),
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    full_name VARCHAR(100) NOT NULL,
    home_address TEXT,
    contact_number VARCHAR(20),
    environmental_interests TEXT,
    profile_image VARCHAR(255) DEFAULT 'default_profile.png',
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Create events table
CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    event_name VARCHAR(200) NOT NULL,
    location VARCHAR(200) NOT NULL,
    event_date DATE NOT NULL,
    event_time TIME NOT NULL,
    duration VARCHAR(50),
    supplies TEXT,
    safety_instructions TEXT,
    created_by INTEGER NOT NULL REFERENCES users(user_id),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'upcoming' CHECK (status IN ('upcoming', 'completed', 'cancelled')),
    event_type VARCHAR(50) DEFAULT 'general',
    bags_collected INTEGER DEFAULT 0,
    recyclables_sorted INTEGER DEFAULT 0,
    CONSTRAINT event_date_check CHECK (event_date >= CURRENT_DATE - INTERVAL '1 year')
);

-- Create registrations table
CREATE TABLE registrations (
    registration_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    event_id INTEGER NOT NULL REFERENCES events(event_id),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'registered' CHECK (status IN ('registered', 'cancelled', 'attended', 'no_show')),
    attendance_status VARCHAR(20) DEFAULT 'pending' CHECK (attendance_status IN ('pending', 'attended', 'absent')),
    feedback_rating INTEGER CHECK (feedback_rating >= 1 AND feedback_rating <= 5),
    feedback_comment TEXT,
    feedback_date TIMESTAMP,
    UNIQUE(user_id, event_id)
);

-- Create notifications table
CREATE TABLE notifications (
    notification_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    event_id INTEGER REFERENCES events(event_id),
    message TEXT NOT NULL,
    sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE
);

-- Create indexes for better performance
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_events_date ON events(event_date);
CREATE INDEX idx_events_created_by ON events(created_by);
CREATE INDEX idx_registrations_user ON registrations(user_id);
CREATE INDEX idx_registrations_event ON registrations(event_id);
CREATE INDEX idx_notifications_user ON notifications(user_id);