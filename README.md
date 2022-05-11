# TM-Seller

**Бот может**:
* Обновить инвентарь и выставить все трейдабельный вещи
* Выдать минимальные пороги всем выставленным вещам по вашим настройкам
* Биться с конкурентами за цену до ранее выданного минимального порога (Если у вещи нет конкурентов, либо минимальная цена конкурента выше минимального порога в 4 раза, то цена будет выставлена по максимальной цене за последние 50 покупок)
* Отправить проданные предметы покупателю
* Все что выше, только через прокси!

## Установка и использование
### Первым делом вам нужно настроить "Accounts & Settings.json" (Любым блокнотом)
Нужно понимать как определяется минимальный порог до которой бот будет опускать цену, для этого учитываются 3 переменные:
* **tm_min_threshold** : Коэффициент на который умножается средняя цена TM'a за N дней
* **steam_min_threshold** : Коэффициент на который умножается средняя цена Стима за N дней
* **price_per_days** : То самое количество дней (N) за которое определяется средняя цена

*Допустим у вас стоят стандартные настройки:*

> "tm_min_threshold": 0.94,  
>  "steam_min_threshold": 0.85,  
>  "price_per_days": 3

*Пускай средняя цена вещи на TM'е за 3 дня будет равна 100 (минимальный порог по TM'у = 94), а в Стиме средняя цена за 3 дня равняется 105 (Минимальный порог по Стиму = 89.25), то минимальный порог этой вещи будет выставлен по TM'у = 94*

*Следует уточнить, что в первую очередь смотрится порог ТМ'a, а порог стима нужно лишь для того, чтобы не продавать вещи в убыток. Т.е. если вернуться к примеру выше и представить что средняя цена на ТМ'е все также равна 100 (94), но средняя цена стима уже 120 (102), то минимальный порог будет выставлен по Стиму, т.к. Минимальный порог Стима > Минимального порога ТМ'a*

#### Остальные настройки
* **get_thresholds_every** : Обновлять минимальные пороги каждые N часов
* **list_items_every** : Выставлять вещи на продажу каждые N часов  

**Бот также может присылать вам уведомления в телеграмм в случаях если: Все вещи на аккаунте проданы, Логина на аккаунт, При неудачной попытке логина на аккаунт из-за Капчи либо чего-то непридвиденного.** Если вы не нуждаетесь в этих фунциях, то оставьте эти строки пустыми  
**Пример**
>"chat_id": "",  
>"token": ""  

**Если же вам это интересно, тo**  
* **chat_id** : Вы можете найти у @getmyid_bot в телеграмме, нас интересует строка *"Your user ID"*
* **token** : Вам надо будет создать своего бота в телеграмме, это сюда **@BotFather**

### Использование прокси
**Пример**
>"proxy": "login:password@ip:port"  

**Если прокси вам не нужно, то оставьте это поле пустым**
>"proxy": ""

Если вы запускаете бота через прокси, то рекомендуется выключить SIH в браузере и закрыть SDA, иначе бот не сможет отправлять обмены.
Так получается потому что у сессии бота и вашей разница в IP, и я не знаю как + не хочу это решать.

### Данные от аккаунта
* **Название вашего аккаунта** : Можете назвать его как хотите, это неважно. Важно то, что при запуске бота, вам придется ввести название нужного вам аккаунта (На котором будет работать бот)
* **tm_api** : ТМ Апи от вашего аккаунта
* **login** : Логин от стима
* **password** : Пароль от стима
* **maFile** : Название мафайла от аккаунта, должен лежать строго в папке "mafiles"  

#### Данные должны быть заполнены строго в формате JSON, можете проверять на ошибки здесь http://jsonviewer.stack.hu/

***

### Бот также может работать с несколькими аккаунтами сразу, достаточно запустить несколько экземпляров и запускать нужные вам аккаунты
#### Скачать бота вы можете в релизах - https://github.com/STWonderFool/TM-Seller/releases

***

#### Бот достаточно сырой, так что по всем багам, предложениям или вопросам обращаться сюда https://vk.com/yunosrage
##### А еще наверно стоит упомянуть что бот умеет работать только с рублями и кс вещами
