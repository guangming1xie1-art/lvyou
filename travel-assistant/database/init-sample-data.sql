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

INSERT INTO hotels (name, destination, price, rating, description, facilities, check_in_date, check_out_date) VALUES ('上海广场大酒店', '上海', 680.00, 4.5,'位于上海市中心的豪华五星级酒店，享有壮丽的城市景观和世界级设施。','["无线网络", "游泳池", "健身房", "水疗中心", "餐厅", "客房服务", "商务中心", "礼宾服务"]','2025-02-15', '2025-02-20');

INSERT INTO hotels (name, destination, price, rating, description, facilities, check_in_date, check_out_date) VALUES ('北京皇家宫殿酒店', '北京', 1200.00, 4.8,'毗邻故宫的历史豪华酒店，提供传统中式待客之道与现代舒适体验。', '["无线网络", "游泳池", "水疗中心", "多家餐厅", "茶室", "文化之旅", "机场班车"]','2025-03-01', '2025-03-08');

INSERT INTO hotels (name, destination, price, rating, description, facilities, check_in_date, check_out_date) VALUES ('深圳湾度假村', '深圳', 450.00, 4.2,'现代化商务酒店，享有海湾全景，是休闲和商务旅客的理想之选。','["无线网络", "健身房", "商务中心", "会议室", "海景", "精致餐饮"]','2025-02-28', '2025-03-05');

INSERT INTO hotels (name, destination, price, rating, description, facilities, check_in_date, check_out_date) VALUES ('广州明珠塔酒店', '广州', 320.00, 4.0,'位于商业区的现代酒店，交通便利，靠近购物和娱乐场所。','["无线网络", "健身房", "餐厅", "酒吧", "洗衣服务", "24小时前台"]','2025-03-10', '2025-03-15');

INSERT INTO hotels (name, destination, price, rating, description, facilities, check_in_date, check_out_date) VALUES ('成都茶园客栈', '成都', 180.00, 4.6,'迷人的精品酒店，采用传统川式设计，设有美丽的茶园庭院。','["无线网络", "传统庭院", "茶艺服务", "文化活动", "本地餐厅"]','2025-02-25', '2025-02-27');

INSERT INTO hotels (name, destination, price, rating, description, facilities, check_in_date, check_out_date) VALUES ('杭州西湖别墅', '杭州', 890.00, 4.7, '优雅的湖畔酒店，可饱览西湖美景，融合传统建筑与豪华设施。','["无线网络", "湖景", "水疗中心", "传统园林", "精致餐饮", "游船", "文化项目"]','2025-04-01', '2025-04-03');

INSERT INTO hotels (name, destination, price, rating, description, facilities, check_in_date, check_out_date) VALUES ('西安古城酒店', '西安', 280.00, 4.3,'位于古城墙内的历史酒店，提供正宗的唐代文化体验。','["无线网络", "文化表演", "传统建筑", "本地美食", "历史游览"]','2025-03-15', '2025-03-20');

INSERT INTO hotels (name, destination, price, rating, description, facilities, check_in_date, check_out_date) VALUES ('苏州古典园林酒店', '苏州', 520.00, 4.4,'豪华酒店，采用经典苏州园林设计，靠近著名的留园。','["无线网络", "传统园林", "水疗中心", "文化工坊", "精致餐饮", "私人园林"]','2025-04-10', '2025-04-15');

-- =============================================================================
-- 3. 示例航班数据 (flights)
-- FIXED: 移除 departure_time, arrival_time, flight_number, available_seats 字段
-- FIXED: 将 duration_minutes 改为 duration 以匹配 Flight.java 实体
-- =============================================================================

INSERT INTO flights (flight_no, origin, destination, departure_date, return_date, price, airline, duration) VALUES
('MU6002', '北京', '上海', '2026-03-30', '2025-02-20', 580.00, 'Air China', 135),

('MU6002', '上海', '北京', '2026-03-30', '2025-02-20', 620.00, 'China Eastern', 135),

('ES8811', '北京', '深圳', '2026-03-30', '2025-03-08', 1280.00, 'Air China', 195),

('ES8812', '上海', '广州', '2026-03-30', '2025-03-05', 890.00, 'China Southern', 155),

('ES8813', '北京', '成都', '2026-03-30', NULL, 980.00, 'Air China', 195),

('ES8814', '上海', '杭州', '2026-03-30', '2025-02-27', 280.00, 'Spring Airlines', 60),

('ES8815', '北京', '西安', '2026-03-30', '2025-03-20', 750.00, 'Hainan Airlines', 135),

('ES8816', '上海', '苏州', '2026-03-30', '2025-04-03', 180.00, 'Juneyao Airlines', 45),

('MU7002', '北京', '上海', '2026-03-30', '2025-04-15', 680.00, 'Air China', 135),

('MU7002', '上海', '北京', '2026-03-30', '2025-04-15', 720.00, 'China Eastern', 135),

('MU2777', '大连', '北京', '2026-03-30', '2025-03-30', 720.00, 'China Eastern', 135),

('MU2777', '北京', '大连', '2026-03-30', '2025-03-30', 720.00, 'China Eastern', 135);


-- =============================================================================
-- 4. 示例景点数据 (attractions)
-- FIXED: 移除 ticket_price, latitude, longitude, phone, website 字段
-- FIXED: 添加 tags 字段（核心字段，用于搜索和推荐）
-- =============================================================================
INSERT INTO attractions (destination, name, category, rating, description, opening_hours, tags) VALUES
('上海', '外滩', '历史', 4.6,
 '标志性的滨江长廊，展示上海的殖民建筑和现代天际线。',
 '00:00-24:00', '["历史", "地标", "滨江", "摄影", "建筑"]'),

('上海', '豫园', '历史', 4.4,
 '传统中式园林，拥有古典建筑、亭台楼阁和传统商铺。',
 '08:30-17:00', '["历史", "园林", "文化", "传统", "建筑"]'),

('上海', '上海迪士尼度假区', '娱乐', 4.7,
 '神奇的王国，拥有迪士尼角色、刺激游乐设施和精彩演出。',
 '08:00-22:00', '["娱乐", "家庭", "主题公园", "儿童", "冒险"]'),

('上海', '法租界', '历史', 4.5,
 '历史街区，拥有林荫街道、欧式建筑和时尚店铺。',
 '00:00-24:00', '["历史", "建筑", "漫步", "购物", "文化"]'),

('北京', '故宫', '历史', 4.8,
 '皇家宫殿建筑群，展示600年的中国历史与建筑艺术。',
 '08:30-17:00', '["历史", "宫殿", "文化", "世界遗产", "地标", "建筑"]'),

('北京', '长城（八达岭）', '历史', 4.5,
 '长城最受欢迎的路段，提供壮观的山景。',
 '07:30-18:00', '["历史", "地标", "徒步", "世界遗产", "冒险", "山景"]'),

('北京', '颐和园', '历史', 4.6,
 '皇家园林，拥有湖泊、宫殿和传统中式园林景观。',
 '06:30-18:00', '["历史", "园林", "湖泊", "文化", "休闲", "自然"]'),

('北京', '天坛', '历史', 4.3,
 '神圣的建筑群，皇帝曾在此祈求丰收，拥有令人惊叹的建筑。',
 '06:00-22:00', '["历史", "文化", "宗教", "建筑", "寺庙"]'),

('深圳', '锦绣中华民俗村', '历史', 4.2,
 '微缩公园，展示中国的民族多样性和历史地标。',
 '09:00-21:30', '["历史", "文化", "家庭", "娱乐", "民俗"]'),

('深圳', '世界之窗', '娱乐', 4.1,
 '主题公园，展示世界著名地标和文化景点的复制品。',
 '09:00-22:00', '["娱乐", "家庭", "主题公园", "国际", "地标"]'),

('广州', '广州塔', '历史', 4.0,
 '标志性的604米高电视塔，提供全景城市视野和娱乐设施。',
 '09:00-22:30', '["地标", "现代", "城市景观", "娱乐", "建筑"]'),

