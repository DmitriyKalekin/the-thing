
# 108 карт
# 88 карт событий (с рубашкой «Событие»)
# 20 карт паники (с рубашкой «Паника»)

# from app.player import Player
# from app.card import Card
from app.card import (
    Card, 
    CardEvil, CardInfection, CardFlamethrower, CardBloodTest, CardAxe, CardSuspicion, CardWhiskey,
    CardPerseverance, CardLookAround, CardChangePlaces, CardWindUps, CardTemptation, CardFear, CardNotBadHere,
    CardNoThanks, CardMiss, CardNoBbq, CardQuarantine, CardDoor, CardOldRope, CardOneTwo, CardThreeFour,
    CardParty, CardGoAway, CardForgetfulness, CardChainReaction, CardFriendship, CardBlindDating, CardOops,
    CardBetweenUs, CardConfessionTime, CardLovecraft, CardNecronomicon
)


game_info = {  # приоритизация
    "on_start_tip": "```\nВам раздали карты: посмотрите личные сообщения.\nБудьте готовы за WhoMoneyQ и двор стрелять в упор!\n```",
    "description":  "Игра *\"Теряя гуманность\"* начинается!\n"
                    "Вы -- разработчики криптовалютного стартапа `WhoMoneyQ`, собравшего весь свой штат на ежегодной встрече-хакатоне с целью обсуждения перспектив развития проекта.\n\n"
                    "По прибытии на территорию парк-отеля вы случайно попадаете в толпу участников движения ЛГБТ, "
                    "помогающих 👾`Алексу Ф.` приоритизировать актуальные направления \"парющих болей\", "
                    "которых загнали на территорию отеля купавшиеся в фонтане неподалёку ВДВшники.\n\n"
                    "Вам удалось в составе небольшой группы спешно забежать внутрь отеля и заколотить дверь 🚪. "
                    "Поскольку до этого момента вы в лицо не видели других участников (надо было включать видео в Zoom'е), "
                    "то даже не подозреваете, что 👾`The Алексей` успел проникнуть внутрь отеля и сейчас прячется среди вас, очень близко к вам. "
                    "Настолько близко, что, может быть, это и есть... вы 😱!\n\n"
                    "🎯 *Цель игры*\n"
                    "В начале игры все участники - разработчики с нормальной психикой 👩‍💻. Со временем некоторые игроки заразятся идеями 👾`Алекса` "
                    "и пойдут приоритизировать в отдел каздева 🧟‍. В результате получатся две соперничающие команды:\n"
                    "👨‍💻👩‍💻 *1. Разработчики*\n"
                    "Цель разработчиков совместными усилиями вычислить и вылечить 👾`Алекса`.\n"
                    "👾🧟‍ *2. Алекс и каздевщики*\n"
                    "На первом ходу один из игроков понимает, что он и есть 👾`The Алекс`. Его цель - избавиться от всех разработчиков:\n"
                    "либо превратив их в подконтрольных ему каздевщиков 🧟‍, либо госпитализировав в псих-диспансер 👨‍⚕️. "
                    "🧟‍ Задача каздевщиков подыгрывать 👾`Алексу` в порывах буйных психических возбуждений 🤪."
}


# def evil____on_taken(self, p: Player):
#     print(f"!!! {p.name} стал Нечто")
#     p.become_evil()


# def infection____on_given(self, p: Player, sender: Player):
#     assert self.is_infection(), "Текущая карта - заражение"
#     assert sender.is_evil() or p.is_evil() and sender.is_infected(), "Либо нечто передаёт, либо мы сами нечто и нам передаёт заражённый"
#     assert not sender.is_good(), "Люди не могут передавать заражение"
#     assert not (sender.is_infected() and (p.is_good() or p.is_infected())), "Зараженный не может передавать человеку или зараженному (только Нечто может)"
#     print("!!! Заражение принято ")
#     p.become_infected()
#     # super(Card, self).on_received(p, sender)


# def flamethrower____on_played_to_person(self, p: Player, target: Player):
#     print(f"{p.name} сыграл. {self.name} сыгран на игрока", target.name)
#     pass


# def blood_test____on_played_to_person(self, p: Player, target: Player):
#     print(f"{p.name} сыграл. {self.name} сыгран на игрока", target.name)
#     pass


