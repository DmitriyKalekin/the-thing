class User:
    def __init__(self, d: dict):
        self.id = None
        self.is_bot = None
        self.first_name = None
        self.last_name = None
        self.username = None
        for k, v in d.items():
            if k not in self.__dict__:
                continue
            setattr(self, k, v) 


class Message:
    def __init__(self, d: dict):
        self.id = None
        self.sender = None 
        self.chat_id = None
        self.text = ""
        assert d["message"] is not None       
        for k, v in d["message"].items():
            if k == "from": 
                k = "sender"
                v = User(v)
            elif k == "chat":
                k = "chat_id"
                v = v["id"]
            elif k == "message_id":
                k = "id"
            elif k not in self.__dict__:
                continue                 
            setattr(self, k, v) 


class Callback:
    def __init__(self, d: dict):
        self.id = None
        self.sender = None 
        self.chat_id = None
        self.message_id = None
        self.data = ""
        assert d["callback_query"] is not None       
        for k, v in d["callback_query"].items():
            if k == "from": 
                k = "sender"
                v = User(v)
            elif k == "message":
                self.chat_id = v["chat"]["id"]
                self.message_id = v["message_id"]
                # k = "chat_id"
                # v = v["chat"]["id"]
            elif k not in self.__dict__:
                continue 
            setattr(self, k, v)   
    
    def __repr__(self):
        return "<Callback: %s, chat_id=%s, message_id=%s>" % (self.data, self.chat_id, self.message_id)  # self.__dict__           


class Telebot:
    def __init__(self, url, session):
        self.url = url
        self.session = session
       
    async def get(self, url, json=dict()) -> dict:
        async with self.session.get(url, json=json) as response:
            r = await response.json()
            if response.status != 200:
                pass
                # raise Warning(f"GET response.status {response.status} {url} {str(r)}\n\nparams: {str(json)}")
        return r

    async def post(self, url, json=dict()) -> dict:
        async with self.session.get(url, json=json) as response:
            r = await response.json()
            if response.status != 200:
                pass
                # raise Warning(f"POST response.status {response.status} {url} {str(r)}\n\nparams: {str(json)}")
        return r

    async def sendMessage(self, chat_id, text, **kwargs) -> dict:
        if "parse_mode" not in kwargs and "@" not in text:
            kwargs["parse_mode"] = "markdown"        
        url = self.url + 'sendMessage'
        params = {'chat_id': chat_id, 'text': text,  **kwargs}
        return await self.post(url, params)

    async def sendPhoto(self, chat_id, **kwargs) -> dict:
        """
        photo="http://www.aisystems.ru/temp/hor/img/logo.png", caption="<b>Возвращение квантового кота</b>", parse_mode="html"
        """
        url = self.url + 'sendPhoto'
        params = {'chat_id': chat_id, **kwargs}
        return await self.post(url, params)

    async def sendMediaGroup(self, chat_id, media: list, **kwargs) -> dict:
        """
        photo="http://www.aisystems.ru/temp/hor/img/logo.png", caption="<b>Возвращение квантового кота</b>", parse_mode="html"
        """
        url = self.url + 'sendMediaGroup'
        params = {'chat_id': chat_id, "media": media, **kwargs}
        return await self.post(url, params)

    async def sendAnimation(self, chat_id, **kwargs) -> dict:
        """
        """
        url = self.url + 'sendAnimation'
        params = {'chat_id': chat_id, **kwargs}
        return await self.post(url, params)     

    async def sendVideo(self, chat_id, **kwargs) -> dict:
        """
        """
        url = self.url + 'sendVideo'
        params = {'chat_id': chat_id, **kwargs}
        return await self.post(url, params)        

    async def setWebhook(self, wh_url) -> dict:
        """
        """
        print("Setting: wh")
        url = self.url + "setWebhook?url=" + wh_url
        res = await self.get(url)
        return res

    async def getWebhookInfo(self) -> dict:
        print("Get: wh")
        url = self.url + "getWebhookInfo"
        return await self.get(url)

    async def deleteWebhook(self) -> dict:
        print("Del: wh")
        return await self.get(self.url + "deleteWebhook")

    async def getChatAdministrators(self, chat_id, **kwargs) -> dict:
        url = self.url + 'getChatAdministrators'
        params = {'chat_id': chat_id, **kwargs}
        return await self.post(url, params)

    async def deleteMessage(self, chat_id, message_id) -> dict:
        url = self.url + 'deleteMessage'
        params = {'chat_id': chat_id, 'message_id': message_id}
        return await self.post(url, params)

    async def editMessageText(self, chat_id, message_id, text, **kwargs) -> dict:
        if "parse_mode" not in kwargs and "@" not in text:
            kwargs["parse_mode"] = "markdown"        
        url = self.url + 'editMessageText'
        params = {'chat_id': chat_id, 'message_id': message_id, 'text': text, **kwargs}
        return await self.post(url, params)

    async def editMessageMedia(self, chat_id, message_id, media, **kwargs) -> dict:
        url = self.url + 'editMessageMedia'
        params = {'chat_id': chat_id, 'message_id': message_id, 'media': media, **kwargs}
        return await self.post(url, params)    
    
    async def paramsCallbackQuery(self, callback_query_id, text, **kwargs) -> dict:
        url = self.url + 'paramsCallbackQuery'
        params = {'callback_query_id': callback_query_id, 'text': text, **kwargs}
        return await self.post(url, params)       

      