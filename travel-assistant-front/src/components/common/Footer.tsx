import { Link } from 'react-router-dom'

export const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white py-16">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
          <div className="col-span-1 md:col-span-1">
            <Link to="/" className="text-2xl font-bold text-primary-500 mb-6 block">
              旅游助手
            </Link>
            <p className="text-gray-400 text-sm leading-relaxed">
              AI 驱动的智能旅游规划平台，使用 LangGraph + DeepAgent + Claude 帮助用户快速生成最佳旅游方案。
            </p>
          </div>
          
          <div>
            <h4 className="font-bold mb-6">快速链接</h4>
            <ul className="space-y-4 text-sm text-gray-400">
              <li><Link to="/" className="hover:text-primary-500 transition-colors">首页</Link></li>
              <li><Link to="/info-collection" className="hover:text-primary-500 transition-colors">定制行程</Link></li>
              <li><Link to="/attractions" className="hover:text-primary-500 transition-colors">景点美食</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-bold mb-6">服务支持</h4>
            <ul className="space-y-4 text-sm text-gray-400">
              <li><a href="#" className="hover:text-primary-500 transition-colors">帮助中心</a></li>
              <li><a href="#" className="hover:text-primary-500 transition-colors">预订协议</a></li>
              <li><a href="#" className="hover:text-primary-500 transition-colors">隐私政策</a></li>
            </ul>
          </div>

          <div>
            <h4 className="font-bold mb-6">联系我们</h4>
            <ul className="space-y-4 text-sm text-gray-400">
              <li className="flex items-center gap-2">
                <span>📍</span> 北京市朝阳区某某大厦
              </li>
              <li className="flex items-center gap-2">
                <span>📞</span> 400-123-4567
              </li>
              <li className="flex items-center gap-2">
                <span>✉️</span> support@travel-ai.com
              </li>
            </ul>
          </div>
        </div>
        
        <div className="pt-8 border-t border-gray-800 text-center text-sm text-gray-500">
          <p>© {new Date().getFullYear()} 旅游智能助手. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}
