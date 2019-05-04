class Telebot:
    def __init__(self, url, session):
        self.url = url
        self.session = session
        
    async def get(self, url, json=dict())->dict:
        async with self.session.get(url, json=json) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(await response.json())
        return dict()

    async def post(self, url, json=dict())->dict:
        async with self.session.get(url, json=json) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(await response.json())
        return dict()


    async def sendMessage(self, chat_id, text, **kwargs)->dict:
        print("Send msg")
        url = self.url + 'sendMessage'
        params = {'chat_id': chat_id, 'text': text,  **kwargs}
        return await self.post(url, params)

    async def sendPhoto(self, chat_id, **kwargs)->dict:
        """
        photo="http://www.aisystems.ru/temp/hor/img/logo.png", caption="<b>Возвращение квантового кота</b>", parse_mode="html"
        """
        url = self.url + 'sendPhoto'
        params = {'chat_id': chat_id, **kwargs}
        return await self.post(url, params)

    async def sendAnimation(self, chat_id, **kwargs)->dict:
        """
        photo="http://www.aisystems.ru/temp/hor/img/logo.png", caption="<b>Возвращение квантового кота</b>", parse_mode="html"
        """
        url = self.url + 'sendAnimation'
        params = {'chat_id': chat_id, **kwargs}
        return await self.post(url, params)     

    async def sendVideo(self, chat_id, **kwargs)->dict:
        """
        photo="http://www.aisystems.ru/temp/hor/img/logo.png", caption="<b>Возвращение квантового кота</b>", parse_mode="html"
        """
        url = self.url + 'sendVideo'
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

