import aiohttp  # 用于异步 HTTP 请求
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

@register("ai_plugin", "YourName", "一个 AI 对话插件", "1.0.0")
class AIPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self._listening = False  # 是否正在监听用户消息

    @filter.command("start")
    async def start(self, event: AstrMessageEvent):
        '''开始监听用户消息'''
        self._listening = True
        yield event.plain_result("已开始监听你的消息。发送 /ai <消息> 来与 AI 对话。")

    @filter.command("stop")
    async def stop(self, event: AstrMessageEvent):
        '''停止监听用户消息'''
        self._listening = False
        yield event.plain_result("已停止监听你的消息。")

    async def handle_message(self, event: AstrMessageEvent):
        '''处理用户消息'''
        if not self._listening:
            return  # 如果未在监听状态，直接返回

        message_str = event.message_str
        if message_str.startswith("/ai"):
            # 提取 /ai 后面的内容
            ai_message = message_str[len("/ai"):].strip()
            if ai_message:
                # 调用 API 并获取响应
                api_response = await self.call_api(ai_message)
                yield event.plain_result(f"AI 回复: {api_response}")
            else:
                yield event.plain_result("请发送 /ai <消息> 来与 AI 对话。")

    async def call_api(self, message: str) -> str:
        '''调用指定的 API 接口'''
        api_url = "https://your-api-endpoint.com/chat"  # 替换为你的 API 地址
        payload = {"message": message}  # 请求参数
        headers = {"Content-Type": "application/json"}  # 请求头

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(api_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("response", "API 未返回有效内容")
                    else:
                        return f"API 请求失败，状态码: {response.status}"
            except Exception as e:
                logger.error(f"API 请求出错: {e}")
                return "API 请求出错，请稍后再试。"

    @filter.message
    async def on_message(self, event: AstrMessageEvent):
        '''监听用户消息'''
        await self.handle_message(event)

    async def terminate(self):
        '''插件卸载时调用'''
        self._listening = False
        logger.info("AI 插件已卸载。")