const ATTRACTIONS = [
  { id: 1, name: '埃菲尔铁塔', type: '景点', rating: 4.9, transport: '地铁 6/9 线', image: 'https://images.unsplash.com/photo-1511739001486-6bfe10ce785f?auto=format&fit=crop&w=600&q=80' },
  { id: 2, name: '卢浮宫', type: '景点', rating: 4.8, transport: '地铁 1/7 线', image: 'https://images.unsplash.com/photo-1499856871958-5b9627545d1a?auto=format&fit=crop&w=600&q=80' },
  { id: 3, name: 'Le Jules Verne', type: '美食', rating: 4.7, transport: '铁塔内', image: 'https://images.unsplash.com/photo-1550966841-396ad886016a?auto=format&fit=crop&w=600&q=80' },
  { id: 4, name: '巴黎圣母院', type: '景点', rating: 4.6, transport: '地铁 4 线', image: 'https://images.unsplash.com/photo-1478147427282-58a87a120781?auto=format&fit=crop&w=600&q=80' },
  { id: 5, name: '蒙马特高地', type: '景点', rating: 4.7, transport: '地铁 12 线', image: 'https://images.unsplash.com/photo-1503917988258-f17ae3841648?auto=format&fit=crop&w=600&q=80' },
  { id: 6, name: '杜乐丽花园', type: '景点', rating: 4.5, transport: '地铁 1 线', image: 'https://images.unsplash.com/photo-1559110314-5211d0ef4c2c?auto=format&fit=crop&w=600&q=80' },
]

export const Attractions = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-6">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">发现巴黎的美</h1>
            <p className="text-gray-500 text-lg">精选当地最值得去的景点与不可错过的美食</p>
          </div>
          <div className="flex gap-2">
            {['全部', '景点', '美食', '购物', '咖啡馆'].map((tab) => (
              <button 
                key={tab}
                className={`px-6 py-2 rounded-full font-medium transition-all ${
                  tab === '全部' ? 'bg-primary-600 text-white shadow-md' : 'bg-white text-gray-600 hover:bg-gray-100'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {/* Pinterest style grid */}
        <div className="columns-1 sm:columns-2 lg:columns-3 gap-6 space-y-6">
          {ATTRACTIONS.map((item) => (
            <div key={item.id} className="break-inside-avoid bg-white rounded-3xl overflow-hidden shadow-sm hover:shadow-xl transition-all border border-gray-100 group cursor-pointer">
              <div className="relative">
                <img src={item.image} alt={item.name} className="w-full object-cover" />
                <div className="absolute top-4 left-4 bg-white/90 backdrop-blur px-3 py-1 rounded-full text-xs font-bold text-primary-600">
                  {item.type}
                </div>
              </div>
              <div className="p-6">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-xl font-bold text-gray-900 group-hover:text-primary-600 transition-colors">{item.name}</h3>
                  <div className="flex items-center text-yellow-400">
                    <span className="text-sm font-bold ml-1">★ {item.rating}</span>
                  </div>
                </div>
                <div className="flex items-center text-gray-400 text-sm">
                  <span className="mr-1">🚇</span>
                  {item.transport}
                </div>
              </div>
            </div>
          ))}
        </div>
        
        <div className="mt-16 text-center">
          <button className="px-10 py-4 bg-white border-2 border-gray-100 text-gray-900 font-bold rounded-2xl hover:bg-gray-50 transition-all">
            加载更多推荐
          </button>
        </div>
      </div>
    </div>
  )
}
