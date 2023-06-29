import os
import re
import asyncio
import webbrowser
import requests
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
from bs4 import BeautifulSoup
from underthesea import word_tokenize
from googlesearch import search

from EdgeGPT import Chatbot, ConversationStyle


#Pls copy your cookies bing.com web over "bing_cookies_your.json"
#You can use this extension in Google Chrome: "https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg?hl=eng" to copy cookies after you have already accessed Bing.com 

#Hãy copy cookies trang web bing.com của bạn vào "bing_cookies_your.json"
#Bạn có thể dùng extension trong Google Chrome: "https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg?hl=eng"để copy cookies khi đã truy cập vào Bing.com

cookies_path='bing_cookies_my.json'

wake_word = "seven"
      
class user_command:
    def __init__(self):
        self.r = sr.Recognizer()
    def get(self):
        try:
            with sr.Microphone() as source:
                audio = self.r.listen(source)
                try:
                    query = self.r.recognize_google(audio, language='vi-VN').lower()
                    print(f"- Đại zương nói: {query}" )
                    return query
                except Exception as e:
                    return "Hệ thống: Lỗi gòy, thử lại đại zương ơi..."
        except:
            query = input("Nhận lệnh: ")
            return query

class bot_response:
    def voice(self,query):
        tts = gTTS(query, lang='vi')
        tts.save('temp.mp3')
        playsound('temp.mp3')
        os.remove('temp.mp3')
    def text(self,query):
        print("Hệ thống: " + str(query))
    def text_voice(self,query):
        self.text(query)
        self.voice(query)
   
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
        for word in word_delete:
            text_cleared = text_cleared.replace(word, "") # Loại bỏ từ cần xóa trong `text_cleared`
        return text_cleared.strip()
        # query_cleared = query.replace('\n', ' ').strip()  # Thay thế cả xuống dòng, tab, space dư thừa bằng khoảng trắng
        for word in word_delete:
            query_cleared = re.sub(fr"\b{word}\b", "", text2_cleared)  # Loại bỏ các từ được chỉ định
        query_cleared = re.sub(r"\[\^\d+\^\]", "", query_cleared) 
        return query_cleared.strip()  # Loại bỏ khoảng trắng đầu/chuỗi
    
class bing_response:
    def __init__(self, cookies_path='bing_cookies_my.json'):
        self.bot = Chatbot(cookies_path)

    async def main(self, query):
        response = await self.bot.ask(prompt=query, conversation_style=ConversationStyle.precise)
        for message in response["item"]["messages"]:
            if message["author"] == "bot":
                bot_response = message["text"]

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
            return f"Tôi đã mở {keyword} cho bạn"
        else:
            return f"Mã trạng thái phản hồi không hợp lệ: {response.status_code}"
    def sreach(self,keyword,number):
        urls = []
        for url in search(keyword, num_results = int(number)):
            try:
                webbrowser.open_new_tab(url)
                urls.append(url)
                print(urls)
                return f"Tôi sẽ thử tìm {keyword} trên google"
            except:
                return f"Không tìm được trang web phù hợp"
    


class Seven:
    wake_word = "dậy"
    def __init__(self, ):
        self.user_command = user_command()
        self.bot_response = bot_response()
        self.bing_response = bing_response()
        self.NLP = NLP()
        self.web = web()
    def main(self):
        self.bot_response.text("\n\n ----- March 7th active ----- \n")
        while True:
            self.bot_response.text("Lắng nghe...")
            query = self.user_command.get()           
            if wake_word in query:
                self.bot_response.text("Xin chào, Tôi là March 7th, trợ lý ảo cá nhân, Nói đi đừng ngại")
                while True:
                    query = self.user_command.get() 
                    if "mở" in query or "tìm" in query:
                        query = self.NLP.clear_all(query,"mở")
                        try: 
                            self.bot_response.text_voice(self.web.open(query))
                        except:
                            self.bot_response.text_voice(self.web.sreach(query,1))
                    elif "chờ" in query:
                        query = self.NLP.clear_all(query,"mở")   
                    elif "hỏi" in query:
                        self.bot_response.text("Câu hỏi đang xử lý...") 
                        new_query = self.bing_response.run(query)
                        query = self.NLP.clear_word(new_query, "Xin chào, đây là Bing." , "Tôi có thể hiểu và giao tiếp bằng tiếng Việt." )
                        self.bot_response.text_voice(query)
   
                    elif "chờ" in query:
                        self.bot_response.text("Trạng thái chờ")
                        break
                    else:
                        self.bot_response.text("Hệ thống: Không thể nhận diện lệnh, thử lại đại zương ơi")
            elif "dừng lại" in query:
                self.bot_response.text_voice("Tạm biệt")
                break
            else:
                print("Hệ thống: Không thể nhận diện lệnh, thử lại đại zương ơi")

if __name__ == "__main__":
    friday = Seven()
    friday.main()
