-- =============================================================================
-- Travel Assistant Sample Data
-- 示例数据初始化脚本
-- =============================================================================
-- 创建时间: 2025-01-20
-- 版本: v1.0.0
-- 描述: 为 travel-assistant 项目提供示例测试数据
-- 修复时间: 2025-01-23
-- 修复说明: 与 Java 实体类字段保持一致，移除不存在的字段，添加缺失的字段
-- =============================================================================

-- =============================================================================
-- 1. 示例用户数据 (users)
-- FIXED: 移除 full_name, travel_style, budget_level 字段，添加 is_active, last_login 字段
-- FIXED: 将 travel_style 和 budget_level 合并到 preferences_json 中
-- =============================================================================
INSERT INTO users (email, username, password_hash, is_active, last_login, preferences_json) VALUES
('john.doe@example.com', 'john_doe', '$2a$10$rOzK4Z8kB7mV5jA.xxXxAu', TRUE, NULL,
 '{"preferred_airlines": ["China Eastern", "Air China"], "meal_preference": "vegetarian", "accessibility_needs": [], "travel_style": "cultural", "budget_level": "mid"}'),

('jane.smith@example.com', 'jane_smith', '$2a$10$rOzK4Z8kB7mV5jA.xxXxAu', TRUE, NULL,
 '{"preferred_hotels": ["Hilton", "Marriott"], "travel_insurance": true, "emergency_contact": "+1234567890", "travel_style": "relaxed", "budget_level": "luxury"}'),

('mike.wilson@example.com', 'mike_wilson', '$2a$10$rOzK4Z8kB7mV5jA.xxXxAu', TRUE, NULL,
 '{"budget_range": {"min": 500, "max": 1000}, "group_size": 4, "special_requests": ["quiet_room"], "travel_style": "adventure", "budget_level": "budget"}'),

('sarah.johnson@example.com', 'sarah_j', '$2a$10$rOzK4Z8kB7mV5jA.xxXxAu', TRUE, NULL,
 '{"preferred_destinations": ["Europe", "Asia"], "travel_frequency": "monthly", "loyalty_programs": ["Starwood"], "travel_style": "cultural", "budget_level": "luxury"}'),

('david.brown@example.com', 'david_b', '$2a$10$rOzK4Z8kB7mV5jA.xxXxAu', TRUE, NULL,
 '{"activity_types": ["hiking", "photography"], "accommodation_type": "boutique_hotels", "dietary_restrictions": ["gluten_free"], "travel_style": "adventure", "budget_level": "mid"}');

-- =============================================================================
-- 2. 示例酒店数据 (hotels)
-- FIXED: 移除 check_in_time 和 check_out_time，使用 check_in_date 和 check_out_date 代替
-- =============================================================================

INSERT INTO hotels (name, destination, price, rating, description, facilities, check_in_date, check_out_date) VALUES
('The Grand Plaza Hotel', 'Shanghai', 680.00, 4.5,
 'Luxurious 5-star hotel in the heart of Shanghai with stunning city views and world-class amenities.',
 '["WiFi", "Pool", "Gym", "Spa", "Restaurant", "Room Service", "Business Center", "Concierge"]',
 '2025-02-15', '2025-02-20'),

('Beijing Royal Palace', 'Beijing', 1200.00, 4.8,
 'Historic luxury hotel near the Forbidden City, offering traditional Chinese hospitality with modern comfort.',
 '["WiFi", "Pool", "Spa", "Multiple Restaurants", "Tea House", "Cultural Tours", "Airport Shuttle"]',
 '2025-03-01', '2025-03-08'),

('Shenzhen Bay Resort', 'Shenzhen', 450.00, 4.2,
 'Modern business hotel with panoramic bay views, perfect for both leisure and business travelers.',
 '["WiFi", "Gym", "Business Center", "Meeting Rooms", "Harbor View", "Fine Dining"]',
 '2025-02-28', '2025-03-05'),

('Guangzhou Pearl Tower Hotel', 'Guangzhou', 320.00, 4.0,
 'Contemporary hotel in the commercial district with easy access to shopping and entertainment.',
 '["WiFi", "Gym", "Restaurant", "Bar", "Laundry Service", "24-hour Front Desk"]',
 '2025-03-10', '2025-03-15'),

('Chengdu Tea Garden Inn', 'Chengdu', 180.00, 4.6,
 'Charming boutique hotel with traditional Sichuan design, featuring a beautiful tea garden courtyard.',
 '["WiFi", "Traditional Courtyard", "Tea Service", "Cultural Activities", "Local Restaurant"]',
 '2025-02-25', '2025-02-27'),

