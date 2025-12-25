import { Link } from 'react-router-dom'

const PLANS = [
  {
    id: 'eco',
    name: '经济实惠型',
    price: '¥2,800',
    description: '适合预算有限，追求性价比的旅行者。主要选择高评分民宿和公共交通。',
    highlights: ['高性价比民宿', '地道街头美食', '深度公交体验'],
    image: 'https://images.unsplash.com/photo-1518173946687-a4c8a98039f5?auto=format&fit=crop&w=800&q=80',
    color: 'bg-green-500',
  },
  {
    id: 'std',
    name: '舒适优选型',
    price: '¥5,500',
    description: '平衡预算与品质。精选四星级酒店，包含部分私家包车，行程节奏适中。',
    highlights: ['精品四星酒店', '必吃榜餐厅', '舒适包车服务'],
    image: 'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80',
    color: 'bg-primary-600',
    isPopular: true,
  },
  {
    id: 'lux',
    name: '豪华享受型',
    price: '¥12,000',
    description: '极致奢华体验。入住五星级酒店或度假村，全程私家导游，享受顶奢美食。',
    highlights: ['五星级奢华酒店', '米其林/黑珍珠餐厅', '全程VIP定制'],
    image: 'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=800&q=80',
    color: 'bg-purple-600',
  },
]

export const PlanDisplay = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">为您生成的 3 套专属方案</h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            基于您的需求，AI 智能引擎为您匹配了以下三种风格的行程。您可以对比选择最心仪的一款。
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
          {PLANS.map((plan) => (
            <div 
              key={plan.id} 
              className={`relative bg-white rounded-3xl overflow-hidden shadow-sm hover:shadow-2xl transition-all border-2 ${
                plan.isPopular ? 'border-primary-600 scale-105 z-10' : 'border-transparent'
              }`}
            >
              {plan.isPopular && (
                <div className="absolute top-0 right-0 bg-primary-600 text-white px-6 py-1 rounded-bl-2xl text-sm font-bold">
                  最受推荐
                </div>
              )}
              
              <div className="h-48 overflow-hidden">
                <img src={plan.image} alt={plan.name} className="w-full h-full object-cover" />
              </div>

              <div className="p-8">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-2xl font-bold text-gray-900">{plan.name}</h2>
                  <div className={`${plan.color} text-white px-3 py-1 rounded-lg text-sm font-bold`}>
                    {plan.id === 'eco' ? '经济' : plan.id === 'std' ? '舒适' : '豪华'}
                  </div>
                </div>

                <div className="mb-6">
                  <span className="text-sm text-gray-500">预估总价/人</span>
                  <p className={`text-4xl font-black ${plan.isPopular ? 'text-primary-600' : 'text-gray-900'}`}>{plan.price}</p>
                </div>

                <p className="text-gray-600 mb-8 line-clamp-3">
                  {plan.description}
                </p>

                <div className="space-y-3 mb-10">
                  {plan.highlights.map((h, i) => (
                    <div key={i} className="flex items-center text-sm text-gray-700">
                      <span className="text-primary-500 mr-2">✓</span>
                      {h}
                    </div>
                  ))}
                </div>

                <Link
                  to="/plan-detail"
                  className={`block text-center py-4 rounded-xl font-bold transition-all ${
                    plan.isPopular 
                      ? 'bg-primary-600 text-white hover:bg-primary-700' 
                      : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                  }`}
                >
                  查看方案详情
                </Link>
              </div>
            </div>
          ))}
        </div>

        <div className="bg-white rounded-3xl p-8 shadow-sm border border-gray-100">
          <h3 className="text-xl font-bold mb-6">方案核心对比</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="pb-4 font-bold text-gray-400">对比项</th>
                  <th className="pb-4 font-bold text-green-600">经济实惠型</th>
                  <th className="pb-4 font-bold text-primary-600">舒适优选型</th>
                  <th className="pb-4 font-bold text-purple-600">豪华享受型</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                <tr>
                  <td className="py-4 text-gray-500">住宿标准</td>
                  <td className="py-4 font-medium">民宿/快捷酒店</td>
                  <td className="py-4 font-medium">四星级/高档酒店</td>
                  <td className="py-4 font-medium">五星级/奢华品牌</td>
                </tr>
                <tr>
                  <td className="py-4 text-gray-500">交通工具</td>
                  <td className="py-4 font-medium">地铁/公交</td>
                  <td className="py-4 font-medium">拼车/部分包车</td>
                  <td className="py-4 font-medium">全程私家车接送</td>
                </tr>
                <tr>
                  <td className="py-4 text-gray-500">餐饮体验</td>
                  <td className="py-4 font-medium">当地小吃/家常菜</td>
                  <td className="py-4 font-medium">特色正餐/网红店</td>
                  <td className="py-4 font-medium">米其林/顶级私房菜</td>
                </tr>
                <tr>
                  <td className="py-4 text-gray-500">行程节奏</td>
                  <td className="py-4 font-medium">紧凑充实</td>
                  <td className="py-4 font-medium">有紧有松</td>
                  <td className="py-4 font-medium">随心所欲</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