card_deck_struct = [
    {
        "_uuids": [1],
        "_class_name": "CardEvil",
        "type": "infection",
        "color": "green",
        "name": "Нечто",
        "_players": [0],
        "images": ["green-the-thing"],
        # "on_taken": evil____on_taken
    },
    {
        "_uuids": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21],
        "_class_name": "CardInfection",
        "type": "event",
        "color": "green",
        "name": "Заражение",
        "_players": [4, 4, 4, 4, 4, 4, 4, 4, 6, 7, 7, 7, 8, 9, 9, 10, 10, 11, 11, 11],
        "images": [
            "green-infection-1",
            "green-infection-2",
            "green-infection-3",
            "green-infection-4"
        ],
        # "on_given": infection____on_given
    },
    {
        "_uuids": [22, 23, 24, 25, 26],
        "_class_name": "CardFlamethrower",
        "type": "event",
        "color": "green",
        "name": "Огнемёт",
        "_players": [4, 4, 6, 9, 11],
        "images": ["green-flamethrower"],
        "person_target": ["prev", "next"]
        # "on_played_to_person": flamethrower____on_played_to_person,
    },
    {
        "_uuids": [27, 28, 29],
        "_class_name": "CardBloodTest",
        "type": "event",
        "color": "green",
        "name": "Анализ",
        "_players": [5, 6, 9],
        "images": ["green-blood-test"],
        "person_target": ["prev", "next"]
        # "on_played_to_person": blood_test____on_played_to_person,
       
    },
    {
        "_uuids": [30, 31],
        "_class_name": "CardAxe",
        "type": "event",
        "color": "green",
        "name": "Топор",
        "_players": [4, 9],
        "images": ["green-axe"],
        "person_target": ["self", "prev", "next"]
        
    },
    {
        "_uuids": [32, 33, 34, 35, 36, 37, 38, 39],
        "_class_name": "CardSuspicion",
        "type": "event",
        "color": "green",
        "name": "Подозрение",
        "_players": [4, 4, 4, 4, 7, 8, 9, 10], 
        "images": ["green-suspicion"],
        "person_target": ["prev", "next"]
        
    },
    {
        "_uuids": [40, 41, 42],
        "_class_name": "CardWhiskey",
        "type": "event",
        "color": "green",
        "name": "Виски",
        "_players": [4, 6, 10],
        "images": ["green-whiskey"],
        "person_target": ["self"]
        
    },
    {
        "_uuids": [43, 44, 45, 46, 47],
        "_class_name": "CardPerseverance",
        "type": "event",
        "color": "green",
        "name": "Упорство",
        "_players": [4, 4, 6, 9, 10],
        "images": ["green-perseverance"]
        
    },
    {
        "_uuids": [48, 49],
        "_class_name": "CardLookAround",
        "type": "event",
        "color": "green",
        "name": "Гляди по сторонам",
        "_players": [4, 9],
        "images": ["green-look-around"],
        
    },    
    {
        "_uuids": [50, 51, 52, 53, 54],
        "_class_name": "CardChangePlaces",
        "type": "event",
        "color": "green",
        "name": "Меняемся местами",
        "_players": [4, 4, 7, 9, 11],
        "images": ["green-change-places"],
        "person_target": ["prev", "next"]
        
    },
    {
        "_uuids": [55, 56, 57, 58, 59],
        "_class_name": "CardWindUps",
        "type": "event",
        "color": "green",
        "name": "Сматывай удочки",
        "_players": [4, 4, 7, 9, 11],
        "images": ["green-wind-up"],
        "person_target": ["any"]
        
    },
    {
        "_uuids": [60, 61, 62, 63, 64, 65, 66],
        "_class_name": "CardTemptation",
        "type": "event",
        "color": "green",
        "name": "Соблазн",
        "_players": [4, 4, 6, 7, 8, 10, 11],
        "images": ["green-temptation"],
        "person_target": ["any"]
        
    },
    # {"": "====================================== BLUE ========================================"},                                                
    {
        "_uuids": [67, 68, 69, 70],
        "_class_name": "CardFear",
        "type": "event",
        "color": "blue",
        "name": "Страх",
        "_players": [5, 6, 8, 11],
        "images": ["blue-fear"],
        
    },
    {
        "_uuids": [71, 72, 73],
        "_class_name": "CardNotBadHere",
        "type": "event",
        "color": "blue",
        "name": "Мне и здесь неплохо",
        "_players": [4, 6, 11],
        "images": ["blue-not-bad-here"],
        
    },
    {
        "_uuids": [74, 75, 76, 77],
        "_class_name": "CardNoThanks",
        "type": "event",
        "color": "blue",
        "name": "Нет уж, спасибо",
        "_players": [4, 6, 8, 11],
        "images": ["blue-no-th"],
        
    },
    {
        "_uuids": [78, 79, 80],
        "_class_name": "CardMiss",
        "type": "event",
        "color": "blue",
        "name": "Мимо",
        "_players": [4, 6, 11],
        "images": ["blue-miss"],
        
    },
    {
        "_uuids": [81, 82, 83],
        "_class_name": "CardNoBbq",
        "type": "event",
        "color": "blue",
        "name": "Никакого шашлыка",
        "_players": [4, 6, 11],
        "images": ["blue-no-bbq"],
        
    },
    # {"": "====================================== YELLOW ========================================"}, 
    {
        "_uuids": [84, 85],
        "_class_name": "CardQuarantine",
        "type": "event",
        "color": "yellow",
        "name": "Карантин",
        "_players": [5, 9],
        "images": ["yellow-quarantine"],
        "person_target": ["self", "prev", "next"]
        
    },
    {
        "_uuids": [86, 87, 88],
        "_class_name": "CardDoor",
        "type": "event",
        "color": "yellow",
        "name": "Заколоченная дверь",
        "_players": [4, 7, 11],
        "images": ["yellow-door"],
        "person_target": ["prev", "next"]
        
    },
    # {"": "====================================== RED ========================================"},
    {
        "_uuids": [89, 90],
        "_class_name": "CardOldRope",
        "type": "panic",
        "color": "red",
        "name": "Старые верёвки",
        "_players": [6, 9],
        "images": ["panic-old-rope"],
    },
    {
        "_uuids": [91, 92],
        "_class_name": "CardOneTwo",
        "type": "panic",
        "color": "red",
        "name": "Раз-два",
        "_players": [5, 9],
        "images": ["panic-one-two"],
    },
    {
        "_uuids": [93, 94],
        "_class_name": "CardThreeFour",
        "type": "panic",
        "color": "red",
        "name": "Три-четыре",
        "_players": [4, 9],
        "images": ["panic-three-four"],
    },
    {
        "_uuids": [95, 96],
        "_class_name": "CardParty",
        "type": "panic",
        "color": "red",
        "name": "И это вы называете вечеринкой?",
        "_players": [5, 9],
        "images": ["panic-party"],
    },
    {
        "_uuids": [97],
        "_class_name": "CardGoAway",
        "type": "panic",
        "color": "red",
        "name": "Убирайся прочь!",
        "_players": [5],
        "images": ["panic-go-away"],
    },
    {
        "_uuids": [98],
        "_class_name": "CardForgetfulness",
        "type": "panic",
        "color": "red",
        "name": "Забывчивость",
        "_players": [4],
        "images": ["panic-forgetfulness-950x1343"],
    },
    {
        "_uuids": [99, 100],
        "_class_name": "CardChainReaction",
        "type": "panic",
        "color": "red",
        "name": "Цепная реакция",
        "_players": [4, 9],
        "images": ["panic-chain-reaction"],
    },
    {
        "_uuids": [101, 102],
        "_class_name": "CardFriendship",
        "type": "panic",
        "color": "red",
        "name": "Давай дружить",
        "_players": [7, 9],
        "images": ["panic-friendship"],
    },
    {
        "_uuids": [103, 104],
        "_class_name": "CardBlindDating",
        "type": "panic",
        "color": "red",
        "name": "Свидание вслепую",
        "_players": [4, 9],
        "images": ["panic-blind-dating"],
    },
    {
        "_uuids": [105],
        "_class_name": "CardOops",
        "type": "panic",
        "color": "red",
        "name": "Упс",
        "_players": [10],
        "images": ["panic-oops"],
    },
    {
        "_uuids": [106, 107],
        "_class_name": "CardBetweenUs",
        "type": "panic",
        "color": "red",
        "name": "Только между нами",
        "_players": [7, 9],
        "images": ["panic-between-us"],
    },
    {
        "_uuids": [108],
        "_class_name": "CardConfessionTime",
        "type": "panic",
        "color": "red",
        "name": "Время признаний",
        "_players": [8],
        "images": ["panic-confession-time"],
    },
    # {"": "-------------------------ПРОМО-----------------------------------------------------"},
    {
        "_uuids": [109],
        "_class_name": "CardLovecraft",
        "type": "event",
        "color": "green",
        "name": "Лавкрафт",
        "_players": [6],
        "images": ["green-lovecraft"],
        
    },
    {
        "_uuids": [110],
        "_class_name": "CardNecronomicon",
        "type": "event",
        "color": "green",
        "name": "Некрономикон",
        "_players": [10],
        "images": ["green-necronomicon"],
        
    }    
]