('Hangzhou West Lake Villa', 'Hangzhou', 890.00, 4.7,
 'Elegant lakeside hotel with breathtaking views of West Lake, combining traditional architecture with luxury amenities.',
 '["WiFi", "Lake View", "Spa", "Traditional Gardens", "Fine Dining", "Boat Tours", "Cultural Programs"]',
 '2025-04-01', '2025-04-03'),

('Xi''an Ancient City Hotel', 'Xi''an', 280.00, 4.3,
 'Historic hotel within the ancient city walls, offering authentic Tang Dynasty cultural experience.',
 '["WiFi", "Cultural Shows", "Traditional Architecture", "Local Cuisine", "Historical Tours"]',
 '2025-03-15', '2025-03-20'),

('Suzhou Classical Gardens Hotel', 'Suzhou', 520.00, 4.4,
 'Luxury hotel featuring classical Suzhou garden design, located near the famous Lingering Garden.',
 '["WiFi", "Traditional Gardens", "Spa", "Cultural Workshops", "Fine Dining", "Private Gardens"]',
 '2025-04-10', '2025-04-15');

-- =============================================================================
-- 3. 示例航班数据 (flights)
-- FIXED: 移除 departure_time, arrival_time, flight_number, available_seats 字段
-- FIXED: 将 duration_minutes 改为 duration 以匹配 Flight.java 实体
-- =============================================================================

INSERT INTO flights (origin, destination, departure_date, return_date, price, airline, duration) VALUES
('Beijing', 'Shanghai', '2025-02-15', '2025-02-20', 580.00, 'Air China', 135),

('Shanghai', 'Beijing', '2025-02-15', '2025-02-20', 620.00, 'China Eastern', 135),

('Beijing', 'Shenzhen', '2025-03-01', '2025-03-08', 1280.00, 'Air China', 195),

('Shanghai', 'Guangzhou', '2025-02-28', '2025-03-05', 890.00, 'China Southern', 155),

('Beijing', 'Chengdu', '2025-03-10', NULL, 980.00, 'Air China', 195),

('Shanghai', 'Hangzhou', '2025-02-25', '2025-02-27', 280.00, 'Spring Airlines', 60),

('Beijing', 'Xi''an', '2025-03-15', '2025-03-20', 750.00, 'Hainan Airlines', 135),

('Shanghai', 'Suzhou', '2025-04-01', '2025-04-03', 180.00, 'Juneyao Airlines', 45),

('Beijing', 'Shanghai', '2025-04-10', '2025-04-15', 680.00, 'Air China', 135),

('Shanghai', 'Beijing', '2025-04-10', '2025-04-15', 720.00, 'China Eastern', 135);

-- =============================================================================
-- 4. 示例景点数据 (attractions)
-- FIXED: 移除 ticket_price, latitude, longitude, phone, website 字段
-- FIXED: 添加 tags 字段（核心字段，用于搜索和推荐）
-- =============================================================================
INSERT INTO attractions (destination, name, category, rating, description, opening_hours, tags) VALUES
('Shanghai', 'The Bund', 'historic', 4.6,
 'Iconic waterfront promenade showcasing Shanghai''s colonial architecture and modern skyline.',
 '00:00-24:00', '["historic", "landmark", "waterfront", "photography", "architecture"]'),

('Shanghai', 'Yu Garden', 'historic', 4.4,
 'Traditional Chinese garden featuring classical architecture, pavilions, and traditional shops.',
 '08:30-17:00', '["historic", "garden", "culture", "traditional", "architecture"]'),

('Shanghai', 'Shanghai Disney Resort', 'entertainment', 4.7,
 'Magic kingdom featuring Disney characters, thrilling rides, and spectacular shows.',
 '08:00-22:00', '["entertainment", "family", "theme_park", "kids", "adventure"]'),

('Shanghai', 'French Concession', 'historic', 4.5,
 'Historic area with tree-lined streets, European architecture, and trendy shops.',
 '00:00-24:00', '["historic", "architecture", "walking", "shopping", "culture"]'),

('Beijing', 'Forbidden City', 'historic', 4.8,
 'Imperial palace complex showcasing 600 years of Chinese history and architecture.',
 '08:30-17:00', '["historic", "palace", "culture", "unesco", "landmark", "architecture"]'),

('Beijing', 'Great Wall (Badaling)', 'historic', 4.5,
 'Most visited section of the Great Wall offering spectacular mountain views.',
 '07:30-18:00', '["historic", "landmark", "hiking", "unesco", "adventure", "mountain"]'),

