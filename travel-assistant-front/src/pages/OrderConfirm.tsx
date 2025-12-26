import { Link } from 'react-router-dom'

export const OrderConfirm = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8 flex items-center justify-between">
            <h1 className="text-3xl font-bold text-gray-900">确认您的行程</h1>
            <Link to="/plan-detail" className="text-primary-600 font-bold hover:underline">返回修改</Link>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-6">
              {/* Trip Summary */}
              <div className="bg-white rounded-3xl p-8 shadow-sm border border-gray-100">
                <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                  <span className="text-2xl">📋</span> 行程概览
                </h2>
                <div className="space-y-6">
                  <div className="flex gap-6">
                    <img 
                      src="https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=400&q=80" 
                      className="w-24 h-24 rounded-2xl object-cover" 
                      alt="Paris"
                    />
                    <div>
                      <h3 className="text-lg font-bold text-gray-900">巴黎 5 日浪漫艺术之旅</h3>
                      <p className="text-gray-500 text-sm mt-1">2024年5月20日 - 2024年5月24日</p>
                      <div className="flex gap-4 mt-2">
                        <span className="text-xs bg-gray-100 px-2 py-1 rounded-md text-gray-600">2 人出行</span>
                        <span className="text-xs bg-gray-100 px-2 py-1 rounded-md text-gray-600">舒适优选型</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="border-t border-gray-50 pt-6">
                    <h4 className="font-bold text-sm text-gray-400 uppercase tracking-wider mb-4">包含项</h4>
                    <ul className="grid grid-cols-2 gap-y-3">
                      {['4晚精品酒店住宿', '往返含税机票', '卢浮宫/铁塔门票', '全程包车服务', '行程规划与AI助手服务', '赠送当地电话卡'].map((item, i) => (
                        <li key={i} className="flex items-center text-sm text-gray-700">
                          <span className="text-green-500 mr-2 text-xs">●</span>
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>

              {/* Passenger Info */}
              <div className="bg-white rounded-3xl p-8 shadow-sm border border-gray-100">
                <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                  <span className="text-2xl">👤</span> 出行人信息
                </h2>
                <div className="space-y-4">
                  <div className="p-4 bg-gray-50 rounded-2xl flex justify-between items-center border border-gray-100">
                    <div>
                      <p className="font-bold">张三</p>
                      <p className="text-sm text-gray-500">身份证: 1101**********1234</p>
                    </div>
                    <button className="text-primary-600 text-sm font-bold">编辑</button>
                  </div>
                  <button className="w-full py-4 border-2 border-dashed border-gray-200 rounded-2xl text-gray-400 font-bold hover:bg-gray-50 transition-all">
                    + 添加出行人
                  </button>
                </div>
              </div>
            </div>

            {/* Price Sidebar */}
            <div className="space-y-6">
              <div className="bg-white rounded-3xl p-8 shadow-sm border border-gray-100">
                <h2 className="text-xl font-bold mb-6">费用总计</h2>
                <div className="space-y-4 mb-8">
                  <div className="flex justify-between text-gray-600">
                    <span>成人 x2</span>
                    <span>¥10,600</span>
                  </div>
                  <div className="flex justify-between text-gray-600 text-sm">
                    <span>行程定制费 (AI)</span>
                    <span className="text-green-600 font-bold">免费</span>
                  </div>
                  <div className="flex justify-between text-gray-600 text-sm">
                    <span>平台优惠券</span>
                    <span className="text-secondary-600">- ¥300</span>
                  </div>
                </div>
                <div className="pt-6 border-t border-gray-100 flex justify-between items-center mb-8">
                  <span className="text-lg font-bold">应付金额</span>
                  <span className="text-3xl font-black text-secondary-600">¥10,300</span>
                </div>
                
                <div className="space-y-4">
                  <label className="flex gap-3 cursor-pointer group">
                    <input type="checkbox" className="mt-1 rounded border-gray-300 text-primary-600 focus:ring-primary-600" />
                    <span className="text-xs text-gray-500 group-hover:text-gray-700 transition-colors">
                      我已阅读并同意 <a href="#" className="text-primary-600 underline">《旅游助手预订协议》</a> 和 <a href="#" className="text-primary-600 underline">《个人信息保护政策》</a>
                    </span>
                  </label>
                  
                  <button className="w-full py-5 bg-secondary-600 text-white text-xl font-bold rounded-2xl hover:bg-secondary-700 transition-all shadow-lg active:scale-95">
                    立即预订
                  </button>
                </div>
              </div>
              
              <div className="text-center">
                <p className="text-sm text-gray-400 mb-2">如有疑问，请拨打客服电话</p>
                <p className="font-bold text-gray-600">400-123-4567</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
