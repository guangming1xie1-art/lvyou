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
SELECT 'bookings', COUNT(*) FROM bookings;

-- =============================================================================
-- 示例数据初始化完成
-- =============================================================================
-- FIXED: 所有表结构与 Java 实体类保持一致
-- FIXED: 移除了所有不存在的字段引用
-- FIXED: 添加了缺失的字段（password_hash, is_active, last_login, tags）
-- FIXED: 修复了字段命名不一致的问题（duration_minutes -> duration）
-- FIXED: 添加了bookings表及示例数据
-- =============================================================================