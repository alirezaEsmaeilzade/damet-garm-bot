from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from database import DB
from excel_report import wirteReportInExcelFile

admin_id = 1711499820
my_test_id = 1840222377
group_id = 1372458178
db = DB()


class Singleton(type):
    """Metaclass."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Users(object, metaclass=Singleton):
    def __init__(self):
        self.dict_of_users = {}

    def insert_user(self, user_id, chat_id):
        self.dict_of_users[user_id] = User(user_id, chat_id)

    def get_user(self, user_id):
        if user_id not in self.dict_of_users:
            return None
        return self.dict_of_users[user_id]

    def is_user_exist(self, user_id):
        if user_id not in self.dict_of_users:
            return False
        return True

    def reset_pin_capacity(self):
        for user in self.dict_of_users.values():
            user.pinCapcity = 5


class User:
    def __init__(self, chat_id, user_id):
        self.pinCapcity = 5
        self.chatID = chat_id
        self.userID = user_id
        self.name = None
        self.step = 0
        self.main_message = ''
        self.pressedButton1 = False
        self.pressedButton2 = False
        if DB.isUserExist(self.userID) == False:
            DB.insertUser(self.userID)
        else:
            self.pinCapcity = DB.getPinCapacity(self.userID)

    def setName(self, name):
        self.name = name

    def setReceiver(self, receiver):
        self.receiver = receiver

    def setChoicedPin(self, choicedPin):
        self.choicedPin = choicedPin

    def setChoicedPinNumber(self, choicedPinNumber):
        self.choicedPinNumber = choicedPinNumber

    def convertInputPinCodeForDB(self, input):
        if input == 'a':
            return 'One'
        if input == 'b':
            return 'Two'
        if input == 'c':
            return 'Three'
        if input == 'd':
            return 'Four'
        if input == 'e':
            return 'Five'
        return None

    def storeDataOfReceiver(self):
        pin = int(self.choicedPinNumber)
        name = str(self.receiver)
        inputType = self.convertInputPinCodeForDB(str(self.choicedPin))
        DB.storeDataOfReceiverInDB(pin, name, inputType)

    def decreasePinCapacity(self):
        if self.pinCapcity > 0 and self.pinCapcity >= self.choicedPinNumber:
            self.pinCapcity -= self.choicedPinNumber
            DB.storeUserDataInDB(self.pinCapcity, 'PinCapacity', self.userID)


def get_final_markup():
    keyboard = [
        [InlineKeyboardButton("برای ارسال پیام در گروه کلیک کنید", callback_data="send")],
        [InlineKeyboardButton("لغو ارسال", callback_data="canceled_send")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def get_pin_number_markup():
    keyboard = [
        [InlineKeyboardButton("1", callback_data="1")],
        [InlineKeyboardButton("2", callback_data="2")],
        [InlineKeyboardButton("3", callback_data="3")],
        [InlineKeyboardButton("4", callback_data="4")],
        [InlineKeyboardButton("5", callback_data="5")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def get_choice_markup():
    keyboard = [
        [InlineKeyboardButton("یادگیرندگی و یاد دهندگی", callback_data="a")],
        [InlineKeyboardButton("تعهد و مسولیت پذیری", callback_data="b")],
        [InlineKeyboardButton("همکاری تیمی", callback_data="c")],
        [InlineKeyboardButton("دغدغه محصول و مشتری", callback_data="d")],
        [InlineKeyboardButton("همینجوری دمت گرم", callback_data="e")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def reset_all_pin_capacity():
    users = Users()
    users.reset_pin_capacity()
    DB.resetAllPinCapacityOfReceiver()


def msgOfSortedUserByPin(data, pinType, i):
    y = sorted(data, key=lambda tup: tup[i], reverse=True)
    msg = pinType + '\n\n'
    for j in range(len(y)):
        msg += str(j + 1) + ') ' + str(y[j][0]) + ' تعداد پین: ' + str(y[j][i]) + '\n'
    return msg


def msgOfSortedUserBySumOfAllPin(data):
    y = []
    for i in data:
        y.append([i[0], sum(list(i[1:]))])
    z = sorted(y, key=lambda list: list[1], reverse=True)
    msg = 'رتبه بندی کلی لیگ برتر دمت گرم' + '\n\n'
    for i in range(len(z)):
        msg += str(i + 1) + ') ' + str(z[i][0]) + ' تعداد پین: ' + str(z[i][1]) + '\n'
    return msg


def echo(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    l = globals()
    users = Users()
    if update.message.chat.type == "group":
        return

    if not users.is_user_exist(user_id):
        users.insert_user(user_id, chat_id)
    curr_user = users.get_user(user_id)
    text = update.message.text
    if text == 'send report':
        if user_id == l['admin_id'] or user_id == l['my_test_id']:
            data = DB.GetInfoForSendReportInGroup()
            if data == None:
                context.bot.send_message(chat_id, "هیچ داده ای موجود نیست")
                return
            pinType = ["یادگیرندگی و یاد دهندگی", "تعهد و مسولیت پذیری", "همکاری تیمی", "دغدغه محصول و مشتری",
                       "همینجوری دمت گرم"]
            for i in range(1, 5):
                msg = msgOfSortedUserByPin(data, pinType[i], i)
                context.bot.send_message(chat_id, msg)
            msg = msgOfSortedUserBySumOfAllPin(data)
            context.bot.send_message(chat_id, msg)
            return
    elif text == 'send report file':
        if user_id == l['admin_id'] or user_id == l['my_test_id']:
            data = DB.GetInfoForSendReportInGroup()
            if data == None:
                context.bot.send_message(chat_id, "هیچ داده ای موجود نیست")
                return
            wirteReportInExcelFile(data)
            context.bot.send_document(chat_id=chat_id, document=open('report.xlsx', 'rb'))
            DB.deletetDataOfReceiver()
            return
    elif text == 'reset pin':
        if user_id == l['admin_id'] or user_id == l['my_test_id']:
            reset_all_pin_capacity()
            context.bot.send_message(chat_id, "ظرفیت پین ها با موفقیت آپدیت شد")
            return
    step = curr_user.step
    if step == 0:
        if curr_user.pinCapcity == 0:
            context.bot.send_message(chat_id, "متاسفانه تعداد پین های شما به پایان رسیده است")
            return
        context.bot.send_message(chat_id, "لطفا نام و نام خانوادگی خود را وارد کنید")
        curr_user.step = 1
    elif step == 1:
        curr_user.main_message += "پین دهنده: " + text + "\n"
        curr_user.setName(text)  # can invalid name
        curr_user.step = 2
        context.bot.send_message(chat_id, "لطفا نام و نام خانوادگی گیرنده را واردکنید را وارد کنید")
    elif step == 2:
        if curr_user.name == text:
            context.bot.send_message(chat_id,
                                     "خطا: نام پین دهنده و گیرنده نمی تواند یکسان باشد لطفا مجددا نام گیرنده را ارسال فرمایید")
            return
        curr_user.main_message += "گیرنده: " + text + "\n"
        curr_user.setReceiver(text)
        context.bot.send_message(chat_id, "لطفا نوع پین را انتخاب کنید", reply_markup=get_choice_markup())
        curr_user.step = 3
    elif step == 3:
        if not curr_user.pressedButton1:
            context.bot.send_message(chat_id, "خطا!: لطفا ابتدا نوع پین را از پیام قبل انتخاب کنید")
            return
        if not curr_user.pressedButton2:
            context.bot.send_message(chat_id, "خطا!: لطفا ابتدا تعداد پین را از پیام قبل انتخاب کنید")
            return
        curr_user.main_message += "دلیل و توضیحات: " + text + "\n"
        context.bot.send_message(chat_id, curr_user.main_message, reply_markup=get_final_markup())


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    users = Users()
    user_id = query.from_user.id
    curr_user = users.get_user(user_id)
    l = globals()
    if query.data in ['a', 'b', 'c', 'd', 'e']:
        if curr_user.step != 3 or curr_user.pressedButton1:
            return
        curr_user.main_message += "نوع پین: "
        curr_user.setChoicedPin(query.data)
        chosen_button = ''
        if query.data == "a":
            chosen_button = "یادگیرندگی و یاد دهندگی"
        elif query.data == "b":
            chosen_button = "تعهد و مسولیت پذیری"
        elif query.data == "c":
            chosen_button = "همکاری تیمی"
        elif query.data == "d":
            chosen_button = "دغدغه محصول و مشتری"
        elif query.data == "e":
            chosen_button = "همینجوری دمت گرم"

        curr_user.main_message += chosen_button
        curr_user.main_message += "\n"
        curr_user.pressedButton1 = True
        context.bot.send_message(curr_user.chatID, "نوع پین انتخاب شد")
        pinMsg = "لطفا تعداد پین های خود را انتخاب کنید" + '\n' + " (ظرفیت پین شما در ماه حداکثر ۵ پین است)"
        context.bot.send_message(curr_user.chatID, pinMsg, reply_markup=get_pin_number_markup())
    elif query.data in ['1', '2', '3', '4', '5']:
        if curr_user.step != 3 or curr_user.pressedButton2:
            return
        if curr_user.pinCapcity < int(query.data):
            errorMsg = "خطا!: موجودی پین های شما ناکافی است. موجودی : " + str(
                curr_user.pinCapcity) + "\n"
            context.bot.send_message(curr_user.chatID, errorMsg)
            if curr_user.pinCapcity != 0:
                errorMsg = "لطفا مجددا از پیام قبلی تعداد پین ها را انتخاب کنید" + "\n"
                context.bot.send_message(curr_user.chatID, errorMsg)
            return
        curr_user.pressedButton2 = True
        curr_user.setChoicedPinNumber(int(query.data))
        curr_user.main_message += "تعداد پین : " + query.data + "\n"
        context.bot.send_message(curr_user.chatID, "تعداد پین انتخاب شد")
        context.bot.send_message(curr_user.chatID, "لطفا دلیل و توضیحات خود را وارد کنید")
    elif query.data == "send":
        curr_user.decreasePinCapacity()
        context.bot.send_message(l['group_id'], curr_user.main_message)
        numberOfpinsStr = str(curr_user.pinCapcity) + "\n"
        context.bot.send_message(curr_user.chatID,
                                 "پیام در گروه ارسال شد تعداد پین باقی مانده: " + numberOfpinsStr)
        context.bot.send_message(curr_user.chatID,
                                 "برای ارسال مجدد پیام دستور" + " /start " + "را بزنید")
        curr_user.step = 0
        curr_user.main_message = ''
        curr_user.storeDataOfReceiver()
        curr_user.pressedButton1 = False
        curr_user.pressedButton2 = False

    elif query.data == "canceled_send":
        context.bot.send_message(curr_user.chatID, "ارسال پیام لغو شد")
        context.bot.send_message(curr_user.chatID,
                                 "برای ارسال مجدد پیام دستور" + " /start " + "را بزنید")
        curr_user.step = 0
        curr_user.main_message = ''
        curr_user.pressedButton1 = False
        curr_user.pressedButton2 = False


def main() -> None:
    updater = Updater(token='TOKEN', use_context=True)
    DB.makeTable()
    echo_handler = MessageHandler(Filters.text, echo)
    updater.dispatcher.add_handler(echo_handler)
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
