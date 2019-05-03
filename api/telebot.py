from aiohttp import ClientSession, ClientConnectionError
import ujson


class Telebot:
    def __init__(self, url):
        self.url = url
        
    async def get(self, url, json=dict())->dict:
        async with ClientSession(json_serialize=ujson.dumps) as session:
            async with session.get(url, json=json) as response:
                assert response.status == 200
                return await response.json()
        return dict()

    async def post(self, url, json=dict())->dict:
        async with ClientSession(json_serialize=ujson.dumps) as session:
            async with session.get(url, json=json) as response:
                assert response.status == 200
                return await response.json()
        return dict()


    async def sendMessage(self, chat_id, text, **kwargs)->dict:
        print("Send msg")
        url = self.url + 'sendMessage'
        params = {'chat_id': chat_id, 'text': text,  **kwargs}
        return await self.post(url, params)

    async def sendPhoto(self, chat_id, **kwargs)->dict:
        """
        """
        url = self.url + 'sendPhoto'
        params = {'chat_id': chat_id, **kwargs}
        return await self.post(url, params)


    async def setWebhook(self, wh_url)->dict:
        """
        """
        print("Setting: wh")
        url = self.url + "setWebhook?url=" + wh_url
        res = await self.get(url)
        return res
    

    async def getWebhookInfo(self)->dict:
        print("Get: wh")
        url = self.url + "getWebhookInfo"
        return await self.get(url)

    async def deleteWebhook(self)->dict:
        print("Del: wh")
        return await self.get(self.url + "deleteWebhook")


    async def getChatAdministrators(self, chat_id, **kwargs)->dict:
        url = self.url + 'getChatAdministrators'
        params = {'chat_id': chat_id, **kwargs}
        return await self.post(url, params)

    async def editMessageText(self, chat_id, message_id, text, **kwargs)->dict:
        url = self.url + 'editMessageText'
        params = {'chat_id': chat_id, 'message_id': message_id, 'text': text, **kwargs}
        return await self.post(url, params)

    async def paramsCallbackQuery(self, callback_query_id, text, **kwargs)->dict:
        url = self.url + 'paramsCallbackQuery'
        params = {'callback_query_id': callback_query_id, 'text': text, **kwargs}
        return await self.post(url, params)       

