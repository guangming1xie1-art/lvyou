import { Link } from 'react-router-dom'

export const Home = () => {
  return (
    <div className="container mx-auto px-4 py-12">
      <section className="text-center mb-16">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">欢迎来到智能旅游助手</h1>
        <p className="text-xl text-gray-600 mb-8">让 AI 为您定制专属的旅行方案，轻松规划完美旅程</p>
        <Link
          to="/info-collection"
          className="inline-block px-8 py-4 bg-primary-600 text-white text-lg font-semibold rounded-lg hover:bg-primary-700 transition-colors shadow-lg"
        >
          开始定制行程
        </Link>
      </section>

      <section className="grid md:grid-cols-3 gap-8 mb-16">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
            <span className="text-2xl">🎯</span>
          </div>
          <h3 className="text-xl font-semibold mb-2">智能推荐</h3>
          <p className="text-gray-600">基于您的偏好和预算，AI 智能生成多套旅行方案供您选择</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="w-12 h-12 bg-secondary-100 rounded-lg flex items-center justify-center mb-4">
            <span className="text-2xl">📅</span>
          </div>
          <h3 className="text-xl font-semibold mb-2">详细规划</h3>
          <p className="text-gray-600">每日行程安排清晰明了，包含景点、餐饮、住宿等完整信息</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="w-12 h-12 bg-accent-100 rounded-lg flex items-center justify-center mb-4">
            <span className="text-2xl">💰</span>
          </div>
          <h3 className="text-xl font-semibold mb-2">费用透明</h3>
          <p className="text-gray-600">详细的费用明细，让您清楚了解每一笔开支，合理控制预算</p>
        </div>
      </section>

      <section className="bg-gray-50 rounded-lg p-8">
        <h2 className="text-3xl font-bold text-center mb-8">如何使用</h2>
        <div className="grid md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="w-16 h-16 bg-primary-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
              1
            </div>
            <h4 className="font-semibold mb-2">填写信息</h4>
            <p className="text-sm text-gray-600">输入目的地、日期、人数和预算</p>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 bg-primary-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
              2
            </div>
            <h4 className="font-semibold mb-2">查看方案</h4>
            <p className="text-sm text-gray-600">AI 生成多套旅行方案</p>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 bg-primary-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
              3
            </div>
            <h4 className="font-semibold mb-2">选择方案</h4>
            <p className="text-sm text-gray-600">对比选择最适合的方案</p>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 bg-primary-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
              4
            </div>
            <h4 className="font-semibold mb-2">确认订单</h4>
            <p className="text-sm text-gray-600">提交订单，开始旅程</p>
          </div>
        </div>
      </section>
    </div>
  )
}
