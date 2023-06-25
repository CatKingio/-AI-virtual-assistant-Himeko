import os
import openai
import asyncio
import re
import speech_recognition as sr
from EdgeGPT import Chatbot, ConversationStyle
from gtts import gTTS
from playsound import playsound
import os
import webbrowser
import requests
from bs4 import BeautifulSoup
import pandas as pd
from underthesea import word_tokenize
from googlesearch import search


wake_word = "dậy"

#Pls copy your cookies bing.com web over here
#You can use this extension in Google Chrome: "https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg?hl=eng" to copy cookies after you have already accessed Bing.com 

#Hãy copy cookies trang web bing.com của bạn vào đây
#Bạn có thể dùng extension trong Google Chrome: "https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg?hl=eng"để copy cookies khi đã truy cập vào Bing.com

bot = Chatbot('bing_cookies_your.json') 

r = sr.Recognizer()
def getcommand():
    with sr.Microphone() as source:
        print("Hệ thống: Lắng nghe...")
        audio =r.listen(source)
        try:
            query = (r.recognize_google(audio, language='vi-VN')).lower()
            print(f"- Đại zương nói: {query}" )
            return query
        except Exception as e:
            return "Hệ thống: Lỗi gòy, thử lại đại zương ơi..."
        
def play_sound(text):
    tts = gTTS(text, lang='vi')
    tts.save('temp.mp3')
    playsound('temp.mp3')
    os.remove('temp.mp3')
    
def bot_respone(text):
    print("Hệ thống: " + str(text))
    play_sound(text)
    
    
with open("vietnamese.txt" , encoding="utf-8") as file:
    stopwords = file.readlines()
stop_words = [x[:-1] for x in stopwords]

def delete_stopword(text,*word_delete):
    if word_delete is None:
        word_delete = ()
    word_tokens = word_tokenize(text)
    #stop_words.append('object')
    filtered_sentence = []
    for w in word_tokens:
        if w not in stop_words and w not in word_delete:
            filtered_sentence.append(w) 
            
    query = " ".join([w for w in filtered_sentence if re.search('[a-z]', w)])
    return query

def delete_word(query,*word_delete):
    for word in word_delete:
        query = query.replace(word, "")
    query = re.sub(r"\[\^\d+\^\]", "", query) 
    return query 

def search_and_open(keyword,number):
    urls = []
    for url in search(keyword, num_results = int(number)):
        webbrowser.open_new_tab(url)
        urls.append(url)
        print(urls)
    return urls
# results = search_and_open("how to learn programming")


async def main():
    while True:
        query = getcommand()
        if wake_word in query:
            bot_respone("Xin chào, Tôi là Friday, trợ lý ảo cá nhân, Nói đi đừng ngại")
            # print("zô")
            while True:
                query = getcommand()
                if "mở" in query or "tìm" in query:
                    query = delete_stopword(query,"mở")
                    web = f"https://www.{query}.com"
                    try:
                        response = requests.get(web)
                        if response.status_code == 200:
                            webbrowser.open(web)
                            print(f"Hệ thống: Trang web {web} đang hoạt động")
                            bot_respone(f"Tôi đã mở {query} cho bạn")
                        else:
                            print(f"Mã trạng thái phản hồi không hợp lệ: {response.status_code}")
                    except:
                        # print(f"Hệ thống: Không thể kết nối đến trang web {query}")
                        bot_respone(f"Tôi sẽ thử tìm {query} trên google")
                        search_and_open(query,1)
                        continue
                        
                elif "hỏi" in query:
                    bot_respone("Câu hỏi của bạn đang được xử lý...")    
                    try:
                        response = await bot.ask(prompt=query, conversation_style=ConversationStyle.precise)
                        for message in response["item"]["messages"]:
                            if message["author"] == "bot":
                                query = message["text"]
                        query = delete_word(query, "Xin chào, đây là Bing." , "Tôi có thể hiểu và giao tiếp bằng tiếng Việt.")
                        bot_respone(query)
                        await bot.close()
                        continue
                        
                    except:
                        return "Hệ thống: Lỗi gòy, thử lại đại zương ơi..."
                elif "dừng lại" in query:
                    bot_respone("Tạm biệt")
                    break
                else:
                    print("Hệ thống: Không thể nhận diện lệnh, thử lại đại zương ơi")
        elif "dừng lại" in query:
            text="Tạm biệt"
            print("Hệ thống:" + str(text))
            play_sound(text)
            break
        else:
            print("Hệ thống: Không thể nhận diện lệnh, thử lại đại zương ơi")
        
       









if __name__ == "__main__":
    print("//////////////// Trợ lý ảo Bé Bảy đã khởi động \\\\\\\\\\\\\\\\\\\\")
    asyncio.run(main())  