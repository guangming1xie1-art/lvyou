import { Link } from 'react-router-dom'

const POPULAR_DESTINATIONS = [
  { id: 1, name: '巴黎', image: 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=800&q=80', country: '法国' },
  { id: 2, name: '东京', image: 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=800&q=80', country: '日本' },
  { id: 3, name: '纽约', image: 'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&w=800&q=80', country: '美国' },
  { id: 4, name: '巴厘岛', image: 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=800&q=80', country: '印度尼西亚' },
]

const FEATURED_ITINERARIES = [
  { id: 1, title: '浪漫之都：巴黎 5 日慢生活', days: 5, price: '¥8,999', image: 'https://images.unsplash.com/photo-1499856871958-5b9627545d1a?auto=format&fit=crop&w=800&q=80' },
  { id: 2, title: '极简京都：传统与现代的碰撞', days: 4, price: '¥6,500', image: 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=800&q=80' },
  { id: 3, title: '加州阳光：西海岸自驾之旅', days: 10, price: '¥15,000', image: 'https://images.unsplash.com/photo-1501594923292-0a700149e978?auto=format&fit=crop&w=800&q=80' },
]

export const Home = () => {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative h-[80vh] flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0">
          <img
            src="https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=1920&q=80"
            alt="Hero background"
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-black/40" />
        </div>
        
        <div className="relative z-10 text-center px-4 max-w-4xl mx-auto">
          <h1 className="text-4xl md:text-7xl font-bold text-white mb-6 drop-shadow-lg">
            探索世界的无限可能
          </h1>
          <p className="text-xl md:text-2xl text-white/90 mb-10 drop-shadow-md">
            AI 驱动的智能旅行管家，为您定制专属完美行程
          </p>
          
          <div className="bg-white p-2 rounded-2xl shadow-2xl flex flex-col md:flex-row items-center gap-2 max-w-2xl mx-auto">
            <div className="flex-grow flex items-center px-4 w-full">
              <span className="text-gray-400 mr-2">📍</span>
              <input 
                type="text" 
                placeholder="你想去哪儿？" 
                className="w-full py-3 outline-none text-gray-800 text-lg"
              />
            </div>
            <Link
              to="/info-collection"
              className="w-full md:w-auto px-8 py-4 bg-secondary-600 text-white font-bold rounded-xl hover:bg-secondary-700 transition-all shadow-lg active:scale-95"
            >
              出发去哪儿
            </Link>
          </div>
          
          <div className="mt-8 flex flex-wrap justify-center gap-4">
            {['海滨度假', '城市探秘', '美食之旅', '自然风光'].map((tag) => (
              <button key={tag} className="px-4 py-1.5 bg-white/20 backdrop-blur-md border border-white/30 rounded-full text-white text-sm hover:bg-white/30 transition-all">
                {tag}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Popular Destinations */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-end mb-10">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-2">热门目的地</h2>
              <p className="text-gray-500">挑选一个你喜欢的城市，开启奇妙旅程</p>
            </div>
            <Link to="/attractions" className="text-primary-600 font-semibold hover:underline">查看全部</Link>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {POPULAR_DESTINATIONS.map((dest) => (
              <div key={dest.id} className="group relative rounded-2xl overflow-hidden aspect-[4/5] cursor-pointer shadow-lg hover:shadow-xl transition-all">
                <img src={dest.image} alt={dest.name} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent" />
                <div className="absolute bottom-6 left-6 text-white">
                  <p className="text-sm text-white/80 mb-1">{dest.country}</p>
                  <h3 className="text-2xl font-bold">{dest.name}</h3>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Itineraries */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">精选行程推荐</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              由 AI 和旅行达人共同打造，经过数千位旅行者验证的最佳路线，让你省心出发
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {FEATURED_ITINERARIES.map((item) => (
              <div key={item.id} className="bg-white rounded-3xl overflow-hidden shadow-sm hover:shadow-xl transition-all border border-gray-100 group">
                <div className="relative h-64 overflow-hidden">
                  <img src={item.image} alt={item.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                  <div className="absolute top-4 right-4 bg-white/90 backdrop-blur px-3 py-1 rounded-full text-sm font-bold text-secondary-600">
                    {item.days} 天
                  </div>
                </div>
                <div className="p-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors">{item.title}</h3>
                  <div className="flex justify-between items-center mt-6">
                    <div>
                      <span className="text-sm text-gray-500 italic">预计花费</span>
                      <p className="text-2xl font-bold text-secondary-600">{item.price}</p>
                    </div>
                    <Link
                      to="/plan-detail"
                      className="px-5 py-2.5 bg-primary-50 text-primary-600 font-bold rounded-xl hover:bg-primary-600 hover:text-white transition-all"
                    >
                      查看详情
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
      
      {/* Call to Action */}
      <section className="py-24 bg-primary-900 text-white overflow-hidden relative">
        <div className="container mx-auto px-4 relative z-10 text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">准备好开始你的下一次冒险了吗？</h2>
          <p className="text-xl text-primary-100 mb-10 max-w-2xl mx-auto">
            只需 30 秒，输入你的基本信息，AI 即刻为你规划出最省心、最地道的旅行方案。
          </p>
          <Link
            to="/info-collection"
            className="inline-block px-10 py-5 bg-secondary-500 text-white text-xl font-bold rounded-2xl hover:bg-secondary-600 transition-all shadow-2xl hover:-translate-y-1"
          >
            立即免费定制
          </Link>
        </div>
        <div className="absolute top-0 right-0 -translate-y-1/2 translate-x-1/2 w-96 h-96 bg-primary-800 rounded-full blur-3xl opacity-50" />
        <div className="absolute bottom-0 left-0 translate-y-1/2 -translate-x-1/2 w-96 h-96 bg-secondary-900 rounded-full blur-3xl opacity-30" />
      </section>
    </div>
  )
}
