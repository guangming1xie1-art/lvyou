-- =============================================================================
-- Travel Assistant Sample Data
-- 示例数据初始化脚本
-- =============================================================================
-- 创建时间: 2025-01-20
-- 版本: v1.0.0
-- 描述: 为 travel-assistant 项目提供示例测试数据
-- =============================================================================

-- =============================================================================
-- 1. 示例用户数据 (users)
-- =============================================================================

INSERT INTO users (email, username, password_hash, full_name, preferences_json, travel_style, budget_level) VALUES
('john.doe@example.com', 'john_doe', '$2a$10$rOzK4Z8kB7mV5jA.xxXxAu', 'John Doe', 
 '{"preferred_airlines": ["China Eastern", "Air China"], "meal_preference": "vegetarian", "accessibility_needs": []}', 
 'cultural', 'mid'),

('jane.smith@example.com', 'jane_smith', '$2a$10$rOzK4Z8kB7mV5jA.xxXxAu', 'Jane Smith',
 '{"preferred_hotels": ["Hilton", "Marriott"], "travel_insurance": true, "emergency_contact": "+1234567890"}',
 'relaxed', 'luxury'),

('mike.wilson@example.com', 'mike_wilson', '$2a$10$rOzK4Z8kB7mV5jA.xxXxAu', 'Mike Wilson',
 '{"budget_range": {"min": 500, "max": 1000}, "group_size": 4, "special_requests": ["quiet_room"]}',
 'adventure', 'budget'),

('sarah.johnson@example.com', 'sarah_j', '$2a$10$rOzK4Z8kB7mV5jA.xxXxAu', 'Sarah Johnson',
 '{"preferred_destinations": ["Europe", "Asia"], "travel_frequency": "monthly", "loyalty_programs": ["Starwood"]}',
 'cultural', 'luxury'),

('david.brown@example.com', 'david_b', '$2a$10$rOzK4Z8kB7mV5jA.xxXxAu', 'David Brown',
 '{"activity_types": ["hiking", "photography"], "accommodation_type": "boutique_hotels", "dietary_restrictions": ["gluten_free"]}',
 'adventure', 'mid');

-- =============================================================================
-- 2. 示例酒店数据 (hotels)
-- =============================================================================

INSERT INTO hotels (name, destination, price, rating, description, facilities, check_in_time, check_out_time) VALUES
('The Grand Plaza Hotel', 'Shanghai', 680.00, 4.5, 
 'Luxurious 5-star hotel in the heart of Shanghai with stunning city views and world-class amenities.',
 '["WiFi", "Pool", "Gym", "Spa", "Restaurant", "Room Service", "Business Center", "Concierge"]',
 '15:00:00', '11:00:00'),

('Beijing Royal Palace', 'Beijing', 1200.00, 4.8,
 'Historic luxury hotel near the Forbidden City, offering traditional Chinese hospitality with modern comfort.',
 '["WiFi", "Pool", "Spa", "Multiple Restaurants", "Tea House", "Cultural Tours", "Airport Shuttle"]',
 '14:00:00', '12:00:00'),

('Shenzhen Bay Resort', 'Shenzhen', 450.00, 4.2,
 'Modern business hotel with panoramic bay views, perfect for both leisure and business travelers.',
 '["WiFi", "Gym", "Business Center", "Meeting Rooms", "Harbor View", "Fine Dining"]',
 '15:00:00', '12:00:00'),

('Guangzhou Pearl Tower Hotel', 'Guangzhou', 320.00, 4.0,
 'Contemporary hotel in the commercial district with easy access to shopping and entertainment.',
 '["WiFi", "Gym", "Restaurant", "Bar", "Laundry Service", "24-hour Front Desk"]',
 '14:00:00', '11:00:00'),

('Chengdu Tea Garden Inn', 'Chengdu', 180.00, 4.6,
 'Charming boutique hotel with traditional Sichuan design, featuring a beautiful tea garden courtyard.',
 '["WiFi", "Traditional Courtyard", "Tea Service", "Cultural Activities", "Local Restaurant"]',
 '15:00:00', '11:00:00'),

('Hangzhou West Lake Villa', 'Hangzhou', 890.00, 4.7,
 'Elegant lakeside hotel with breathtaking views of West Lake, combining traditional architecture with luxury amenities.',
 '["WiFi", "Lake View", "Spa", "Traditional Gardens", "Fine Dining", "Boat Tours", "Cultural Programs"]',
 '15:00:00', '12:00:00'),

