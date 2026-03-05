-- EcoCleanUp Hub Database Population Script
-- COMP639 Individual Project

-- First, clear existing data (if any)
TRUNCATE notifications, registrations, events, users RESTART IDENTITY CASCADE;

-- Insert users (passwords are hashed versions of 'Password123!')
-- Use password_hash_generator.py to generate these hashes

-- Insert 2 admins
INSERT INTO users (username, email, password_hash, role, status, full_name, home_address, contact_number, environmental_interests, profile_image) VALUES
('admin_sarah', 'sarah.johnson@ecocleanup.org', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'admin', 'active', 'Sarah Johnson', '42 Green Lane, Eco City', '021-555-0123', 'Environmental policy, Community organizing', 'default_profile.png'),
('admin_michael', 'michael.chen@ecocleanup.org', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'admin', 'active', 'Michael Chen', '15 Sustainable Street, Eco City', '021-555-0456', 'Climate action, Environmental education', 'default_profile.png');

-- Insert 5 event leaders
INSERT INTO users (username, email, password_hash, role, status, full_name, home_address, contact_number, environmental_interests, profile_image) VALUES
('leader_emma', 'emma.wilson@ecocleanup.org', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'event_leader', 'active', 'Emma Wilson', '78 Beach Road, Coastal Town', '021-555-0789', 'Beach cleanup, Marine conservation', 'default_profile.png'),
('leader_james', 'james.thompson@ecocleanup.org', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'event_leader', 'active', 'James Thompson', '23 Forest Avenue, Woodland Heights', '021-555-0234', 'Forest conservation, Recycling', 'default_profile.png'),
('leader_lisa', 'lisa.rodriguez@ecocleanup.org', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'event_leader', 'active', 'Lisa Rodriguez', '56 Park View, Green Valley', '021-555-0678', 'Park maintenance, Community gardens', 'default_profile.png'),
('leader_david', 'david.kim@ecocleanup.org', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'event_leader', 'active', 'David Kim', '89 Riverside Drive, River City', '021-555-0345', 'River cleanup, Water conservation', 'default_profile.png'),
('leader_rachel', 'rachel.green@ecocleanup.org', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'event_leader', 'active', 'Rachel Green', '34 Sustainability Way, Eco City', '021-555-0890', 'Zero waste, Community education', 'default_profile.png');

