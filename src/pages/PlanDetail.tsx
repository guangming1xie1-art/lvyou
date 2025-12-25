import { useState } from 'react'
import { Link } from 'react-router-dom'

const DAILY_SCHEDULE = [
  {
    day: 1,
    title: '初识巴黎：塞纳河畔的浪漫',
    activities: [
      { time: '09:00', type: 'sight', name: '埃菲尔铁塔', desc: '巴黎的地标，建议提前预约登顶。', img: 'https://images.unsplash.com/photo-1511739001486-6bfe10ce785f?auto=format&fit=crop&w=400&q=80' },
      { time: '12:30', type: 'food', name: 'Le Jules Verne', desc: '位于铁塔二层的米其林餐厅。', img: 'https://images.unsplash.com/photo-1550966841-396ad886016a?auto=format&fit=crop&w=400&q=80' },
      { time: '15:00', type: 'sight', name: '塞纳河游船', desc: '乘船欣赏两岸风景。', img: 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=400&q=80' },
    ],
    hotel: { name: 'Pullman Paris Tour Eiffel', star: 4 }
  },
  {
    day: 2,
    title: '艺术殿堂：卢浮宫与蒙马特',
    activities: [
      { time: '10:00', type: 'sight', name: '卢浮宫', desc: '世界四大博物馆之首。', img: 'https://images.unsplash.com/photo-1499856871958-5b9627545d1a?auto=format&fit=crop&w=400&q=80' },
      { time: '14:00', type: 'sight', name: '杜乐丽花园', desc: '法式园林的典范。', img: 'https://images.unsplash.com/photo-1559110314-5211d0ef4c2c?auto=format&fit=crop&w=400&q=80' },
    ],
    hotel: { name: 'Pullman Paris Tour Eiffel', star: 4 }
  }
]

const COST_BREAKDOWN = [
  { category: '交通', cost: '¥4,500', detail: '往返机票 + 当地包车' },
  { category: '住宿', cost: '¥3,200', detail: '4晚精品酒店' },
  { category: '餐饮', cost: '¥1,800', detail: '包含一顿米其林简餐' },
  { category: '门票', cost: '¥800', detail: '主要景点通票' },
]

export const PlanDetail = () => {
  const [activeDay, setActiveDay] = useState(1)

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Banner */}
      <div className="relative h-96 overflow-hidden">
        <img 
          src="https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=1920&q=80" 
          alt="Paris" 
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-black/30" />
        <div className="absolute bottom-12 left-0 w-full">
          <div className="container mx-auto px-4">
            <div className="flex flex-wrap items-end justify-between gap-6">
              <div className="text-white">
                <nav className="flex mb-4 text-sm text-white/80">
                  <Link to="/" className="hover:text-white">首页</Link>
                  <span className="mx-2">/</span>
                  <Link to="/plan-display" className="hover:text-white">方案选择</Link>
                  <span className="mx-2">/</span>
                  <span>方案详情</span>
                </nav>
                <h1 className="text-4xl md:text-5xl font-bold mb-2">巴黎 5 日浪漫艺术之旅</h1>
                <div className="flex items-center gap-4">
                  <span className="bg-secondary-500 px-3 py-1 rounded-lg font-bold text-sm">舒适优选型</span>
                  <span className="text-lg">预计总价：¥5,500/人</span>
                </div>
              </div>
              <div className="flex gap-4">
                <button className="px-6 py-3 bg-white/20 backdrop-blur-md text-white border border-white/30 rounded-xl font-bold hover:bg-white/30 transition-all">
                  修改行程
                </button>
                <Link to="/order-confirm" className="px-8 py-3 bg-secondary-600 text-white rounded-xl font-bold hover:bg-secondary-700 transition-all shadow-lg">
                  立即预订
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 mt-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Day Selector */}
            <div className="flex gap-2 overflow-x-auto pb-2">
              {DAILY_SCHEDULE.map((d) => (
                <button
                  key={d.day}
                  onClick={() => setActiveDay(d.day)}
                  className={`flex-shrink-0 px-6 py-3 rounded-2xl font-bold transition-all ${
                    activeDay === d.day 
                      ? 'bg-primary-600 text-white shadow-lg' 
                      : 'bg-white text-gray-500 hover:bg-gray-100'
                  }`}
                >
                  Day {d.day}
                </button>
              ))}
              <button className="flex-shrink-0 px-6 py-3 bg-white text-gray-400 rounded-2xl font-bold border-2 border-dashed border-gray-200">
                + 添加天数
              </button>
            </div>

            {/* Daily Details */}
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900">
                {DAILY_SCHEDULE.find(d => d.day === activeDay)?.title}
              </h2>
              
              <div className="space-y-8 relative before:absolute before:left-[19px] before:top-4 before:bottom-4 before:w-0.5 before:bg-gray-200">
                {DAILY_SCHEDULE.find(d => d.day === activeDay)?.activities.map((act, i) => (
                  <div key={i} className="relative pl-12">
                    <div className={`absolute left-0 top-1 w-10 h-10 rounded-full flex items-center justify-center z-10 ${
                      act.type === 'sight' ? 'bg-blue-100 text-blue-600' : 'bg-orange-100 text-orange-600'
                    }`}>
                      {act.type === 'sight' ? '🏛️' : '🍴'}
                    </div>
                    <div className="bg-white rounded-3xl p-6 shadow-sm border border-gray-100 flex flex-col md:flex-row gap-6">
                      <div className="w-full md:w-48 h-32 flex-shrink-0 rounded-2xl overflow-hidden">
                        <img src={act.img} alt={act.name} className="w-full h-full object-cover" />
                      </div>
                      <div className="flex-grow">
                        <div className="flex justify-between items-start mb-2">
                          <span className="text-sm font-bold text-primary-600">{act.time}</span>
                          <button className="text-gray-400 hover:text-primary-600 text-sm">更换项目</button>
                        </div>
                        <h3 className="text-xl font-bold text-gray-900 mb-2">{act.name}</h3>
                        <p className="text-gray-500 text-sm">{act.desc}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Hotel Card */}
              <div className="bg-primary-50 rounded-3xl p-6 border border-primary-100 mt-12">
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-2xl">🏨</span>
                  <h3 className="text-lg font-bold text-primary-900">当日住宿推荐</h3>
                </div>
                <div className="bg-white rounded-2xl p-4 flex justify-between items-center shadow-sm">
                  <div>
                    <p className="font-bold text-gray-900">{DAILY_SCHEDULE.find(d => d.day === activeDay)?.hotel.name}</p>
                    <div className="text-yellow-400 text-sm">
                      {'★'.repeat(DAILY_SCHEDULE.find(d => d.day === activeDay)?.hotel.star || 0)}
                    </div>
                  </div>
                  <button className="text-primary-600 font-bold text-sm">查看预订详情</button>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-8">
            <div className="bg-white rounded-3xl p-8 shadow-sm border border-gray-100">
              <h3 className="text-xl font-bold text-gray-900 mb-6">费用预算明细</h3>
              <div className="space-y-4 mb-8">
                {COST_BREAKDOWN.map((c, i) => (
                  <div key={i} className="flex justify-between items-start">
                    <div>
                      <p className="font-bold text-gray-900">{c.category}</p>
                      <p className="text-xs text-gray-500">{c.detail}</p>
                    </div>
                    <span className="font-bold text-gray-900">{c.cost}</span>
                  </div>
                ))}
              </div>
              <div className="pt-6 border-t border-gray-100 flex justify-between items-center">
                <span className="text-lg font-bold">总计预估</span>
                <span className="text-3xl font-black text-secondary-600">¥10,300</span>
              </div>
              <p className="text-xs text-gray-400 mt-4 text-center italic">* 以上费用为双人参考总价</p>
            </div>

            <div className="bg-primary-900 rounded-3xl p-8 text-white shadow-xl relative overflow-hidden">
              <h3 className="text-xl font-bold mb-4 relative z-10">不满意这个方案？</h3>
              <p className="text-primary-200 mb-6 relative z-10 text-sm">
                您可以告诉 AI 您的具体修改需求，例如 "我想要更轻便的行程" 或 "多加一点美食探店"。
              </p>
              <textarea 
                placeholder="在此输入您的修改要求..." 
                className="w-full h-24 bg-primary-800 border-none rounded-2xl p-4 text-sm text-white placeholder-primary-400 focus:ring-2 focus:ring-secondary-500 outline-none mb-4 relative z-10"
              />
              <button className="w-full py-4 bg-secondary-500 text-white font-bold rounded-xl hover:bg-secondary-600 transition-all relative z-10">
                重新生成方案
              </button>
              <div className="absolute -bottom-10 -right-10 w-32 h-32 bg-primary-700 rounded-full blur-3xl" />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