('广州', '长隆野生动物世界', '娱乐', 4.4,
 '大型野生动物园，拥有多样化的野生动物和精彩的动物表演。',
 '09:30-17:30', '["野生动物", "家庭", "动物", "自然", "冒险"]'),

('成都', '大熊猫繁育研究基地', '历史', 4.8,
 '世界著名的大熊猫保护中心，游客可以在此观赏大熊猫。',
 '07:30-18:00', '["野生动物", "动物", "自然", "家庭", "文化", "保护"]'),

('成都', '锦里古街', '美食', 4.3,
 '历史悠久的街道，两旁是传统的川菜餐厅和文化商店。',
 '00:00-24:00', '["美食", "历史", "文化", "夜生活", "传统", "购物"]'),

('杭州', '西湖', '历史', 4.9,
 '联合国教科文组织世界遗产，拥有美丽的湖泊、园林和历史宝塔。',
 '00:00-24:00', '["自然", "湖泊", "风景", "世界遗产", "休闲", "园林"]'),

('杭州', '灵隐寺', '历史', 4.5,
 '古老的佛教寺庙建筑群，拥有令人印象深刻的石刻和宁静的园林。',
 '07:00-18:15', '["历史", "文化", "宗教", "寺庙", "自然", "建筑"]'),

('西安', '兵马俑', '历史', 4.7,
 '古代军事博物馆，拥有数千个真人大小的陶制士兵。',
 '08:30-18:00', '["历史", "考古", "文化", "世界遗产", "博物馆", "古代"]'),

('西安', '西安城墙', '历史', 4.2,
 '完整的明代城墙，提供骑行和城市景观观赏。',
 '08:00-22:00', '["历史", "地标", "建筑", "骑行", "城市景观", "古代"]'),

('苏州', '留园', '历史', 4.6,
 '古典中式园林，被联合国教科文组织认定为世界遗产。',
 '07:30-17:30', '["历史", "园林", "世界遗产", "文化", "建筑", "景观"]'),

('苏州', '拙政园', '历史', 4.5,
 '苏州最大的古典园林，展示传统中式园林设计。',
 '07:30-17:30', '["历史", "园林", "世界遗产", "文化", "建筑", "景观"]');

===========================
INSERT INTO attractions (destination, name, category, rating, description, opening_hours, tags) VALUES
('上海', '外滩', '历史', 4.6,
 '标志性的滨江长廊，展示上海的殖民建筑和现代天际线。',
 '00:00-24:00', ARRAY['历史', '地标', '滨江', '摄影', '建筑']),

('上海', '豫园', '历史', 4.4,
 '传统中式园林，拥有古典建筑、亭台楼阁和传统商铺。',
 '08:30-17:00', ARRAY['历史', '园林', '文化', '传统', '建筑']),

('上海', '上海迪士尼度假区', '娱乐', 4.7,
 '神奇的王国，拥有迪士尼角色、刺激游乐设施和精彩演出。',
 '08:00-22:00', ARRAY['娱乐', '家庭', '主题公园', '儿童', '冒险']),

('上海', '法租界', '历史', 4.5,
 '历史街区，拥有林荫街道、欧式建筑和时尚店铺。',
 '00:00-24:00', ARRAY['历史', '建筑', '漫步', '购物', '文化']),

('北京', '故宫', '历史', 4.8,
 '皇家宫殿建筑群，展示600年的中国历史与建筑艺术。',
 '08:30-17:00', ARRAY['历史', '宫殿', '文化', '世界遗产', '地标', '建筑']),

('北京', '长城（八达岭）', '历史', 4.5,
 '长城最受欢迎的路段，提供壮观的山景。',
 '07:30-18:00', ARRAY['历史', '地标', '徒步', '世界遗产', '冒险', '山景']),

('北京', '颐和园', '历史', 4.6,
 '皇家园林，拥有湖泊、宫殿和传统中式园林景观。',
 '06:30-18:00', ARRAY['历史', '园林', '湖泊', '文化', '休闲', '自然']),

('北京', '天坛', '历史', 4.3,
 '神圣的建筑群，皇帝曾在此祈求丰收，拥有令人惊叹的建筑。',
 '06:00-22:00', ARRAY['历史', '文化', '宗教', '建筑', '寺庙']),

('深圳', '锦绣中华民俗村', '历史', 4.2,
 '微缩公园，展示中国的民族多样性和历史地标。',
 '09:00-21:30', ARRAY['历史', '文化', '家庭', '娱乐', '民俗']),

('深圳', '世界之窗', '娱乐', 4.1,
 '主题公园，展示世界著名地标和文化景点的复制品。',
 '09:00-22:00', ARRAY['娱乐', '家庭', '主题公园', '国际', '地标']),

('广州', '广州塔', '历史', 4.0,
 '标志性的604米高电视塔，提供全景城市视野和娱乐设施。',
 '09:00-22:30', ARRAY['地标', '现代', '城市景观', '娱乐', '建筑']),

('广州', '长隆野生动物世界', '娱乐', 4.4,
 '大型野生动物园，拥有多样化的野生动物和精彩的动物表演。',
 '09:30-17:30', ARRAY['野生动物', '家庭', '动物', '自然', '冒险']),

('成都', '大熊猫繁育研究基地', '历史', 4.8,
 '世界著名的大熊猫保护中心，游客可以在此观赏大熊猫。',
 '07:30-18:00', ARRAY['野生动物', '动物', '自然', '家庭', '文化', '保护']),

('成都', '锦里古街', '美食', 4.3,
 '历史悠久的街道，两旁是传统的川菜餐厅和文化商店。',
 '00:00-24:00', ARRAY['美食', '历史', '文化', '夜生活', '传统', '购物']),

('杭州', '西湖', '历史', 4.9,
 '联合国教科文组织世界遗产，拥有美丽的湖泊、园林和历史宝塔。',
 '00:00-24:00', ARRAY['自然', '湖泊', '风景', '世界遗产', '休闲', '园林']),

('杭州', '灵隐寺', '历史', 4.5,
 '古老的佛教寺庙建筑群，拥有令人印象深刻的石刻和宁静的园林。',
 '07:00-18:15', ARRAY['历史', '文化', '宗教', '寺庙', '自然', '建筑']),

('西安', '兵马俑', '历史', 4.7,
 '古代军事博物馆，拥有数千个真人大小的陶制士兵。',
 '08:30-18:00', ARRAY['历史', '考古', '文化', '世界遗产', '博物馆', '古代']),

('西安', '西安城墙', '历史', 4.2,
 '完整的明代城墙，提供骑行和城市景观观赏。',
 '08:00-22:00', ARRAY['历史', '地标', '建筑', '骑行', '城市景观', '古代']),

('苏州', '留园', '历史', 4.6,
 '古典中式园林，被联合国教科文组织认定为世界遗产。',
 '07:30-17:30', ARRAY['历史', '园林', '世界遗产', '文化', '建筑', '景观']),

('苏州', '拙政园', '历史', 4.5,
 '苏州最大的古典园林，展示传统中式园林设计。',
 '07:30-17:30', ARRAY['历史', '园林', '世界遗产', '文化', '建筑', '景观']);
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

-- =============================================================================
-- 6. 示例审计日志数据 (audit_logs)
-- =============================================================================
INSERT INTO audit_logs (user_id, action, endpoint, method, status_code, ip_address, user_agent)
VALUES(
(SELECT id FROM users WHERE username = 'john_doe' LIMIT 1),
    'search',
    '/api/v1/hotels/search',
    'GET',
    200,
    '192.168.1.100',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    ),