('Xi''an Ancient City Hotel', 'Xi''an', 280.00, 4.3,
 'Historic hotel within the ancient city walls, offering authentic Tang Dynasty cultural experience.',
 '["WiFi", "Cultural Shows", "Traditional Architecture", "Local Cuisine", "Historical Tours"]',
 '14:00:00', '11:00:00'),

('Suzhou Classical Gardens Hotel', 'Suzhou', 520.00, 4.4,
 'Luxury hotel featuring classical Suzhou garden design, located near the famous Lingering Garden.',
 '["WiFi", "Traditional Gardens", "Spa", "Cultural Workshops", "Fine Dining", "Private Gardens"]',
 '15:00:00', '11:00:00');

-- =============================================================================
-- 3. 示例航班数据 (flights)
-- =============================================================================

INSERT INTO flights (origin, destination, departure_date, return_date, departure_time, arrival_time, price, airline, flight_number, duration_minutes, available_seats) VALUES
('Beijing', 'Shanghai', '2025-02-15', '2025-02-20', '08:30:00', '10:45:00', 580.00, 'Air China', 'CA1851', 135, 45),

('Shanghai', 'Beijing', '2025-02-15', '2025-02-20', '14:20:00', '16:35:00', 620.00, 'China Eastern', 'MU5135', 135, 32),

('Beijing', 'Shenzhen', '2025-03-01', '2025-03-08', '09:15:00', '12:30:00', 1280.00, 'Air China', 'CA1315', 195, 28),

('Shanghai', 'Guangzhou', '2025-02-28', '2025-03-05', '16:45:00', '19:20:00', 890.00, 'China Southern', 'CZ3501', 155, 67),

('Beijing', 'Chengdu', '2025-03-10', NULL, '07:30:00', '10:45:00', 980.00, 'Air China', 'CA1403', 195, 0),

('Shanghai', 'Hangzhou', '2025-02-25', '2025-02-27', '11:30:00', '12:30:00', 280.00, 'Spring Airlines', '9C8883', 60, 23),

('Beijing', 'Xi''an', '2025-03-15', '2025-03-20', '13:20:00', '15:35:00', 750.00, 'Hainan Airlines', 'HU7885', 135, 41),

('Shanghai', 'Suzhou', '2025-04-01', '2025-04-03', '10:15:00', '11:00:00', 180.00, 'Juneyao Airlines', 'HO1255', 45, 15),

('Beijing', 'Shanghai', '2025-04-10', '2025-04-15', '19:50:00', '22:05:00', 680.00, 'Air China', 'CA1889', 135, 89),

('Shanghai', 'Beijing', '2025-04-10', '2025-04-15', '06:30:00', '08:45:00', 720.00, 'China Eastern', 'MU5101', 135, 56);

-- =============================================================================
-- 4. 示例景点数据 (attractions)
-- =============================================================================

INSERT INTO attractions (destination, name, category, rating, description, opening_hours, ticket_price, latitude, longitude, phone, website) VALUES
('Shanghai', 'The Bund', 'historic', 4.6,
 'Iconic waterfront promenade showcasing Shanghai''s colonial architecture and modern skyline.',
 '00:00-24:00', 0.00, 31.2397, 121.4900, '+86-21-6329-6888', 'https://www.thebund-shanghai.com'),

('Shanghai', 'Yu Garden', 'historic', 4.4,
 'Traditional Chinese garden featuring classical architecture, pavilions, and traditional shops.',
 '08:30-17:00', 40.00, 31.2276, 121.4919, '+86-21-6355-7938', 'https://www.yuyangarden.com'),

('Shanghai', 'Shanghai Disney Resort', 'entertainment', 4.7,
 'Magic kingdom featuring Disney characters, thrilling rides, and spectacular shows.',
 '08:00-22:00', 499.00, 31.1429, 121.6580, '+86-21-2099-8888', 'https://www.shanghaidisneyresort.com'),

('Shanghai', 'French Concession', 'historic', 4.5,
 'Historic area with tree-lined streets, European architecture, and trendy shops.',
 '00:00-24:00', 0.00, 31.2200, 121.4500, NULL, NULL),

('Beijing', 'Forbidden City', 'historic', 4.8,
 'Imperial palace complex showcasing 600 years of Chinese history and architecture.',
 '08:30-17:00', 60.00, 39.9163, 116.3972, '+86-10-8500-7421', 'https://www.dpm.org.cn'),

