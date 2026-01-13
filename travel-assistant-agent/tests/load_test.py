"""
负载测试脚本
测试 API 在高负载下的性能
"""
import asyncio
import aiohttp
import time
from typing import List, Dict
import statistics


BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/agent"


class LoadTester:
    """负载测试器"""

    def __init__(self, base_url: str = API_URL):
        self.base_url = base_url
        self.results: List[Dict] = []

    async def make_request(
        self,
        session: aiohttp.ClientSession,
        endpoint: str,
        method: str = "POST",
        data: dict = None
    ) -> Dict:
        """发送单个请求"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method == "POST":
                async with session.post(url, json=data) as response:
                    status = response.status
                    response_data = await response.json()
                    elapsed = time.time() - start_time
                    
                    return {
                        "success": True,
                        "status": status,
                        "elapsed": elapsed,
                        "cache_hit": response_data.get("cache_hit", False)
                    }
            else:
                async with session.get(url) as response:
                    status = response.status
                    await response.json()
                    elapsed = time.time() - start_time
                    
                    return {
                        "success": True,
                        "status": status,
                        "elapsed": elapsed
                    }
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "elapsed": elapsed
            }

    async def run_concurrent_requests(
        self,
        num_requests: int,
        endpoint: str,
        method: str = "POST",
        data: dict = None
    ):
        """并发运行多个请求"""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.make_request(session, endpoint, method, data)
                for _ in range(num_requests)
            ]
            
            results = await asyncio.gather(*tasks)
            self.results.extend(results)
            return results

    def print_stats(self):
        """打印统计信息"""
        if not self.results:
            print("没有测试结果")
            return

        successful = [r for r in self.results if r["success"]]
        failed = [r for r in self.results if not r["success"]]
        
        if not successful:
            print("所有请求都失败了")
            return

        elapsed_times = [r["elapsed"] for r in successful]
        cache_hits = sum(1 for r in successful if r.get("cache_hit"))
        
        print("\n" + "="*60)
        print("负载测试结果")
        print("="*60)
        print(f"总请求数:       {len(self.results)}")
        print(f"成功请求:       {len(successful)} ({len(successful)/len(self.results)*100:.1f}%)")
        print(f"失败请求:       {len(failed)} ({len(failed)/len(self.results)*100:.1f}%)")
        print(f"缓存命中:       {cache_hits} ({cache_hits/len(successful)*100:.1f}%)")
        print("-"*60)
        print(f"平均响应时间:   {statistics.mean(elapsed_times):.3f}s")
        print(f"中位响应时间:   {statistics.median(elapsed_times):.3f}s")
        print(f"最快响应:       {min(elapsed_times):.3f}s")
        print(f"最慢响应:       {max(elapsed_times):.3f}s")
        print(f"P95 响应时间:   {statistics.quantiles(elapsed_times, n=20)[18]:.3f}s")
        print(f"P99 响应时间:   {statistics.quantiles(elapsed_times, n=100)[98]:.3f}s")
        print("="*60 + "\n")


async def test_search_endpoint(num_requests: int = 100):
    """测试搜索端点"""
    print(f"\n开始测试搜索端点 ({num_requests} 个请求)...")
    
    tester = LoadTester()
    
    search_request = {
        "origin": "Beijing",
        "destination": "Tokyo",
        "departure_date": "2025-02-01",
        "return_date": "2025-02-10",
        "passengers": 2,
        "cabin_class": "economy",
        "include_hotels": True,
        "check_in_date": "2025-02-01",
        "check_out_date": "2025-02-10",
        "rooms": 1
    }
    
    start_time = time.time()
    await tester.run_concurrent_requests(
        num_requests,
        "/search",
        method="POST",
        data=search_request
    )
    total_time = time.time() - start_time
    
    print(f"总耗时: {total_time:.2f}s")
    print(f"吞吐量: {num_requests/total_time:.2f} req/s")
    
    tester.print_stats()


async def test_recommend_endpoint(num_requests: int = 100):
    """测试推荐端点"""
    print(f"\n开始测试推荐端点 ({num_requests} 个请求)...")
    
    tester = LoadTester()
    
    recommend_request = {
        "destination": "Tokyo",
        "start_date": "2025-02-01",
        "end_date": "2025-02-10",
        "preferences": ["culture", "food", "shopping"],
        "budget": "medium",
        "include_attractions": True,
        "include_weather": True,
        "include_reviews": False
    }
    
    start_time = time.time()
    await tester.run_concurrent_requests(
        num_requests,
        "/recommend",
        method="POST",
        data=recommend_request
    )
    total_time = time.time() - start_time
    
    print(f"总耗时: {total_time:.2f}s")
    print(f"吞吐量: {num_requests/total_time:.2f} req/s")
    
    tester.print_stats()


async def test_cache_effectiveness():
    """测试缓存效果"""
    print("\n测试缓存效果...")
    print("="*60)
    
    tester = LoadTester()
    
    search_request = {
        "origin": "Shanghai",
        "destination": "Osaka",
        "departure_date": "2025-03-01",
        "return_date": "2025-03-10",
        "passengers": 1
    }
    
    # 第一次请求（应该未命中缓存）
    print("第一次请求（预期：缓存未命中）...")
    results_1 = await tester.run_concurrent_requests(
        1,
        "/search",
        method="POST",
        data=search_request
    )
    
    if results_1[0]["success"]:
        print(f"  响应时间: {results_1[0]['elapsed']:.3f}s")
        print(f"  缓存命中: {results_1[0].get('cache_hit', False)}")
    
    # 等待一下确保缓存已写入
    await asyncio.sleep(0.5)
    
    # 第二次请求（应该命中缓存）
    print("\n第二次请求（预期：缓存命中）...")
    results_2 = await tester.run_concurrent_requests(
        1,
        "/search",
        method="POST",
        data=search_request
    )
    
    if results_2[0]["success"]:
        print(f"  响应时间: {results_2[0]['elapsed']:.3f}s")
        print(f"  缓存命中: {results_2[0].get('cache_hit', False)}")
    
    # 计算性能提升
    if results_1[0]["success"] and results_2[0]["success"]:
        speedup = results_1[0]["elapsed"] / results_2[0]["elapsed"]
        improvement = (1 - results_2[0]["elapsed"] / results_1[0]["elapsed"]) * 100
        print(f"\n性能提升: {speedup:.2f}x ({improvement:.1f}% 更快)")
    
    print("="*60)


async def test_pagination_performance():
    """测试分页性能"""
    print("\n测试分页性能...")
    print("="*60)
    
    tester = LoadTester()
    
    search_request = {
        "origin": "Guangzhou",
        "destination": "Seoul",
        "departure_date": "2025-04-01",
        "passengers": 2
    }
    
    # 测试不同页面大小的性能
    page_sizes = [10, 20, 50, 100]
    
    for page_size in page_sizes:
        print(f"\n测试页面大小: {page_size}")
        
        # 构建带分页参数的请求
        # 注意：需要在 URL 中添加查询参数
        endpoint = f"/search?page=1&page_size={page_size}"
        
        results = await tester.run_concurrent_requests(
            10,
            endpoint,
            method="POST",
            data=search_request
        )
        
        successful = [r for r in results if r["success"]]
        if successful:
            avg_time = statistics.mean([r["elapsed"] for r in successful])
            print(f"  平均响应时间: {avg_time:.3f}s")
    
    print("="*60)


async def stress_test(duration_seconds: int = 60):
    """压力测试 - 持续发送请求"""
    print(f"\n开始压力测试 (持续 {duration_seconds} 秒)...")
    print("="*60)
    
    tester = LoadTester()
    
    search_request = {
        "origin": "Beijing",
        "destination": "Tokyo",
        "departure_date": "2025-02-01",
        "passengers": 2
    }
    
    start_time = time.time()
    request_count = 0
    
    async with aiohttp.ClientSession() as session:
        while time.time() - start_time < duration_seconds:
            result = await tester.make_request(
                session,
                "/search",
                method="POST",
                data=search_request
            )
            tester.results.append(result)
            request_count += 1
            
            # 每 10 个请求打印一次进度
            if request_count % 10 == 0:
                elapsed = time.time() - start_time
                rps = request_count / elapsed
                print(f"  已发送 {request_count} 个请求 ({rps:.1f} req/s)", end="\r")
    
    total_time = time.time() - start_time
    print(f"\n\n完成压力测试:")
    print(f"  总请求数: {request_count}")
    print(f"  总耗时: {total_time:.2f}s")
    print(f"  平均吞吐量: {request_count/total_time:.2f} req/s")
    
    tester.print_stats()


async def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("Travel Assistant Agent - 负载测试")
    print("="*60)
    print(f"目标服务器: {BASE_URL}")
    print("="*60)
    
    # 检查服务器是否在线
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health") as response:
                if response.status == 200:
                    print("✓ 服务器在线\n")
                else:
                    print(f"✗ 服务器响应异常: {response.status}\n")
                    return
    except Exception as e:
        print(f"✗ 无法连接到服务器: {e}\n")
        print("请确保服务器正在运行: uvicorn src.main:app --reload")
        return
    
    # 运行测试
    try:
        # 1. 缓存效果测试
        await test_cache_effectiveness()
        
        # 2. 搜索端点负载测试
        await test_search_endpoint(num_requests=50)
        
        # 3. 推荐端点负载测试
        await test_recommend_endpoint(num_requests=50)
        
        # 4. 分页性能测试
        await test_pagination_performance()
        
        # 5. 压力测试（可选，注释掉以避免过长时间）
        # await stress_test(duration_seconds=30)
        
        print("\n所有测试完成！")
        
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n\n测试出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