(
  (SELECT id FROM users WHERE username = 'jane_smith' LIMIT 1),
  'book',
  '/api/v1/hotels/book',
  'POST',
  201,
  '192.168.1.101',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
),
(
  (SELECT id FROM users WHERE username = 'mike_wilson' LIMIT 1),
  'search',
  '/api/v1/flights/search',
  'GET',
  200,
  '192.168.1.102',
  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
),
(
  (SELECT id FROM users WHERE username = 'sarah_j' LIMIT 1),
  'recommend',
  '/api/v1/attractions/recommend',
  'GET',
  200,
  '192.168.1.103',
  'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15'
),
(
  (SELECT id FROM users WHERE username = 'david_b' LIMIT 1),
  'search',
  '/api/v1/attractions/search',
  'GET',
  200,
  '192.168.1.104',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
);
-- =============================================================================
-- 7. 示例预订数据 (bookings)
-- =============================================================================
INSERT INTO bookings (
  user_id,
  booking_type,
  resource_id,
  booking_date,
  status,
  total_price,
  notes,
  created_by,
  updated_by
) VALUES
-- PENDING状态的酒店预订
(
  (SELECT id FROM users WHERE username = 'john_doe' LIMIT 1),
  'HOTEL',
  (SELECT id FROM hotels WHERE name = 'The Grand Plaza Hotel' LIMIT 1),
  '2025-01-25 10:30:00',
  'PENDING',
  3400.00,
  'Need a room with city view, preferably on higher floors',
  (SELECT id FROM users WHERE username = 'john_doe' LIMIT 1),
  (SELECT id FROM users WHERE username = 'john_doe' LIMIT 1)
),

-- CONFIRMED状态的航班预订
(
  (SELECT id FROM users WHERE username = 'jane_smith' LIMIT 1),
  'FLIGHT',
  (SELECT id FROM flights WHERE origin = 'Beijing' AND destination = 'Shanghai' AND airline = 'Air China' LIMIT 1),
  '2025-01-20 14:15:00',
  'CONFIRMED',
  1240.00,
  'Business class, window seat preferred',
  (SELECT id FROM users WHERE username = 'jane_smith' LIMIT 1),
  (SELECT id FROM users WHERE username = 'jane_smith' LIMIT 1)
),

-- CONFIRMED状态的景点预订
(
  (SELECT id FROM users WHERE username = 'mike_wilson' LIMIT 1),
  'ATTRACTION',
  (SELECT id FROM attractions WHERE name = 'Giant Panda Breeding Research Base' LIMIT 1),
  '2025-01-22 09:45:00',
  'CONFIRMED',
  180.00,
  'Family of 4, need guide service',
  (SELECT id FROM users WHERE username = 'mike_wilson' LIMIT 1),
  (SELECT id FROM users WHERE username = 'mike_wilson' LIMIT 1)
),

-- PENDING状态的酒店预订
(
  (SELECT id FROM users WHERE username = 'sarah_j' LIMIT 1),
  'HOTEL',
  (SELECT id FROM hotels WHERE name = 'Beijing Royal Palace' LIMIT 1),
  '2025-01-26 16:20:00',
  'PENDING',
  9600.00,
  'Executive suite, need airport pickup',
  (SELECT id FROM users WHERE username = 'sarah_j' LIMIT 1),
  (SELECT id FROM users WHERE username = 'sarah_j' LIMIT 1)
),

-- CANCELLED状态的航班预订
(
  (SELECT id FROM users WHERE username = 'david_b' LIMIT 1),
  'FLIGHT',
  (SELECT id FROM flights WHERE origin = 'Shanghai' AND destination = 'Hangzhou' AND airline = 'Spring Airlines' LIMIT 1),
  '2025-01-18 11:30:00',
  'CANCELLED',
  280.00,
  'Cancelled due to schedule conflict',
  (SELECT id FROM users WHERE username = 'david_b' LIMIT 1),
  (SELECT id FROM users WHERE username = 'david_b' LIMIT 1)
),

-- CONFIRMED状态的酒店预订
(
  (SELECT id FROM users WHERE username = 'john_doe' LIMIT 1),
  'HOTEL',
  (SELECT id FROM hotels WHERE name = 'Chengdu Tea Garden Inn' LIMIT 1),
  '2025-01-19 13:50:00',
  'CONFIRMED',
  360.00,
  'Traditional room with courtyard view',
  (SELECT id FROM users WHERE username = 'john_doe' LIMIT 1),
  (SELECT id FROM users WHERE username = 'john_doe' LIMIT 1)
),

-- PENDING状态的景点预订
(
  (SELECT id FROM users WHERE username = 'jane_smith' LIMIT 1),
  'ATTRACTION',
  (SELECT id FROM attractions WHERE name = 'Forbidden City' LIMIT 1),
  '2025-01-27 08:00:00',
  'PENDING',
  120.00,
  'Private tour for 2 people, English-speaking guide required',
  (SELECT id FROM users WHERE username = 'jane_smith' LIMIT 1),
  (SELECT id FROM users WHERE username = 'jane_smith' LIMIT 1)
),

-- CONFIRMED状态的航班预订
(
  (SELECT id FROM users WHERE username = 'mike_wilson' LIMIT 1),
  'FLIGHT',
  (SELECT id FROM flights WHERE origin = 'Beijing' AND destination = 'Shenzhen' AND airline = 'Air China' LIMIT 1),
  '2025-01-21 15:40:00',
  'CONFIRMED',
  5120.00,
  'Group booking for 4 people, need seats together',
  (SELECT id FROM users WHERE username = 'mike_wilson' LIMIT 1),
  (SELECT id FROM users WHERE username = 'mike_wilson' LIMIT 1)
);

-- =============================================================================
-- 9. 示例记忆系统数据（从 schema_memory.sql 整合）
-- 用途：为四层记忆系统提供示例数据
-- =============================================================================

-- =============================================================================
-- 9.1 对话会话数据 (conversations)
-- =============================================================================
INSERT INTO conversations (user_id, session_id, title, status, summary, metadata) VALUES
-- 用户1的会话
((SELECT id FROM users WHERE username = 'john_doe' LIMIT 1), 'session_1', '三亚旅游规划', 'active', '用户计划去三亚旅游，需要酒店和景点推荐', '{"travel_destination": "三亚", "travel_days": 5, "budget": "5000-8000"}'),
((SELECT id FROM users WHERE username = 'john_doe' LIMIT 1), 'session_2', '北京周末游', 'archived', '用户计划北京周末游，需要故宫和长城的攻略', '{"travel_destination": "北京", "travel_days": 2, "budget": "2000-3000"}'),

-- 用户2的会话
((SELECT id FROM users WHERE username = 'jane_smith' LIMIT 1), 'session_3', '上海商务旅行', 'active', '用户需要上海商务旅行的酒店和交通推荐', '{"travel_destination": "上海", "travel_purpose": "business", "budget": "10000+"}'),

-- 用户3的会话
((SELECT id FROM users WHERE username = 'mike_wilson' LIMIT 1), 'session_4', '成都美食之旅', 'active', '用户计划成都美食之旅，需要餐厅推荐', '{"travel_destination": "成都", "travel_purpose": "food", "budget": "3000-5000"}'),

-- 用户4的会话
((SELECT id FROM users WHERE username = 'sarah_j' LIMIT 1), 'session_5', '杭州西湖游', 'archived', '用户计划杭州西湖一日游，需要景点和交通信息', '{"travel_destination": "杭州", "travel_days": 1, "budget": "1000-2000"}');

-- =============================================================================
-- 9.2 对话消息数据 (conversation_messages)
-- =============================================================================
INSERT INTO conversation_messages (conversation_id, user_id, role, content, message_type, metadata) VALUES
-- 会话1的消息
((SELECT id FROM conversations WHERE session_id = 'session_1' LIMIT 1), (SELECT id FROM users WHERE username = 'john_doe' LIMIT 1), 'user', '我计划下个月去三亚旅游，想了解一下酒店和景点推荐', 'text', '{"message_id": "msg_1"}'),
((SELECT id FROM conversations WHERE session_id = 'session_1' LIMIT 1), (SELECT id FROM users WHERE username = 'john_doe' LIMIT 1), 'assistant', '三亚是一个非常适合度假的地方！推荐您考虑以下酒店：\n1. 三亚亚特兰蒂斯酒店 - 豪华水世界主题酒店\n2. 三亚海棠湾红树林度假酒店 - 海边豪华酒店\n3. 三亚亚龙湾铂尔曼度假酒店 - 性价比高\n\n推荐景点：\n1. 亚龙湾 - 著名的白沙滩\n2. 蜈支洲岛 - 潜水胜地\n3. 天涯海角 - 标志性景点\n4. 南山文化旅游区 - 佛教文化胜地', 'text', '{"message_id": "msg_2", "token_count": 150}'),