('Beijing', 'Great Wall (Badaling)', 'historic', 4.5,
 'Most visited section of the Great Wall offering spectacular mountain views.',
 '07:30-18:00', 45.00, 40.3597, 116.0144, '+86-10-8973-9886', 'https://www.mutianyugreatwall.com'),

('Beijing', 'Summer Palace', 'historic', 4.6,
 'Imperial garden featuring lakes, palaces, and traditional Chinese landscaping.',
 '06:30-18:00', 30.00, 39.9994, 116.2752, '+86-10-6288-1144', 'https://www.summerpalace.com.cn'),

('Beijing', 'Temple of Heaven', 'historic', 4.3,
 'Sacred complex where emperors prayed for good harvests, featuring stunning architecture.',
 '06:00-22:00', 15.00, 39.8838, 116.4074, '+86-10-6702-8866', NULL),

('Shenzhen', 'Splendid China Folk Village', 'historic', 4.2,
 'Miniature park showcasing China''s ethnic diversity and historical landmarks.',
 '09:00-21:30', 220.00, 22.5333, 113.9667, '+86-755-2660-2888', 'https://www.szc.cn'),

('Shenzhen', 'Window of the World', 'entertainment', 4.1,
 'Theme park featuring replicas of world-famous landmarks and cultural attractions.',
 '09:00-22:00', 200.00, 22.5396, 113.9755, '+86-755-2991-6666', 'https://www.szwworld.com'),

('Guangzhou', 'Canton Tower', 'historic', 4.0,
 'Iconic 604m television tower offering panoramic city views and entertainment facilities.',
 '09:00-22:30', 50.00, 23.1050, 113.3250, '+86-20-8933-8222', 'https://www.cantontower.com'),

('Guangzhou', 'Chimelong Safari Park', 'entertainment', 4.4,
 'Large safari park featuring diverse wildlife and exciting animal shows.',
 '09:30-17:30', 300.00, 23.0017, 113.3300, '+86-20-3471-9909', 'https://gzgz.gz.chimelong.com'),

('Chengdu', 'Giant Panda Breeding Research Base', 'historic', 4.8,
 'World-renowned panda conservation center where visitors can observe giant pandas.',
 '07:30-18:00', 58.00, 30.7328, 104.1512, '+86-28-8351-6666', 'https://www.panda.org.cn'),

('Chengdu', 'Jinli Ancient Street', 'food', 4.3,
 'Historic street lined with traditional Sichuan restaurants and cultural shops.',
 '00:00-24:00', 0.00, 30.6586, 104.0633, NULL, NULL),

('Hangzhou', 'West Lake', 'historic', 4.9,
 'UNESCO World Heritage site featuring beautiful lakes, gardens, and historic pagodas.',
 '00:00-24:00', 0.00, 30.2741, 120.1551, '+86-571-8717-9637', 'https://www.gotohz.com'),

('Hangzhou', 'Lingyin Temple', 'historic', 4.5,
 'Ancient Buddhist temple complex with impressive rock carvings and peaceful gardens.',
 '07:00-18:15', 30.00, 30.2406, 120.1017, '+86-571-8796-7729', 'https://www.lingyinsi.com'),

('Xi''an', 'Terracotta Army', 'historic', 4.7,
 'Ancient military museum featuring thousands of life-sized terracotta soldiers.',
 '08:30-18:00', 150.00, 34.3848, 109.2734, '+86-29-8139-9127', 'https://www.bmy.com.cn'),

('Xi''an', 'Xi''an City Wall', 'historic', 4.2,
 'Complete Ming Dynasty city wall offering bike riding and city views.',
 '08:00-22:00', 54.00, 34.2658, 108.9542, '+86-29-8727-5786', 'https://www.xacitywall.com'),

('Suzhou', 'Lingering Garden', 'historic', 4.6,
 'Classical Chinese garden recognized as a UNESCO World Heritage site.',
 '07:30-17:30', 30.00, 31.3237, 120.6258, '+86-512-6753-6666', 'https://www.szlyj.com'),

('Suzhou', 'Humble Administrator''s Garden', 'historic', 4.5,
 'Largest classical garden in Suzhou showcasing traditional Chinese garden design.',
 '07:30-17:30', 90.00, 31.3234, 120.6270, '+86-512-6751-0266', NULL);

-- =============================================================================
-- 5. 示例RAG文档数据 (rag_documents) - 可选
-- =============================================================================

