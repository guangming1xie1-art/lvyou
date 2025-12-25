export const Footer = () => {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="bg-gray-800 text-white mt-auto">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-lg font-semibold mb-4">
              {import.meta.env.VITE_APP_NAME || '旅游助手'}
            </h3>
            <p className="text-gray-400">智能定制您的完美旅程</p>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-4">快捷链接</h3>
            <ul className="space-y-2">
              <li>
                <a href="/" className="text-gray-400 hover:text-white transition-colors">
                  首页
                </a>
              </li>
              <li>
                <a
                  href="/info-collection"
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  定制行程
                </a>
              </li>
              <li>
                <a href="/attractions" className="text-gray-400 hover:text-white transition-colors">
                  景点美食
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-4">联系我们</h3>
            <ul className="space-y-2 text-gray-400">
              <li>邮箱：support@travel-assistant.com</li>
              <li>电话：400-123-4567</li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-700 mt-8 pt-8 text-center text-gray-400">
          <p>&copy; {currentYear} 旅游助手. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}