-- 会话2的消息
((SELECT id FROM conversations WHERE session_id = 'session_2' LIMIT 1), (SELECT id FROM users WHERE username = 'john_doe' LIMIT 1), 'user', '我周末想去北京玩，故宫和长城怎么安排比较好？', 'text', '{"message_id": "msg_3"}'),
((SELECT id FROM conversations WHERE session_id = 'session_2' LIMIT 1), (SELECT id FROM users WHERE username = 'john_doe' LIMIT 1), 'assistant', '周末游北京的建议安排：\n\n**第一天：故宫**\n- 建议早上8:30入场，避开人流\n- 参观路线：午门 → 太和殿 → 乾清宫 → 御花园\n- 预计游览时间：4-5小时\n- 午餐推荐：故宫附近的王府井大街\n\n**第二天：长城**\n- 推荐八达岭长城，交通最便利\n- 早上7点出发，可乘坐S2线火车\n- 预计游览时间：3-4小时\n- 下午返回市区，可顺路参观明十三陵', 'text', '{"message_id": "msg_4", "token_count": 200}'),

-- 会话3的消息
((SELECT id FROM conversations WHERE session_id = 'session_3' LIMIT 1), (SELECT id FROM users WHERE username = 'jane_smith' LIMIT 1), 'user', '我需要去上海出差3天，推荐一下市中心的商务酒店', 'text', '{"message_id": "msg_5"}'),
((SELECT id FROM conversations WHERE session_id = 'session_3' LIMIT 1), (SELECT id FROM users WHERE username = 'jane_smith' LIMIT 1), 'assistant', '上海市中心的商务酒店推荐：\n\n1. 上海浦东香格里拉大酒店 - 位于陆家嘴金融区，交通便利\n2. 上海静安香格里拉大酒店 - 位于静安区，购物方便\n3. 上海外滩华尔道夫酒店 - 位于外滩，景观优美\n4. 上海凯悦酒店 - 位于人民广场附近，地理位置优越\n\n这些酒店都提供商务中心、高速网络和会议设施，非常适合商务出行。', 'text', '{"message_id": "msg_6", "token_count": 120}');

-- =============================================================================
-- 9.3 用户偏好数据 (user_preferences)
-- =============================================================================
INSERT INTO user_preferences (user_id, preference_type, preference_value, confidence, source, metadata) VALUES
-- 用户1的偏好
((SELECT id FROM users WHERE username = 'john_doe' LIMIT 1), 'travel_style', 'cultural', 0.8, 'explicit', '{"last_confirmed": "2025-01-15"}'),
((SELECT id FROM users WHERE username = 'john_doe' LIMIT 1), 'budget_range', 'mid', 0.9, 'explicit', '{"last_confirmed": "2025-01-15"}'),
((SELECT id FROM users WHERE username = 'john_doe' LIMIT 1), 'destination_type', 'beach', 0.7, 'implicit', '{"inferred_count": 3}'),

-- 用户2的偏好
((SELECT id FROM users WHERE username = 'jane_smith' LIMIT 1), 'travel_style', 'luxury', 0.9, 'explicit', '{"last_confirmed": "2025-01-18"}'),
((SELECT id FROM users WHERE username = 'jane_smith' LIMIT 1), 'accommodation_type', '5_star_hotel', 0.85, 'explicit', '{"last_confirmed": "2025-01-18"}'),

-- 用户3的偏好
((SELECT id FROM users WHERE username = 'mike_wilson' LIMIT 1), 'travel_style', 'adventure', 0.8, 'explicit', '{"last_confirmed": "2025-01-20"}'),
((SELECT id FROM users WHERE username = 'mike_wilson' LIMIT 1), 'budget_range', 'budget', 0.9, 'explicit', '{"last_confirmed": "2025-01-20"}'),
((SELECT id FROM users WHERE username = 'mike_wilson' LIMIT 1), 'food_preference', 'local_cuisine', 0.95, 'explicit', '{"last_confirmed": "2025-01-20"}'),

-- 用户4的偏好
((SELECT id FROM users WHERE username = 'sarah_j' LIMIT 1), 'travel_style', 'cultural', 0.75, 'implicit', '{"inferred_count": 2}'),
((SELECT id FROM users WHERE username = 'sarah_j' LIMIT 1), 'budget_range', 'luxury', 0.8, 'explicit', '{"last_confirmed": "2025-01-10"}'),

-- 用户5的偏好
((SELECT id FROM users WHERE username = 'david_b' LIMIT 1), 'travel_style', 'adventure', 0.85, 'explicit', '{"last_confirmed": "2025-01-12"}'),
((SELECT id FROM users WHERE username = 'david_b' LIMIT 1), 'activity_type', 'hiking', 0.9, 'explicit', '{"last_confirmed": "2025-01-12"}');

-- =============================================================================
-- 9.4 历史任务案例数据 (task_cases)
-- =============================================================================
INSERT INTO task_cases (user_id, destination, duration_days, budget_range, preferences, plan_summary, satisfaction, feedback) VALUES
-- 用户1的任务案例
((SELECT id FROM users WHERE username = 'john_doe' LIMIT 1), '三亚', 5, '5000-8000', '["海边", "美食", "休闲"]', '5天4晚三亚之旅，入住亚特兰蒂斯酒店，游览亚龙湾、蜈支洲岛和天涯海角，品尝当地海鲜美食', 4.8, '非常满意，酒店设施一流，景点推荐很到位'),

-- 用户2的任务案例
((SELECT id FROM users WHERE username = 'jane_smith' LIMIT 1), '上海', 3, '10000+', '["商务", "购物", "美食"]', '3天2晚上海商务之行，入住浦东香格里拉大酒店，参加商务会议，空余时间购物和品尝美食', 4.5, '酒店位置很好，交通便利，服务周到'),

-- 用户3的任务案例
((SELECT id FROM users WHERE username = 'mike_wilson' LIMIT 1), '成都', 4, '3000-5000', '["美食", "文化", "熊猫"]', '4天3晚成都美食之旅，入住锦里附近酒店，品尝川菜，参观大熊猫基地，游览武侯祠', 4.9, '美食推荐非常棒，熊猫基地的体验难忘'),

-- 用户4的任务案例
((SELECT id FROM users WHERE username = 'sarah_j' LIMIT 1), '杭州', 2, '2000-3000', '["风景", "文化", "休闲"]', '2天1晚杭州之旅，入住西湖附近酒店，游览西湖、灵隐寺，品尝西湖醋鱼', 4.6, '西湖景色很美，酒店位置绝佳'),

-- 用户5的任务案例
((SELECT id FROM users WHERE username = 'david_b' LIMIT 1), '西安', 3, '4000-6000', '["历史", "文化", "美食"]', '3天2晚西安之旅，入住古城墙附近酒店，参观兵马俑、古城墙，品尝肉夹馍和凉皮', 4.7, '历史文化体验丰富，美食令人难忘');

-- =============================================================================
-- 9.5 向量存储元数据 (vector_memories)
-- =============================================================================
INSERT INTO vector_memories (user_id, memory_type, content, embedding_id, metadata) VALUES
-- 用户1的向量记忆
((SELECT id FROM users WHERE username = 'john_doe' LIMIT 1), 'preference', '用户喜欢海滩度假，预算中等，偏好文化体验', 'emb_1', '{"destination_type": "beach", "budget_level": "mid", "travel_style": "cultural"}'),
((SELECT id FROM users WHERE username = 'john_doe' LIMIT 1), 'task_case', '三亚5天4晚度假，入住亚特兰蒂斯酒店，游览亚龙湾、蜈支洲岛', 'emb_2', '{"destination": "三亚", "duration": 5, "satisfaction": 4.8}'),