INSERT INTO rag_documents (entity_type, entity_id, content, source, metadata) VALUES
('hotel', (SELECT id FROM hotels WHERE name = 'The Grand Plaza Hotel' LIMIT 1),
 'The Grand Plaza Hotel is a luxury 5-star property located in the heart of Shanghai. It offers world-class amenities including a spa, multiple restaurants, and stunning city views. The hotel is within walking distance of major shopping areas and transportation hubs. Guests praise the exceptional service quality and modern facilities.',
 'review', '{"rating": 4.5, "review_count": 2847, "amenities_score": 4.8}'),

('attraction', (SELECT id FROM attractions WHERE name = 'Forbidden City' LIMIT 1),
 'The Forbidden City is a palace complex in Dongcheng District, Beijing, China, at the center of the Imperial City of Beijing. It is surrounded by numerous temples and halls. The Forbidden City is a rectangular palace complex covering 720,000 square meters (7.8 hectares). It is the world''s largest palace complex and the most complete ancient wooden structure in the world.',
 'wiki', '{"visitors_per_year": 17000000, "unesco_status": "World Heritage", "dynasty": "Ming and Qing"}'),

('attraction', (SELECT id FROM attractions WHERE name = 'Giant Panda Breeding Research Base' LIMIT 1),
 'The Chengdu Research Base of Giant Panda Breeding is located in Chengdu, Sichuan Province, China. It was established in 1987 with the aim of creating a research base for the giant panda breeding program. The base houses over 100 giant pandas and is one of the most popular tourist attractions in China.',
 'official', '{"panda_count": 120, "conservation_status": "vulnerable", "research_focus": "breeding"}'),

('flight', (SELECT id FROM flights WHERE flight_number = 'CA1851' LIMIT 1),
 'Air China Flight CA1851 operates daily between Beijing Capital International Airport (PEK) and Shanghai Pudong International Airport (PVG). The flight duration is approximately 2 hours and 15 minutes. The airline offers complimentary meals and beverages on this route. Passengers can earn frequent flyer miles on the PhoenixMiles program.',
 'airline', '{"aircraft_type": "Boeing 737-800", "frequency": "daily", "meal_service": "complimentary"}');

-- =============================================================================
-- 6. 示例审计日志数据 (audit_logs) - 可选
-- =============================================================================

INSERT INTO audit_logs (user_id, action, resource_type, resource_id, details, ip_address, user_agent) VALUES
((SELECT id FROM users WHERE username = 'john_doe' LIMIT 1), 'search', 'hotels', (SELECT id FROM hotels WHERE destination = 'Shanghai' LIMIT 1),
 '{"search_criteria": {"destination": "Shanghai", "check_in": "2025-02-15", "check_out": "2025-02-20", "budget_max": 1000}}',
 '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),

((SELECT id FROM users WHERE username = 'jane_smith' LIMIT 1), 'book', 'hotel', (SELECT id FROM hotels WHERE name = 'Beijing Royal Palace' LIMIT 1),
 '{"booking_details": {"nights": 5, "room_type": "deluxe", "total_price": 6000, "guests": 2}}',
 '192.168.1.101', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'),

((SELECT id FROM users WHERE username = 'mike_wilson' LIMIT 1), 'search', 'flights', (SELECT id FROM flights WHERE origin = 'Beijing' LIMIT 1),
 '{"search_criteria": {"origin": "Beijing", "destination": "Shanghai", "departure_date": "2025-03-01", "passengers": 1}}',
 '192.168.1.102', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'),

((SELECT id FROM users WHERE username = 'sarah_j' LIMIT 1), 'recommend', 'attractions', (SELECT id FROM attractions WHERE destination = 'Shanghai' LIMIT 1),
 '{"recommendation_reason": "Based on user''s cultural travel style and luxury budget level", "similar_users": 15}',
 '192.168.1.103', 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15'),

((SELECT id FROM users WHERE username = 'david_b' LIMIT 1), 'search', 'attractions', (SELECT id FROM attractions WHERE category = 'historic' LIMIT 1),
 '{"search_criteria": {"category": "historic", "rating_min": 4.0, "destination": "Beijing"}}',
 '192.168.1.104', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36');

-- =============================================================================
-- 7. 示例查询 - 验证数据完整性
-- =============================================================================

-- 检查插入的数据
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'hotels', COUNT(*) FROM hotels
UNION ALL
SELECT 'flights', COUNT(*) FROM flights
UNION ALL
SELECT 'attractions', COUNT(*) FROM attractions
UNION ALL
SELECT 'rag_documents', COUNT(*) FROM rag_documents
UNION ALL
SELECT 'audit_logs', COUNT(*) FROM audit_logs;

-- =============================================================================
-- 示例数据初始化完成
-- =============================================================================