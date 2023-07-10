import os
import re
import threading
import asyncio
import webbrowser
import requests
from colorama import Fore, Back, Style
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
from bs4 import BeautifulSoup
from underthesea import word_tokenize
from googlesearch import search

from EdgeGPT import Chatbot, ConversationStyle
from Crypto.Util import number


#Pls copy your cookies bing.com web over "bing_cookies_your.json"
#You can use this extension in Google Chrome: "https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg?hl=eng" to copy cookies after you have already accessed Bing.com 

#Hãy copy cookies trang web bing.com của bạn vào "bing_cookies_your.json"
#Bạn có thể dùng extension trong Google Chrome: "https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg?hl=eng"để copy cookies khi đã truy cập vào Bing.com

cookies_path='bing_cookies_my.json'
mode = 0
wake_word = "alo"
import threading

class Program:
    def __init__(self):
        self.is_running = False
        self.is_paused = False
        self.pause_event = threading.Event()

    def run(self):
        self.is_running = True

    def stop(self):
        self.is_running = False


class bot_response:
    def __init__(self): 
        self.avt= Fore.MAGENTA + "\n   /)⑅/) \n꒰˶• ༝•˶꒱\n./づ~ ♡ Eula: " + Style.RESET_ALL
        self.avt2 =Fore.GREEN + "\n  (\ (\ \n(„• ֊ •„) ♡\n━O━O━━━━━ Bạn: " + Style.RESET_ALL
    def voice(self,query):
        tts = gTTS(query, lang='vi')
        tts.save('temp.mp3')
        playsound('temp.mp3')
        os.remove('temp.mp3')
    def text(self,query):
        print(self.avt + str(query))
    def text_voice(self,query):
        self.text(query)
        self.voice(query)

        
class user_command(bot_response):

    def __init__(self):
        super().__init__()
        self.r = sr.Recognizer()
    def get(self):
        global mode
        if mode == 1:
            with sr.Microphone() as source:
                audio = self.r.listen(source)
                try:
                    query = self.r.recognize_google(audio, language='vi-VN').lower()
                    print(self.avt2 + str(query))
                    return query
                except Exception as e:
                    query = "none"
                    print(self.avt + "Eula không nhận được lệnh, hãy thử lại nào!")
                    return query
        else:
            query = input(self.avt2)
            return query    
        # except:
        #     pass
        #     query = input(self.avt2)
        #     return query
class NLP:
    def __init__(self):
        with open("vietnamese.txt", "r", encoding="utf-8") as file:
            self.stop_words = [line.strip() for line in file]
    def clear_all(self,text,*word_delete):
        filtered_sentence = []
        word_tokens = word_tokenize(text)
        filtered_sentence = [w for w in word_tokens 
                         if w not in self.stop_words and 
                         w not in word_delete and 
                         re.search('[a-z]', w)]
        if len(filtered_sentence) == 0:
            return ""
        return ' '.join(filtered_sentence)
    
    def clear_word(self, text, *word_delete):
        text_cleared = text # Tạo một bản sao của `text` để thực hiện việc loại bỏ từ
        # for word in word_delete:
        #     text_cleared = text_cleared.replace(word, "") # Loại bỏ từ cần xóa trong `text_cleared`
        # return text_cleared.strip()
        # query_cleared = query.replace('\n', ' ').strip()  # Thay thế cả xuống dòng, tab, space dư thừa bằng khoảng trắng
        for word in word_delete:
            text_cleared = text_cleared.replace(word, "")
            query_cleared = re.sub(fr"\b{word}\b", "", text_cleared)  # Loại bỏ các từ được chỉ định
        query_cleared = re.sub(r"\[\^\d+\^\]", "", query_cleared) 
        return query_cleared.strip()  # Loại bỏ khoảng trắng đầu/chuỗi
    
class bing_response(NLP):
    def __init__(self, cookies_path='bing_cookies_my.json'):
        super().__init__()
        self.bot = Chatbot(cookies_path)

    async def main(self, query):
        response = await self.bot.ask(prompt=query, conversation_style=ConversationStyle.precise)
        for message in response["item"]["messages"]:
            if message["author"] == "bot":
                bot_response = message["text"]
        bot_response = self.clear_word(bot_response , "Xin chào, đây là Bing.", "Tôi có thể hiểu và giao tiếp bằng tiếng Việt." )
        await self.bot.close()
        return bot_response
    def run(self, query):
        loop = asyncio.get_event_loop()
        bot_response = loop.run_until_complete(self.main(query))
        return bot_response

class web:
    # def __init__(self,):
    def open(self,keyword):
        web = f"https://www.{keyword}.com"
        response = requests.get(web)
        if response.status_code == 200:
            webbrowser.open(web)
            return f"Eula đã mở {keyword} cho bạn"
        else:
            return f"Eula phát hiện, mã trạng thái phản hồi không hợp lệ: {response.status_code}"
    def sreach_open(self, keyword, number):
        urls = []
        try:
            for url in search(keyword, num_results=int(number)):
                webbrowser.open_new_tab(url)
                urls.append(url)
            return f"Eula đã tìm :{keyword} trên Google và mở {len(urls)} kết quả trong trình duyệt"
        except:
            return f"Eula không tìm được trang web phù hợp hoặc có lỗi xảy ra"
    

class Seven:
    wake_word = "alo"
    def __init__(self):
        self.Program = Program()
        self.user_command = user_command()
        self.bot_response = bot_response()
        self.bing_response = bing_response()
        self.NLP = NLP()
        self.web = web()
    
    def main(self):
        global mode
        self.bot_response.text_voice(" ----- Eula active ૮ ˶ᵔ ᵕ ᵔ˶ ა ----- ")
        self.Program.run()
        while self.Program.is_running:
            self.bot_response.text("Hãy đánh thức Eula...")
            query = self.user_command.get()           
            if wake_word in query:
                self.bot_response.text_voice("Xin chào, mình là Eula, hãy yêu cầu mình bất cứ điều gì")
                self.CommandExecutor()
            elif "thoát" in query:
                self.bot_response.text("Tạm biệt")
                break
            else:
                self.bot_response.text("Eula không hiểu yêu cầu của bạn, hãy thử lại nhé!")
    def CommandExecutor(self):
        global mode
        while self.Program.is_running:
            self.bot_response.text("Lắng nghe...")
            query = self.user_command.get() 
            if "mở" in query or "tìm" in query:
                query = self.NLP.clear_all(query,"mở")
                try: 
                    self.bot_response.text(self.web.open(query))
                except:
                    self.bot_response.text(self.web.sreach_open(query,1))

            elif "hỏi" in query:
                self.bot_response.text_voice("Eula đã nhận được câu hỏi, câu hỏi đang xử lý!...") 
                query = self.bing_response.run(query)
                self.bot_response.text(query)
            elif "chờ" in query:
                self.bot_response.text("Eula đã vào trạng thái chờ")
                # self.Program.pause()
                break
            elif "kết thúc" in query:
                self.program.stop()
                # self.Program.pause()
                break
            elif "chat" in query:
                mode = 0
                self.bot_response.text("Eula đã vào trạng thái chat")
            elif "giọng nói" in query:
                mode = 1
                self.bot_response.text("Eula đã vào trạng thái giọng nói")
            elif "nhập liệu" in query:
                pass
            else:
                self.bot_response.text("Eula không hiểu yêu cầu của bạn, hãy thử lại nhé!")
        
if __name__ == "__main__":
    friday = Seven()
    friday.main()