-- 用户2的向量记忆
((SELECT id FROM users WHERE username = 'jane_smith' LIMIT 1), 'preference', '用户偏好豪华旅行，喜欢五星级酒店，商务出行频繁', 'emb_3', '{"budget_level": "luxury", "accommodation_type": "5_star", "travel_purpose": "business"}'),

-- 用户3的向量记忆
((SELECT id FROM users WHERE username = 'mike_wilson' LIMIT 1), 'preference', '用户喜欢冒险旅行，预算有限，对当地美食有浓厚兴趣', 'emb_4', '{"travel_style": "adventure", "budget_level": "budget", "food_preference": "local"}'),

-- 用户4的向量记忆
((SELECT id FROM users WHERE username = 'sarah_j' LIMIT 1), 'task_case', '杭州2天1晚休闲游，游览西湖和灵隐寺，入住西湖附近酒店', 'emb_5', '{"destination": "杭州", "duration": 2, "satisfaction": 4.6}'),

-- 用户5的向量记忆
((SELECT id FROM users WHERE username = 'david_b' LIMIT 1), 'preference', '用户喜欢徒步旅行，对历史文化景点有兴趣，偏好冒险活动', 'emb_6', '{"activity_type": "hiking", "travel_style": "adventure", "interest": "history"}');

-- =============================================================================
-- 8. 示例查询 - 验证数据完整性
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
SELECT 'audit_logs', COUNT(*) FROM audit_logs
UNION ALL
SELECT 'bookings', COUNT(*) FROM bookings
UNION ALL
-- 记忆系统表
SELECT 'conversations', COUNT(*) FROM conversations
UNION ALL
SELECT 'conversation_messages', COUNT(*) FROM conversation_messages
UNION ALL
SELECT 'user_preferences', COUNT(*) FROM user_preferences
UNION ALL
SELECT 'task_cases', COUNT(*) FROM task_cases
UNION ALL
SELECT 'vector_memories', COUNT(*) FROM vector_memories
UNION ALL
-- 管理系统表
SELECT 'admin_users', COUNT(*) FROM admin_users
UNION ALL
SELECT 'roles', COUNT(*) FROM roles
UNION ALL
SELECT 'permissions', COUNT(*) FROM permissions
UNION ALL
SELECT 'admin_user_roles', COUNT(*) FROM admin_user_roles
UNION ALL
SELECT 'role_permissions', COUNT(*) FROM role_permissions
UNION ALL
SELECT 'prompts', COUNT(*) FROM prompts;

-- =============================================================================
-- 9. 示例管理员数据 (admin_users, roles, permissions)
-- 用途：为后台管理系统提供初始管理员、角色和权限数据
-- 对应实体类：admin-service/src/main/java/com/travelassistant/admin/entity/
-- =============================================================================

-- 9.1 示例管理员用户数据
INSERT INTO admin_users (username, email, password_hash, real_name, phone, avatar, is_active, last_login) VALUES
('admin', 'admin@travelassistant.com', '$2a$10$rOzK4Z8kB7mV5jA.xxXxAu', '系统管理员', '13800138000', 'https://api.dicebear.com/7.x/avataaars/svg?seed=admin', TRUE, CURRENT_TIMESTAMP),
('editor', 'editor@travelassistant.com', '$2a$10$rOzK4Z8kB7mV5jA.xxXxAu', '内容编辑', '13800138001', 'https://api.dicebear.com/7.x/avataaars/svg?seed=editor', TRUE, NULL),
('viewer', 'viewer@travelassistant.com', '$2a$10$rOzK4Z8kB7mV5jA.xxXxAu', '查看员', '13800138002', 'https://api.dicebear.com/7.x/avataaars/svg?seed=viewer', TRUE, NULL);

-- 9.2 示例角色数据
INSERT INTO roles (name, code, description, is_active) VALUES
('超级管理员', 'SUPER_ADMIN', '拥有所有权限，可以管理所有功能', TRUE),
('内容管理员', 'CONTENT_ADMIN', '可以管理景点、酒店、航班等内容', TRUE),
('查看员', 'VIEWER', '只能查看数据，不能修改', TRUE);

-- 9.3 示例权限数据
INSERT INTO permissions (name, code, type, parent_id, path, icon, sort_order, is_active) VALUES
-- 一级菜单
('系统管理', 'SYSTEM', 'MENU', NULL, '/system', 'SettingOutlined', 100, TRUE),
('用户管理', 'USER', 'MENU', NULL, '/user', 'UserOutlined', 200, TRUE),
('内容管理', 'CONTENT', 'MENU', NULL, '/content', 'AppstoreOutlined', 300, TRUE),
('提示词管理', 'PROMPT', 'MENU', NULL, '/prompt', 'MessageOutlined', 400, TRUE),

-- 系统管理子菜单
('管理员列表', 'ADMIN_USER_LIST', 'MENU', 
 (SELECT id FROM permissions WHERE code = 'SYSTEM'), '/system/admin', 'TeamOutlined', 10, TRUE),
('角色管理', 'ROLE_MANAGE', 'MENU', 
 (SELECT id FROM permissions WHERE code = 'SYSTEM'), '/system/role', 'SafetyCertificateOutlined', 20, TRUE),
('权限管理', 'PERMISSION_MANAGE', 'MENU', 
 (SELECT id FROM permissions WHERE code = 'SYSTEM'), '/system/permission', 'KeyOutlined', 30, TRUE),

-- 用户管理子菜单
('用户列表', 'USER_LIST', 'MENU', 
 (SELECT id FROM permissions WHERE code = 'USER'), '/user/list', 'UsergroupAddOutlined', 10, TRUE),
('用户偏好', 'USER_PREFERENCE', 'MENU', 
 (SELECT id FROM permissions WHERE code = 'USER'), '/user/preference', 'HeartOutlined', 20, TRUE),
('历史记录', 'USER_HISTORY', 'MENU', 
 (SELECT id FROM permissions WHERE code = 'USER'), '/user/history', 'HistoryOutlined', 30, TRUE),

-- 内容管理子菜单
('景点管理', 'ATTRACTION_MANAGE', 'MENU', 
 (SELECT id FROM permissions WHERE code = 'CONTENT'), '/content/attraction', 'EnvironmentOutlined', 10, TRUE),
('酒店管理', 'HOTEL_MANAGE', 'MENU', 
 (SELECT id FROM permissions WHERE code = 'CONTENT'), '/content/hotel', 'HomeOutlined', 20, TRUE),
('航班管理', 'FLIGHT_MANAGE', 'MENU', 
 (SELECT id FROM permissions WHERE code = 'CONTENT'), '/content/flight', 'SendOutlined', 30, TRUE),
('RAG文档', 'RAG_DOCUMENT', 'MENU', 
 (SELECT id FROM permissions WHERE code = 'CONTENT'), '/content/rag', 'FileTextOutlined', 40, TRUE),

-- 提示词管理子菜单
('提示词列表', 'PROMPT_LIST', 'MENU', 
 (SELECT id FROM permissions WHERE code = 'PROMPT'), '/prompt/list', 'UnorderedListOutlined', 10, TRUE),
('提示词编辑', 'PROMPT_EDIT', 'MENU', 
 (SELECT id FROM permissions WHERE code = 'PROMPT'), '/prompt/edit', 'EditOutlined', 20, TRUE),

-- 按钮权限
('添加管理员', 'ADMIN_USER_ADD', 'BUTTON', 
 (SELECT id FROM permissions WHERE code = 'ADMIN_USER_LIST'), NULL, NULL, 1, TRUE),
('编辑管理员', 'ADMIN_USER_EDIT', 'BUTTON', 
 (SELECT id FROM permissions WHERE code = 'ADMIN_USER_LIST'), NULL, NULL, 2, TRUE),
('删除管理员', 'ADMIN_USER_DELETE', 'BUTTON', 
 (SELECT id FROM permissions WHERE code = 'ADMIN_USER_LIST'), NULL, NULL, 3, TRUE),