('Beijing', 'Summer Palace', 'historic', 4.6,
 'Imperial garden featuring lakes, palaces, and traditional Chinese landscaping.',
 '06:30-18:00', '["historic", "garden", "lake", "culture", "relaxation", "nature"]'),

('Beijing', 'Temple of Heaven', 'historic', 4.3,
 'Sacred complex where emperors prayed for good harvests, featuring stunning architecture.',
 '06:00-22:00', '["historic", "culture", "religion", "architecture", "temple"]'),

('Shenzhen', 'Splendid China Folk Village', 'historic', 4.2,
 'Miniature park showcasing China''s ethnic diversity and historical landmarks.',
 '09:00-21:30', '["historic", "culture", "family", "entertainment", "folk"]'),

('Shenzhen', 'Window of the World', 'entertainment', 4.1,
 'Theme park featuring replicas of world-famous landmarks and cultural attractions.',
 '09:00-22:00', '["entertainment", "family", "theme_park", "international", "landmark"]'),

('Guangzhou', 'Canton Tower', 'historic', 4.0,
 'Iconic 604m television tower offering panoramic city views and entertainment facilities.',
 '09:00-22:30', '["landmark", "modern", "city_view", "entertainment", "architecture"]'),

('Guangzhou', 'Chimelong Safari Park', 'entertainment', 4.4,
 'Large safari park featuring diverse wildlife and exciting animal shows.',
 '09:30-17:30', '["wildlife", "family", "animals", "nature", "adventure"]'),

('Chengdu', 'Giant Panda Breeding Research Base', 'historic', 4.8,
 'World-renowned panda conservation center where visitors can observe giant pandas.',
 '07:30-18:00', '["wildlife", "animals", "nature", "family", "culture", "conservation"]'),

('Chengdu', 'Jinli Ancient Street', 'food', 4.3,
 'Historic street lined with traditional Sichuan restaurants and cultural shops.',
 '00:00-24:00', '["food", "historic", "culture", "nightlife", "traditional", "shopping"]'),

('Hangzhou', 'West Lake', 'historic', 4.9,
 'UNESCO World Heritage site featuring beautiful lakes, gardens, and historic pagodas.',
 '00:00-24:00', '["nature", "lake", "landscape", "unesco", "relaxation", "garden"]'),

('Hangzhou', 'Lingyin Temple', 'historic', 4.5,
 'Ancient Buddhist temple complex with impressive rock carvings and peaceful gardens.',
 '07:00-18:15', '["historic", "culture", "religion", "temple", "nature", "architecture"]'),

('Xi''an', 'Terracotta Army', 'historic', 4.7,
 'Ancient military museum featuring thousands of life-sized terracotta soldiers.',
 '08:30-18:00', '["historic", "archaeology", "culture", "unesco", "museum", "ancient"]'),

('Xi''an', 'Xi''an City Wall', 'historic', 4.2,
 'Complete Ming Dynasty city wall offering bike riding and city views.',
 '08:00-22:00', '["historic", "landmark", "architecture", "cycling", "city_view", "ancient"]'),

('Suzhou', 'Lingering Garden', 'historic', 4.6,
 'Classical Chinese garden recognized as a UNESCO World Heritage site.',
 '07:30-17:30', '["historic", "garden", "unesco", "culture", "architecture", "landscape"]'),

('Suzhou', 'Humble Administrator''s Garden', 'historic', 4.5,
 'Largest classical garden in Suzhou showcasing traditional Chinese garden design.',
 '07:30-17:30', '["historic", "garden", "unesco", "culture", "architecture", "landscape"]');

-- =============================================================================
-- 5. 示例RAG文档数据 (rag_documents) - 可选
-- FIXED: 移除对 flight_number 的引用，使用 origin 和 destination 来查询航班
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

('flight', (SELECT id FROM flights WHERE origin = 'Beijing' AND destination = 'Shanghai' AND airline = 'Air China' LIMIT 1),
 'Air China flight operates daily between Beijing Capital International Airport (PEK) and Shanghai Pudong International Airport (PVG). The flight duration is approximately 2 hours and 15 minutes. The airline offers complimentary meals and beverages on this route. Passengers can earn frequent flyer miles on the PhoenixMiles program.',
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
-- FIXED: 所有表结构与 Java 实体类保持一致
-- FIXED: 移除了所有不存在的字段引用
-- FIXED: 添加了缺失的字段（password_hash, is_active, last_login, tags）
-- FIXED: 修复了字段命名不一致的问题（duration_minutes -> duration）
-- =============================================================================