-- Insert 20 volunteers
INSERT INTO users (username, email, password_hash, role, status, full_name, home_address, contact_number, environmental_interests, profile_image) VALUES
('volunteer_anna', 'anna.smith@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'volunteer', 'active', 'Anna Smith', '123 Main Street, Eco City', '021-111-2233', 'Beach cleanups, Recycling', 'default_profile.png'),
('volunteer_ben', 'ben.jones@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'volunteer', 'active', 'Ben Jones', '45 Oak Avenue, Green Valley', '021-222-3344', 'Tree planting, Park maintenance', 'default_profile.png'),
('volunteer_chloe', 'chloe.williams@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'volunteer', 'active', 'Chloe Williams', '78 Pine Road, Woodland Heights', '021-333-4455', 'River cleanups, Environmental education', 'default_profile.png'),
('volunteer_daniel', 'daniel.brown@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'volunteer', 'active', 'Daniel Brown', '12 Elm Street, Coastal Town', '021-444-5566', 'Beach cleanups, Marine conservation', 'default_profile.png'),
('volunteer_emma', 'emma.davis@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'volunteer', 'active', 'Emma Davis', '34 Cedar Lane, River City', '021-555-6677', 'Recycling, Zero waste living', 'default_profile.png'),
('volunteer_finn', 'finn.miller@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'volunteer', 'active', 'Finn Miller', '56 Birch Street, Eco City', '021-666-7788', 'Community gardens, Composting', 'default_profile.png'),
('volunteer_grace', 'grace.wilson@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'volunteer', 'active', 'Grace Wilson', '89 Spruce Avenue, Green Valley', '021-777-8899', 'Park cleanups, Wildlife protection', 'default_profile.png'),
('volunteer_henry', 'henry.taylor@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'volunteer', 'active', 'Henry Taylor', '23 Maple Drive, Woodland Heights', '021-888-9900', 'Forest conservation, Hiking trail maintenance', 'default_profile.png'),
('volunteer_isla', 'isla.anderson@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'volunteer', 'active', 'Isla Anderson', '45 Willow Road, Coastal Town', '021-999-0011', 'Beach cleanups, Plastic reduction', 'default_profile.png'),
('volunteer_jack', 'jack.thomas@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'volunteer', 'active', 'Jack Thomas', '67 Poplar Lane, River City', '021-111-2234', 'River cleanups, Water quality monitoring', 'default_profile.png'),
('volunteer_kate', 'kate.white@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'volunteer', 'active', 'Kate White', '89 Ash Court, Eco City', '021-222-3345', 'Environmental education, School programs', 'default_profile.png'),
('volunteer_liam', 'liam.harris@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'volunteer', 'active', 'Liam Harris', '12 Fir Terrace, Green Valley', '021-333-4456', 'Tree planting, Urban forestry', 'default_profile.png'),
('volunteer_mia', 'mia.martin@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'volunteer', 'active', 'Mia Martin', '34 Cypress Way, Woodland Heights', '021-444-5567', 'Community cleanups, Litter prevention', 'default_profile.png'),
('volunteer_noah', 'noah.clark@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'volunteer', 'active', 'Noah Clark', '56 Redwood Street, Coastal Town', '021-555-6678', 'Marine conservation, Beach ecology', 'default_profile.png'),
('volunteer_olivia', 'olivia.lewis@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'volunteer', 'active', 'Olivia Lewis', '78 Sequoia Avenue, River City', '021-666-7789', 'Waste reduction, Recycling programs', 'default_profile.png'),
('volunteer_peter', 'peter.walker@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'volunteer', 'active', 'Peter Walker', '90 Magnolia Drive, Eco City', '021-777-8890', 'Sustainable living, Composting', 'default_profile.png'),
('volunteer_quinn', 'quinn.hall@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'volunteer', 'active', 'Quinn Hall', '21 Dogwood Lane, Green Valley', '021-888-9901', 'Park restoration, Native plants', 'default_profile.png'),
('volunteer_rose', 'rose.young@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'volunteer', 'active', 'Rose Young', '43 Sycamore Road, Woodland Heights', '021-999-0012', 'Climate action, Environmental advocacy', 'default_profile.png'),
('volunteer_sam', 'sam.king@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'volunteer', 'active', 'Sam King', '65 Hickory Street, Coastal Town', '021-111-3345', 'Beach cleanups, Ocean conservation', 'default_profile.png'),
('volunteer_tess', 'tess.wright@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'volunteer', 'active', 'Tess Wright', '87 Beech Court, River City', '021-222-4456', 'Community gardening, Food sustainability', 'default_profile.png'),
('volunteer_uma', 'uma.patel@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'volunteer', 'active', 'Uma Patel', '13 Chestnut Way, Eco City', '021-333-5567', 'Environmental justice, Clean energy', 'default_profile.png'),
('volunteer_victor', 'victor.chen@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'volunteer', 'active', 'Victor Chen', '24 Hemlock Terrace, Green Valley', '021-444-6678', 'Recycling innovation, Circular economy', 'default_profile.png');

-- Insert events (20 events)
INSERT INTO events (event_name, location, event_date, event_time, duration, supplies, safety_instructions, created_by, event_type, status, bags_collected, recyclables_sorted) VALUES
('Spring Beach Cleanup', 'Sunset Beach, Coastal Town', '2026-04-15', '09:00:00', '3 hours', 'Gloves, bags, litter pickers provided. Bring water and sunscreen.', 'Wear closed-toe shoes. Stay hydrated. Watch for sharp objects.', 3, 'beach', 'upcoming', 0, 0),
('Riverbank Restoration', 'Riverside Park, River City', '2026-04-22', '10:00:00', '4 hours', 'Gloves, bags, tools provided. Bring water and snacks.', 'Be careful near water. Wear appropriate footwear. Stay with your group.', 5, 'river', 'upcoming', 0, 0),
('Park Cleanup and Planting', 'Central Park, Eco City', '2026-04-08', '13:00:00', '3 hours', 'Gardening tools, plants, gloves provided. Bring water.', 'Use tools safely. Wear sun protection. Follow staff instructions.', 4, 'park', 'upcoming', 0, 0),
('Forest Trail Maintenance', 'Woodland Heights Forest', '2026-04-29', '08:30:00', '5 hours', 'Tools provided. Bring lunch, water, and insect repellent.', 'Stay on marked trails. Wear long pants and sturdy boots. Check for ticks.', 3, 'forest', 'upcoming', 0, 0),
('Community Recycling Drive', 'Green Valley Community Center', '2026-04-12', '09:00:00', '6 hours', 'Sorting tables, bins provided. Bring gloves.', 'Lift with proper technique. Wear mask if sorting dusty items.', 4, 'recycling', 'upcoming', 0, 0),
('Urban Garden Cleanup', 'Eco City Community Garden', '2026-05-03', '10:00:00', '3 hours', 'Gardening tools, gloves, bags provided.', 'Use tools carefully. Wear sun protection. Stay hydrated.', 5, 'garden', 'upcoming', 0, 0),
('Harbor Cleanup', 'Marina Bay, Coastal Town', '2026-05-10', '09:30:00', '4 hours', 'Boats, gloves, collection bags provided. Life jackets required.', 'Must know how to swim. Follow boat safety rules. Wear life jacket at all times.', 3, 'beach', 'upcoming', 0, 0),
('School Environmental Day', 'Sunset Elementary, Eco City', '2026-05-17', '09:00:00', '5 hours', 'Educational materials, craft supplies, gloves.', 'Work with children - be patient and friendly. Follow school protocols.', 6, 'education', 'upcoming', 0, 0),
('Wetland Restoration', 'Marshlands Preserve, River City', '2026-05-24', '08:00:00', '6 hours', 'Waders, gloves, tools provided. Bring lunch and water.', 'Watch for wildlife. Stay in designated areas. Wear waterproof boots.', 5, 'wetland', 'upcoming', 0, 0),
('Mountain Trail Cleanup', 'Lookout Point, Green Valley', '2026-05-31', '07:30:00', '7 hours', 'Tools provided. Bring hiking gear, lunch, plenty of water.', 'Strenuous hike - assess your fitness level. Bring first aid kit. Stay on trail.', 4, 'forest', 'upcoming', 0, 0),
('Completed Beach Cleanup', 'North Beach, Coastal Town', '2026-03-01', '10:00:00', '3 hours', 'Gloves and bags provided.', 'Standard safety precautions.', 3, 'beach', 'completed', 45, 30),
('Completed River Cleanup', 'South River Park, River City', '2026-03-08', '09:00:00', '4 hours', 'All equipment provided.', 'Water safety rules apply.', 5, 'river', 'completed', 38, 25),
('Completed Park Day', 'Memorial Park, Eco City', '2026-03-15', '13:00:00', '3 hours', 'Gardening tools provided.', 'Use tools safely.', 4, 'park', 'completed', 22, 18),
('Completed Forest Day', 'Pine Forest, Woodland Heights', '2026-03-22', '08:00:00', '5 hours', 'Trail tools provided.', 'Forest safety rules.', 3, 'forest', 'completed', 15, 10),
('Completed Recycling Event', 'Recycling Center, Green Valley', '2026-03-29', '09:00:00', '6 hours', 'Sorting equipment provided.', 'Safety gear required.', 4, 'recycling', 'completed', 0, 120),
('Evening Beach Cleanup', 'Sunset Beach, Coastal Town', '2026-06-05', '17:00:00', '2 hours', 'Gloves, bags, headlamps provided.', 'Bring flashlight. Stay in groups. Watch tide times.', 3, 'beach', 'upcoming', 0, 0),
('Weekend Park Cleanup', 'Riverside Park, River City', '2026-06-06', '09:00:00', '4 hours', 'All supplies provided. Bring water.', 'Wear sun protection. Stay hydrated.', 5, 'park', 'upcoming', 0, 0),
('Tree Planting Day', 'Green Valley Reserve', '2026-06-07', '09:00:00', '5 hours', 'Seedlings, tools, gloves provided. Bring lunch.', 'Proper planting technique will be taught. Wear sturdy shoes.', 4, 'forest', 'upcoming', 0, 0),
('Community Cleanup Challenge', 'Eco City Downtown', '2026-06-13', '08:00:00', '4 hours', 'All equipment provided. Prizes for most collected!', 'Stay with your team. Watch for traffic. Use provided safety vests.', 6, 'general', 'upcoming', 0, 0),
('Zero Waste Workshop', 'Community Center, Eco City', '2026-06-14', '14:00:00', '2 hours', 'Materials provided. Bring a notebook.', 'Indoor event - comfortable clothing.', 6, 'education', 'upcoming', 0, 0);

-- Insert registrations (at least 20)
INSERT INTO registrations (user_id, event_id, registration_date, status, attendance_status, feedback_rating, feedback_comment, feedback_date) VALUES
(8, 1, '2026-03-15 10:30:00', 'registered', 'pending', NULL, NULL, NULL),
(9, 1, '2026-03-16 14:20:00', 'registered', 'pending', NULL, NULL, NULL),
(10, 1, '2026-03-17 09:45:00', 'registered', 'pending', NULL, NULL, NULL),
(11, 2, '2026-03-18 11:15:00', 'registered', 'pending', NULL, NULL, NULL),
(12, 2, '2026-03-18 16:30:00', 'registered', 'pending', NULL, NULL, NULL),
(13, 3, '2026-03-19 08:20:00', 'registered', 'pending', NULL, NULL, NULL),
(14, 3, '2026-03-20 13:40:00', 'registered', 'pending', NULL, NULL, NULL),
(15, 4, '2026-03-21 10:10:00', 'registered', 'pending', NULL, NULL, NULL),
(16, 5, '2026-03-22 09:30:00', 'registered', 'pending', NULL, NULL, NULL),
(17, 5, '2026-03-23 14:50:00', 'registered', 'pending', NULL, NULL, NULL),
(18, 6, '2026-03-24 11:25:00', 'registered', 'pending', NULL, NULL, NULL),
(19, 7, '2026-03-25 15:15:00', 'registered', 'pending', NULL, NULL, NULL),
(20, 8, '2026-03-26 08:45:00', 'registered', 'pending', NULL, NULL, NULL),
(21, 9, '2026-03-27 12:30:00', 'registered', 'pending', NULL, NULL, NULL),
(22, 10, '2026-03-28 10:00:00', 'registered', 'pending', NULL, NULL, NULL),
(8, 11, '2026-02-15 09:00:00', 'registered', 'attended', 5, 'Great event! Cleaned up so much trash and met wonderful people.', '2026-03-02 18:30:00'),
(9, 11, '2026-02-16 11:20:00', 'registered', 'attended', 4, 'Well organized, but could use more gloves next time.', '2026-03-02 19:15:00'),
(10, 11, '2026-02-17 14:30:00', 'registered', 'attended', 5, 'Loved it! Will definitely come again.', '2026-03-03 10:45:00'),
(11, 12, '2026-02-20 08:15:00', 'registered', 'attended', 4, 'Good event, river looks much cleaner now.', '2026-03-09 16:20:00'),
(12, 12, '2026-02-21 13:40:00', 'registered', 'attended', 5, 'Excellent organization and great volunteers!', '2026-03-09 20:10:00'),
(13, 13, '2026-03-01 09:30:00', 'registered', 'attended', 3, 'Good effort but more coordination needed.', '2026-03-16 11:30:00'),
(14, 14, '2026-03-05 10:45:00', 'registered', 'attended', 5, 'Beautiful forest, happy to help preserve it.', '2026-03-23 14:25:00'),
(15, 15, '2026-03-10 08:30:00', 'registered', 'attended', 4, 'Learned a lot about recycling.', '2026-03-30 09:50:00'),
(16, 15, '2026-03-11 15:20:00', 'registered', 'attended', 5, 'Great educational event!', '2026-03-30 17:40:00'),
(17, 15, '2026-03-12 11:10:00', 'registered', 'attended', 4, 'Well run, good facilities.', '2026-03-31 08:15:00');

-- Insert notifications
INSERT INTO notifications (user_id, event_id, message, sent_date, is_read) VALUES
(8, 1, 'Reminder: Spring Beach Cleanup is on April 15th at 9:00 AM', '2026-04-01 09:00:00', FALSE),
(9, 1, 'Reminder: Spring Beach Cleanup is on April 15th at 9:00 AM', '2026-04-01 09:00:00', FALSE),
(10, 1, 'Reminder: Spring Beach Cleanup is on April 15th at 9:00 AM', '2026-04-01 09:00:00', FALSE),
(11, 2, 'Reminder: Riverbank Restoration is on April 22nd at 10:00 AM', '2026-04-08 10:00:00', FALSE),
(12, 2, 'Reminder: Riverbank Restoration is on April 22nd at 10:00 AM', '2026-04-08 10:00:00', FALSE),
(13, 3, 'Reminder: Park Cleanup and Planting is on April 8th at 1:00 PM', '2026-04-01 13:00:00', FALSE);

-- Create some test users with simple passwords for easy testing
-- Note: These are additional users for testing purposes
-- Password for all test users: 'Test123!'
INSERT INTO users (username, email, password_hash, role, status, full_name, home_address, contact_number, environmental_interests, profile_image) VALUES
('test_volunteer', 'test.volunteer@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'volunteer', 'active', 'Test Volunteer', '123 Test Street, Eco City', '021-123-4567', 'Testing, Beach cleanups', 'default_profile.png'),
('test_leader', 'test.leader@ecocleanup.org', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'event_leader', 'active', 'Test Leader', '456 Leader Lane, Eco City', '021-234-5678', 'Event organization, Training', 'default_profile.png'),
('test_admin', 'test.admin@ecocleanup.org', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFXyKJYkYzUyZLC', 'admin', 'active', 'Test Admin', '789 Admin Ave, Eco City', '021-345-6789', 'System administration, Analytics', 'default_profile.png');