('添加角色', 'ROLE_ADD', 'BUTTON', 
 (SELECT id FROM permissions WHERE code = 'ROLE_MANAGE'), NULL, NULL, 1, TRUE),
('编辑角色', 'ROLE_EDIT', 'BUTTON', 
 (SELECT id FROM permissions WHERE code = 'ROLE_MANAGE'), NULL, NULL, 2, TRUE),
('删除角色', 'ROLE_DELETE', 'BUTTON', 
 (SELECT id FROM permissions WHERE code = 'ROLE_MANAGE'), NULL, NULL, 3, TRUE),
('添加权限', 'PERMISSION_ADD', 'BUTTON', 
 (SELECT id FROM permissions WHERE code = 'PERMISSION_MANAGE'), NULL, NULL, 1, TRUE),
('编辑权限', 'PERMISSION_EDIT', 'BUTTON', 
 (SELECT id FROM permissions WHERE code = 'PERMISSION_MANAGE'), NULL, NULL, 2, TRUE),
('删除权限', 'PERMISSION_DELETE', 'BUTTON', 
 (SELECT id FROM permissions WHERE code = 'PERMISSION_MANAGE'), NULL, NULL, 3, TRUE),
('添加景点', 'ATTRACTION_ADD', 'BUTTON', 
 (SELECT id FROM permissions WHERE code = 'ATTRACTION_MANAGE'), NULL, NULL, 1, TRUE),
('编辑景点', 'ATTRACTION_EDIT', 'BUTTON', 
 (SELECT id FROM permissions WHERE code = 'ATTRACTION_MANAGE'), NULL, NULL, 2, TRUE),
('删除景点', 'ATTRACTION_DELETE', 'BUTTON', 
 (SELECT id FROM permissions WHERE code = 'ATTRACTION_MANAGE'), NULL, NULL, 3, TRUE),
('添加酒店', 'HOTEL_ADD', 'BUTTON', 
 (SELECT id FROM permissions WHERE code = 'HOTEL_MANAGE'), NULL, NULL, 1, TRUE),
('编辑酒店', 'HOTEL_EDIT', 'BUTTON', 
 (SELECT id FROM permissions WHERE code = 'HOTEL_MANAGE'), NULL, NULL, 2, TRUE),
('删除酒店', 'HOTEL_DELETE', 'BUTTON', 
 (SELECT id FROM permissions WHERE code = 'HOTEL_MANAGE'), NULL, NULL, 3, TRUE),
('添加航班', 'FLIGHT_ADD', 'BUTTON', 
 (SELECT id FROM permissions WHERE code = 'FLIGHT_MANAGE'), NULL, NULL, 1, TRUE),
('编辑航班', 'FLIGHT_EDIT', 'BUTTON', 
 (SELECT id FROM permissions WHERE code = 'FLIGHT_MANAGE'), NULL, NULL, 2, TRUE),
('删除航班', 'FLIGHT_DELETE', 'BUTTON', 
 (SELECT id FROM permissions WHERE code = 'FLIGHT_MANAGE'), NULL, NULL, 3, TRUE),
('添加提示词', 'PROMPT_ADD', 'BUTTON', 
 (SELECT id FROM permissions WHERE code = 'PROMPT_LIST'), NULL, NULL, 1, TRUE),
('编辑提示词', 'PROMPT_EDIT_BTN', 'BUTTON', 
 (SELECT id FROM permissions WHERE code = 'PROMPT_LIST'), NULL, NULL, 2, TRUE),
('删除提示词', 'PROMPT_DELETE', 'BUTTON', 
 (SELECT id FROM permissions WHERE code = 'PROMPT_LIST'), NULL, NULL, 3, TRUE),
('刷新提示词', 'PROMPT_REFRESH', 'BUTTON', 
 (SELECT id FROM permissions WHERE code = 'PROMPT_LIST'), NULL, NULL, 4, TRUE);

-- 9.4 管理员用户角色关联数据
INSERT INTO admin_user_roles (user_id, role_id) VALUES
-- admin 用户拥有超级管理员角色
((SELECT id FROM admin_users WHERE username = 'admin' LIMIT 1), 
 (SELECT id FROM roles WHERE code = 'SUPER_ADMIN' LIMIT 1)),
-- editor 用户拥有内容管理员角色
((SELECT id FROM admin_users WHERE username = 'editor' LIMIT 1), 
 (SELECT id FROM roles WHERE code = 'CONTENT_ADMIN' LIMIT 1)),
-- viewer 用户拥有查看员角色
((SELECT id FROM admin_users WHERE username = 'viewer' LIMIT 1), 
 (SELECT id FROM roles WHERE code = 'VIEWER' LIMIT 1));

-- 9.5 角色权限关联数据
INSERT INTO role_permissions (role_id, permission_id) 
-- 超级管理员拥有所有权限
SELECT 
  (SELECT id FROM roles WHERE code = 'SUPER_ADMIN' LIMIT 1),
  id
FROM permissions;

-- 内容管理员拥有内容管理相关权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT 
  (SELECT id FROM roles WHERE code = 'CONTENT_ADMIN' LIMIT 1),
  id
FROM permissions
WHERE code IN (
  'ATTRACTION_MANAGE', 'HOTEL_MANAGE', 'FLIGHT_MANAGE', 'RAG_DOCUMENT',
  'ATTRACTION_ADD', 'ATTRACTION_EDIT', 'ATTRACTION_DELETE',
  'HOTEL_ADD', 'HOTEL_EDIT', 'HOTEL_DELETE',
  'FLIGHT_ADD', 'FLIGHT_EDIT', 'FLIGHT_DELETE',
  'PROMPT_LIST', 'PROMPT_EDIT', 'PROMPT_ADD', 'PROMPT_EDIT_BTN', 'PROMPT_DELETE', 'PROMPT_REFRESH'
);

-- 查看员只有查看权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT 
  (SELECT id FROM roles WHERE code = 'VIEWER' LIMIT 1),
  id
FROM permissions
WHERE code IN (
  'USER', 'USER_LIST', 'USER_PREFERENCE', 'USER_HISTORY',
  'CONTENT', 'ATTRACTION_MANAGE', 'HOTEL_MANAGE', 'FLIGHT_MANAGE', 'RAG_DOCUMENT',
  'PROMPT', 'PROMPT_LIST', 'PROMPT_EDIT'
);

-- =============================================================================
-- 10. 示例提示词数据 (prompts)
-- 用途：为提示词管理系统提供初始数据
-- 说明：这些提示词用于各个 AI Agent，支持热更新
-- 对应实体类：admin-service/src/main/java/com/travelassistant/admin/entity/Prompt.java
-- =============================================================================

-- 10.1 信息收集 Agent 提示词
INSERT INTO prompts (name, category, content, variables, description, version, is_active) VALUES
('collect_system_prompt', 'collect', 
'你是信息收集员，负责与用户交互收集旅游需求。

你的核心任务：
1. 分析用户的旅游需求
2. 识别关键信息：目的地、时间、预算、偏好等
3. ⚠️ 【重要】严格验证信息的合法性和完整性：
- 日期必须合法（检查月份天数、日期格式等）
- 检查月份范围: 1-12月
- 检查日期范围：根据月份的实际天数(如2月最多29天)
- 关键信息（目的地、日期）不能缺失
4. 如果信息有问题或不足，生成友好的澄清提问

🔴 【critical】complete 字段的含义（这个字段直接影响后续工作流）：
- complete = true: ✅ 所有关键信息都有效且完整，工作流将进入搜索阶段
- complete = false: ❌ 发现信息错误或不足，工作流停止，用户需要澄清

【重点】如果发现任何信息错误（日期无效、信息缺失等），你必须：
1. 设置 complete = false
2. 在回复中清楚地指出问题
3. 提供修正建议和追问

之前的对话历史：
{{history_text}}

返回格式（必须是有效的 JSON):
{
    "destination": "目的地（如北京）",
    "duration": "天数（整数或描述）",
    "budget": "预算范围(如5000-10000元)",
    "preferences": ["偏好1", "偏好2"],
    "dates": "出发时间(YYYY-MM-DD格式或描述)",
    "complete": true or false,
    "message": "你对用户的回复（澄清问题或确认信息）"
}

