import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export const InfoCollection = () => {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState({
    type: 'domestic',
    destination: '',
    startDate: '',
    endDate: '',
    peopleCount: 1,
    budget: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // In a real app, we would validate and save data
    navigate('/plan-display', { state: { formData } })
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4">
        <div className="max-w-2xl mx-auto">
          {/* Progress Indicator */}
          <div className="mb-12">
            <div className="flex justify-between mb-4">
              {[1, 2, 3].map((s) => (
                <div key={s} className="flex flex-col items-center">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold transition-all ${
                    step >= s ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-500'
                  }`}>
                    {s}
                  </div>
                  <span className={`text-xs mt-2 font-medium ${step >= s ? 'text-primary-600' : 'text-gray-400'}`}>
                    {s === 1 ? '基础信息' : s === 2 ? '偏好设置' : '生成方案'}
                  </span>
                </div>
              ))}
            </div>
            <div className="relative h-2 bg-gray-200 rounded-full">
              <div 
                className="absolute h-full bg-primary-600 rounded-full transition-all duration-500"
                style={{ width: `${((step - 1) / 2) * 100}%` }}
              />
            </div>
          </div>

          <div className="bg-white rounded-3xl shadow-xl overflow-hidden">
            <div className="bg-primary-600 p-8 text-white">
              <h1 className="text-3xl font-bold mb-2">告诉我们你的计划</h1>
              <p className="text-primary-100">AI 将根据这些信息为你定制最佳旅行路线</p>
            </div>

            <form onSubmit={handleSubmit} className="p-8 space-y-6">
              {/* Type Selection */}
              <div className="grid grid-cols-2 gap-4">
                <label className={`cursor-pointer border-2 rounded-2xl p-4 transition-all ${
                  formData.type === 'domestic' ? 'border-primary-600 bg-primary-50' : 'border-gray-100 hover:border-gray-200'
                }`}>
                  <input 
                    type="radio" 
                    className="hidden" 
                    name="type" 
                    checked={formData.type === 'domestic'} 
                    onChange={() => setFormData({...formData, type: 'domestic'})}
                  />
                  <div className="text-center">
                    <span className="text-2xl mb-1 block">🇨🇳</span>
                    <span className={`font-bold ${formData.type === 'domestic' ? 'text-primary-700' : 'text-gray-600'}`}>国内游</span>
                  </div>
                </label>
                <label className={`cursor-pointer border-2 rounded-2xl p-4 transition-all ${
                  formData.type === 'international' ? 'border-primary-600 bg-primary-50' : 'border-gray-100 hover:border-gray-200'
                }`}>
                  <input 
                    type="radio" 
                    className="hidden" 
                    name="type" 
                    checked={formData.type === 'international'} 
                    onChange={() => setFormData({...formData, type: 'international'})}
                  />
                  <div className="text-center">
                    <span className="text-2xl mb-1 block">🌎</span>
                    <span className={`font-bold ${formData.type === 'international' ? 'text-primary-700' : 'text-gray-600'}`}>出境游</span>
                  </div>
                </label>
              </div>

              {/* Destination */}
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">目的地</label>
                <div className="relative">
                  <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">📍</span>
                  <input 
                    type="text" 
                    placeholder="你想去哪里？(例如：三亚、巴黎)" 
                    className="w-full pl-10 pr-4 py-4 bg-gray-50 border border-gray-100 rounded-xl focus:ring-2 focus:ring-primary-600 outline-none transition-all"
                    required
                    value={formData.destination}
                    onChange={(e) => setFormData({...formData, destination: e.target.value})}
                  />
                </div>
              </div>

              {/* Dates */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-2">出发日期</label>
                  <input 
                    type="date" 
                    className="w-full px-4 py-4 bg-gray-50 border border-gray-100 rounded-xl focus:ring-2 focus:ring-primary-600 outline-none transition-all"
                    required
                    value={formData.startDate}
                    onChange={(e) => setFormData({...formData, startDate: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-2">回程日期</label>
                  <input 
                    type="date" 
                    className="w-full px-4 py-4 bg-gray-50 border border-gray-100 rounded-xl focus:ring-2 focus:ring-primary-600 outline-none transition-all"
                    required
                    value={formData.endDate}
                    onChange={(e) => setFormData({...formData, endDate: e.target.value})}
                  />
                </div>
              </div>

              {/* People and Budget */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-2">出行人数</label>
                  <select 
                    className="w-full px-4 py-4 bg-gray-50 border border-gray-100 rounded-xl focus:ring-2 focus:ring-primary-600 outline-none transition-all appearance-none"
                    value={formData.peopleCount}
                    onChange={(e) => setFormData({...formData, peopleCount: parseInt(e.target.value)})}
                  >
                    {[1, 2, 3, 4, 5, 6].map(n => <option key={n} value={n}>{n} 人</option>)}
                    <option value="7">7人以上</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-2">人均预算</label>
                  <select 
                    className="w-full px-4 py-4 bg-gray-50 border border-gray-100 rounded-xl focus:ring-2 focus:ring-primary-600 outline-none transition-all appearance-none"
                    value={formData.budget}
                    onChange={(e) => setFormData({...formData, budget: e.target.value})}
                    required
                  >
                    <option value="">请选择预算</option>
                    <option value="eco">经济型 (¥3000以下)</option>
                    <option value="std">舒适型 (¥3000-¥8000)</option>
                    <option value="lux">豪华型 (¥8000以上)</option>
                  </select>
                </div>
              </div>

              <div className="pt-4">
                <button 
                  type="submit"
                  className="w-full py-5 bg-secondary-600 text-white text-xl font-bold rounded-2xl hover:bg-secondary-700 transition-all shadow-lg active:scale-95"
                >
                  生成我的旅行方案
                </button>
                <p className="text-center text-xs text-gray-400 mt-4 italic">
                  * 我们将使用 AI 技术分析成千上万条路线，这可能需要几秒钟时间
                </p>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}