注意:message 字段将单独存储用于对话展示，不会传递给下游搜索和推荐流程。

【规则 1】设置 complete=true 的条件：
✅ 目的地明确
✅ 日期有效且合法（特别注意月份天数）
✅ 出行时长清晰
✅ 足以进行搜索

【规则 2】设置 complete=false 的条件：
❌ 日期错误(如2月30号、13月等)
❌ 日期格式不清楚或模糊
❌ 缺少关键信息（目的地、日期）
❌ 信息逻辑矛盾
❌ 其他需要用户确认的问题

【示例 1】完整输入 - complete=true:
用户输入:我现在在大连,2026年2月28号出发,想去北京玩3天
返回：
{
    "origin":"大连",
    "destination": "北京",
    "duration": "3天",
    "budget": "4000-6000元",
    "preferences": ["喜欢博物馆"],
    "dates": "2026-02-28",
    "complete": true,
    "message": "客户计划在2026年2月28日从大连出发去北京,游玩3天,预算在4000-6000元内,偏好是喜欢博物馆,请为客户搜索合适的酒店、航班和景点推荐。"
}

【示例 2】错误输入 - complete=false:
用户输入:我现在在大连,2026年2月30号,想去北京玩3天
返回：
{
    "origin":"大连",
    "destination": "北京",
    "duration": "3天",
    "budget": "未指定",
    "preferences": ["无偏好"],
    "dates": "2026-02-30(❌ 无效)",
    "complete": false,
    "message": "我注意到您提供的信息中有一个小问题需要澄清。2026年2月30日这个日期是不存在的,因为2月份最多只有29天(闰年)。\n\n请问您是想在以下哪个日期出发呢?\n- 2026年2月29日\n- 2026年3月1日\n- 或其他时间？"
}

说明：以上返回中的 message 字段将被提取并单独存储为 collection_message,用于对话展示;其他字段作为 collected_info 传递给下游流程。',
'{"history_text": "对话历史"}', '信息收集Agent的系统提示词', '1.0.0', TRUE),

-- 10.2 搜索规划 Agent 提示词
('search_plan_system_prompt', 'search_plan',
'你是旅游搜索战略专家。你的工作不仅是重复用户信息，而是：

1. 深度理解用户的真实需求
   - 识别用户的核心诉求和隐含偏好
   - 判断时间与预算的限制条件
2. 识别信息缺口
   - 标注缺失的关键字段以及影响
   - 需要时提出澄清问题
3. 制定清晰的搜索战略
   - 分阶段搜索策略
   - 优先级配置
   - RAG关键词优化
4. 指导执行阶段
   - 输出可直接用于执行阶段的搜索指导

## 输出格式（必须是有效的 JSON)
{
    "user_intent_analysis": {
        "core_needs": "核心需求描述",
        "user_interpretation": {
            "possible_focus": ["可能类型1", "可能类型2"],
            "time_pressure": "时间紧张度判断",
            "budget_flexibility": "预算弹性判断"
        },
        "potential_concerns": ["潜在问题1", "潜在问题2"]
    },
    "search_strategy": {
        "phase1_hot_spots": {
            "priority": "高/中/低",
            "focus": "阶段目标",
            "keywords": ["关键词1", "关键词2"]
        },
        "phase2_special_interests": {
            "priority": "高/中/低",
            "focus": "阶段目标",
            "keywords": ["关键词1", "关键词2"]
        },
        "phase3_accommodation": {
            "priority": "高/中/低",
            "focus": "阶段目标",
            "recommendations": "住宿策略"
        },
        "phase4_logistics": {
            "priority": "高/中/低",
            "focus": "阶段目标",
            "recommendations": "交通策略"
        }
    },
    "clarification_questions": ["问题1", "问题2"],
    "information_gaps": {
        "budget": "缺口说明",
        "travel_style": "缺口说明"
    },
    "search_configuration": {
        "priorities": {"attractions": 0.5, "hotels": 0.3, "flights": 0.2},
        "rag_search_keywords": ["关键词1", "关键词2"],
        "hotel_strategy": "住宿策略",
        "flight_strategy": "交通策略"
    },
    "search_plan": {
        "origin": "出发地",
        "destination": "目的地",
        "check_in": "入住日期",
        "check_out": "退房日期",
        "duration_days": 天数,
        "budget_range": "预算范围",
        "preferences": ["偏好1", "偏好2"]
    },
    "output": "搜索战略说明"
}',
'{}', '搜索规划Agent的系统提示词', '1.0.0', TRUE),

('search_plan_user_query', 'search_plan',
'请根据以下已收集的用户信息，生成搜索战略：

## 用户信息
- 出发地：{origin}
- 目的地：{destination}
- 出发日：{dates}
- 周期：{duration}
- 预算：{budget}
- 偏好：{preferences}

## 原始消息
{user_content}

返回 JSON 格式的搜索战略。',
'{"origin": "出发地", "destination": "目的地", "dates": "出发日", "duration": "周期", "budget": "预算", "preferences": "偏好", "user_content": "原始消息"}', '搜索规划Agent的用户查询模板', '1.0.0', TRUE),

-- 10.3 搜索执行 Agent 提示词
('search_execute_system_prompt', 'search_execute',
'你是旅游搜索执行专家，负责根据搜索策略使用工具获取旅游信息。

## 执行策略
1. 必须按顺序执行以下三个步骤，每个步骤都要实际调用对应工具：
   - 步骤1: 调用工具获取景点信息 (search_attractions)
   - 步骤2: 调用工具获取酒店信息 (search_hotels)
   - 步骤3: 调用工具获取交通信息 (search_flights)
2. 每个步骤完成后，在中间结果中确认该步骤已完成
3. 最终汇总所有结果

## 搜索策略
- 阶段1(热门景点): {search_strategy_phase1}
- 阶段2(特殊兴趣): {search_strategy_phase2}
- 阶段3(住宿): {search_strategy_phase3}
- 阶段4(交通): {search_strategy_phase4}

## 参数信息
- 目的地: {destination}
- 出发地: {origin}
- 入住日期: {check_in}
- 退房日期: {check_out}
- 预算范围: {budget_range}

## 工具使用策略
- 必须调用search_attractions获取景点数据
- 必须调用search_hotels获取住宿数据
- 必须调用search_flights获取交通数据
- 可选使用RAG工具获取背景信息

## 输出格式(JSON)
{
    "output": "综合搜索结果文本描述",
    "search_results": {
        "destinations": [],
        "hotels": [],
        "flights": [],
        "attractions": [],
        "rag_sources_used": [],
        "tools_used": []
    }
}',
'{"search_strategy_phase1": "阶段1", "search_strategy_phase2": "阶段2", "search_strategy_phase3": "阶段3", "search_strategy_phase4": "阶段4", "destination": "目的地", "origin": "出发地", "check_in": "入住日期", "check_out": "退房日期", "budget_range": "预算范围"}', '搜索执行Agent的系统提示词', '1.0.0', TRUE),

('search_execute_user_query', 'search_execute',
'请按执行策略完成搜索任务：

## 用户信息
- 目的地：{destination}
- 出发日：{dates}
- 周期：{duration}
- 预算：{budget}
- 偏好：{preferences}

## 用户原始请求
{user_content}

请严格按照执行策略调用所有必需工具并汇总结果。',
'{"destination": "目的地", "dates": "出发日", "duration": "周期", "budget": "预算", "preferences": "偏好", "user_content": "原始消息"}', '搜索执行Agent的用户查询模板', '1.0.0', TRUE),

-- 10.4 推荐规划 Agent 提示词
('recommend_plan_system_prompt', 'recommend_plan',
'你是旅游推荐规划专家。你的工作不是简单复述搜索结果，而是：

## 职责
1. 分析用户需求与搜索结果，洞察用户偏好与行程节奏
2. 制定推荐框架：构建多方案策略，明确不同方案定位与满意度预期
3. 识别信息缺口，提出澄清问题
4. 为推荐执行阶段提供可操作的指导

## 输出格式(JSON)
{
    "user_profile_analysis": {
        "trip_characteristics": {
            "duration": "行程时长",
            "destination_type": "目的地类型",
            "travel_pace": "行程节奏",
            "interest_focus": "兴趣焦点"
        },
        "recommendation_considerations": ["考虑点1", "考虑点2"]
    },
    "recommendation_framework": {
        "plan_1": {
            "name": "方案名称",
            "target": "目标人群",
            "focus": ["景点1", "景点2"],
            "characteristics": "方案特点",
            "estimated_satisfaction": 0.8
        }
    },
    "information_gaps": {
        "missing_inputs": ["缺失信息1"],
        "impact": "缺失影响"
    },
    "clarification_questions": ["问题1", "问题2"],
    "recommend_plan": {
        "themes": ["主题1", "主题2"],
        "num_plans": 3,
        "focus_points": ["侧重点1", "侧重点2"],
        "weights": {"budget": 0.3, "experience": 0.4, "convenience": 0.3}
    },
    "output": "推荐计划描述"
}',
'{}', '推荐规划Agent的系统提示词', '1.0.0', TRUE),

('recommend_plan_user_query', 'recommend_plan',
'请制定推荐策略：

## 用户信息
- 目的地：{destination}
- 出发日：{dates}
- 周期：{duration}
- 预算：{budget}
- 偏好：{preferences}

## 搜索结果摘要
{search_results}

## 用户原始请求
{user_content}

返回 JSON 格式的推荐策略。',
'{"destination": "目的地", "dates": "出发日", "duration": "周期", "budget": "预算", "preferences": "偏好", "search_results": "搜索结果", "user_content": "原始消息"}', '推荐规划Agent的用户查询模板', '1.0.0', TRUE),

-- 10.5 推荐执行 Agent 提示词
('recommend_execute_system_prompt', 'recommend_execute',
'你是专业的旅游推荐专家，负责根据用户信息和搜索结果生成个性化的旅游推荐方案。

## 职责
1. 综合分析用户需求、偏好、预算和搜索结果
2. 生成具体、实用、个性化的旅游行程方案
3. 包含每日行程安排、推荐住宿、交通建议、预算分配和亮点介绍
4. 确保推荐内容与用户偏好高度匹配
5. 提供多个不同风格的方案供用户选择

## 输出格式(JSON)
{
    "recommendations": {
        "summary": "整体推荐概述",
        "plans": [
            {
                "id": "plan_1",
                "title": "方案标题",
                "subtitle": "副标题，如''适合家庭出游''或''文艺青年首选''",
                "theme": "方案主题",
                "duration": "行程天数",
                "itinerary": [
                    {
                        "day": 1,
                        "date": "具体日期（如果有）",
                        "title": "第X天行程标题",
                        "activities": [
                            {
                                "time": "时间段",
                                "location": "地点名称",
                                "description": "活动描述",
                                "reason": "推荐理由",
                                "estimated_duration": "预计时长",
                                "tips": "实用建议"
                            }
                        ],
                        "accommodation": {
                            "name": "酒店名称",
                            "rating": "评分",
                            "location": "位置",
                            "price_range": "价格区间",
                            "features": ["特色1", "特色2"],
                            "reason": "推荐理由"
                        },
                        "transportation": {
                            "from_to": "交通路线",
                            "mode": "交通方式",
                            "cost": "费用",
                            "duration": "耗时"
                        },
                        "meals": [
                            {
                                "meal_type": "餐别（早餐/午餐/晚餐）",
                                "name": "餐厅/美食名称",
                                "type": "菜系/类型",
                                "cost": "预估费用",
                                "reason": "推荐理由"
                            }
                        ]
                    }
                ],
                "budget_breakdown": {
                    "total_budget": "总预算",
                    "accommodation": "住宿费用",
                    "transportation": "交通费用",
                    "meals": "餐饮费用",
                    "attractions": "景点门票费用",
                    "shopping_other": "购物及其他费用"
                },
                "highlights": ["亮点1", "亮点2", "亮点3"],
                "travel_tips": ["贴士1", "贴士2"],
                "best_for": ["适合人群"]
            }
        ]
    }
}',
'{}', '推荐执行Agent的系统提示词', '1.0.0', TRUE),

('recommend_execute_user_query', 'recommend_execute',
'请生成个性化旅游推荐方案：

## 用户信息
- 目的地：{destination}
- 出发地：{origin}
- 出发日：{dates}
- 周期：{duration}
- 预算：{budget}
- 偏好：{preferences}
- 人数：{group_size}
- 特殊需求：{special_requests}

## 推荐策略分析
- 用户画像：{user_profile}
- 方案框架：{framework}
- 信息缺口：{gaps}

## 推荐计划
- 主题：{themes}
- 方案数量：{num_plans}
- 侧重点：{focus_points}
- 权重：{weights}

## 搜索结果详情
景点信息：
{attractions}

酒店信息：
{hotels}

交通信息：
{flights}

其他信息：
{other_info}

## 用户原始请求
{user_content}

请根据以上所有信息，生成详细、实用、个性化的旅游推荐方案。',
'{"destination": "目的地", "origin": "出发地", "dates": "出发日", "duration": "周期", "budget": "预算", "preferences": "偏好", "group_size": "人数", "special_requests": "特殊需求", "user_profile": "用户画像", "framework": "方案框架", "gaps": "信息缺口", "themes": "主题", "num_plans": "方案数量", "focus_points": "侧重点", "weights": "权重", "attractions": "景点信息", "hotels": "酒店信息", "flights": "交通信息", "other_info": "其他信息", "user_content": "原始消息"}', '推荐执行Agent的用户查询模板', '1.0.0', TRUE),

-- 10.6 预订 Agent 提示词
('booking_system_prompt', 'booking',
'你是预订员，负责完成用户选定的旅游预订。

你的任务：
1. 确认用户选择的推荐方案
2. 使用 create_booking 工具创建预订
3. 返回预订确认信息

推荐方案：
{{recommendations}}

可用工具：
{{tools_text}}

返回格式（JSON）：
{
    "booking_id": "预订ID",
    "status": "confirmed/pending",
    "details": {...},
    "confirmation_message": "确认信息"
}',
'{"recommendations": "推荐方案", "tools_text": "可用工具"}', '预订Agent的系统提示词', '1.0.0', TRUE),

-- 10.7 核心记忆提示词
('core_memory', 'memory',
'{
    "role": "你是一个专业的旅游规划助手",
    "core_tasks": [
        "帮助用户规划行程",
        "搜索景点酒店",
        "提供推荐"
    ],
    "tool_guidelines": {
        "search_flights": "用于搜索航班信息",
        "search_hotels": "用于搜索酒店信息",
        "recommend_destinations": "用于推荐旅游目的地"
    },
    "prohibitions": [
        "不要推荐超出预算的方案",
        "不要编造虚假信息"
    ]
}',
'{}', '核心记忆配置', '1.0.0', TRUE);

-- =============================================================================
-- 示例数据初始化完成
-- =============================================================================
-- FIXED: 所有表结构与 Java 实体类保持一致
-- FIXED: 移除了所有不存在的字段引用
-- FIXED: 添加了缺失的字段（password_hash, is_active, last_login, tags）
-- FIXED: 修复了字段命名不一致的问题（duration_minutes -> duration）
-- FIXED: 添加了bookings表及示例数据
-- FIXED: 添加了prompts表及提示词初始化数据
-- FIXED: 添加了admin_users, roles, permissions, admin_user_roles, role_permissions表及初始化数据
-- FIXED: 完善了权限系统，包括菜单、按钮权限
-- FIXED: 添加了三个示例管理员用户和角色权限关联
-- =============================================================================