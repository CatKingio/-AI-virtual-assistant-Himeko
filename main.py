import os
import re
import json
import threading
import asyncio
import webbrowser
import requests

from colorama import Fore, Style

import speech_recognition as sr
from gtts import gTTS
from playsound import playsound

from unidecode import unidecode
from underthesea import word_tokenize
from pyvi import ViUtils
from googlesearch import search

import torch.nn as nn
import torch
from model import SimpleTransformer

from bs4 import BeautifulSoup
from EdgeGPT import Chatbot, ConversationStyle



#Pls copy your cookies bing.com web over "bing_cookies_your.json"
#You can use this extension in Google Chrome: "https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg?hl=eng" to copy cookies after you have already accessed Bing.com 

#Hãy copy cookies trang web bing.com của bạn vào "bing_cookies_your.json"
#Bạn có thể dùng extension trong Google Chrome: "https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg?hl=eng"để copy cookies khi đã truy cập vào Bing.com

cookies_path='bing_cookies_my.json'
mode = 0
wake_word = "alo"
bot_name = "Himeko"


def load_model_weights(model, filepath):
    model.load_state_dict(torch.load(filepath))
    model.eval()
# Load model weights
loaded_model = SimpleTransformer()
load_model_weights(loaded_model, 'simple_transformer_weights2.pth')
def load_data_from_json(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data
word_to_index = load_data_from_json('word_to_index.json')

def checkdaucau(text):
    normalized_text = unidecode(text)
    return normalized_text != text
def themdaucau(text):
    check = checkdaucau(text)
    if check == False:
        try:
            sentence = ViUtils.add_accents(text).lower()       
        except:
            sentence = text  
    else:
        sentence = text  
    return sentence
def clean_text(text):
    return  re.sub(r'[^\w\s]', ' ', text.lower(), flags=re.UNICODE)
def preprocess_input(input_ids, max_sequence_length=9):
    if len(input_ids) < max_sequence_length:
        padded_input_ids = torch.cat([input_ids, torch.zeros((max_sequence_length - len(input_ids),))])
        processed_input_ids = padded_input_ids.unsqueeze(0) 
    elif len(input_ids) > max_sequence_length:
        processed_input_ids = input_ids[:max_sequence_length].unsqueeze(0)  
    else:
        processed_input_ids = input_ids.unsqueeze(0) 
    
    return processed_input_ids.int() 
def text_to_ids(text, word_to_id_dict = word_to_index):
    pattern1= themdaucau(text)
    pattern2 = clean_text(pattern1)
    # normalized_text = TextNormalization.normalize(pattern)
    words = word_tokenize(pattern2)
    ids = [word_to_id_dict.get(word, -1) for word in words]  # Map words to IDs using the dictionary
    return [id for id in ids if id != -1] 
# Inference function for single input
def predict_single_input(input_ids, model):
    with torch.no_grad():
        logits = model(input_ids)
        predicted_label = torch.argmax(logits).item()
        return predicted_label


def dudoanlabel(text):
    result = text_to_ids(text)
    test_input_ids = torch.tensor(result) 
    processed_input_ids = preprocess_input(test_input_ids)
    predicted_label = predict_single_input(processed_input_ids, loaded_model)
    return predicted_label


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
        self.avt= Fore.MAGENTA + f"\n   /)⑅/) \n꒰˶• ༝•˶꒱\n./づ~ ♡ {bot_name}: " + Style.RESET_ALL
        self.avt2 =Fore.GREEN + f"\n  (\ (\ \n(„• ֊ •„) ♡\n━O━O━━━━━ Bạn: " + Style.RESET_ALL
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
                    print(self.avt + f"{bot_name} không nhận được lệnh, hãy thử lại nào!")
                    return query
        else:
            query = input(self.avt2)
            return query    
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
            text_cleared = text_cleared.replace(word, "")
            query_cleared = re.sub(fr"\b{word}\b", "", text_cleared)  # Loại bỏ các từ được chỉ định
        query_cleared = re.sub(r"\[\^\d+\^\]", "", query_cleared) 
        return query_cleared.strip()  # Loại bỏ khoảng trắng đầu/chuỗi
    
class bing_response(NLP):
    def __init__(self, cookies_path='bing_cookies_my.json'):
        super().__init__()
        self.bot = Chatbot(cookies_path)
            
    async def main(self, query):
        try:
            response = await self.bot.ask(prompt=query, conversation_style=ConversationStyle.precise)
            for message in response["item"]["messages"]:
                if message["author"] == "bot":
                    bot_response = message["text"]
            bot_response = self.clear_word(bot_response , "Xin chào, đây là Bing.", "Tôi có thể hiểu và giao tiếp bằng tiếng Việt." )
            await self.bot.close()
            return bot_response
        except:
             return "Lỗi truy cập"
    def run(self, query):
        loop = asyncio.get_event_loop()
        bot_response = loop.run_until_complete(self.main(query))
        return bot_response

class web:
    # def __init__(self,):
    def open(self,keyword):
        web = f"https://www.{keyword}.com"
        response = requests.get(web)
        webbrowser.open(web)
        return f"{bot_name} đã mở {keyword} cho bạn"  
    def sreach_open(self,keyword, num_results=2):
        search_results = list(search(keyword, num_results=num_results))
        
        for index, result in enumerate(search_results, start=1):
            webbrowser.open_new_tab(result)
            print(f"/n Đã mở trang {index}: {result}")
        return bot_name + f"{bot_name} đã tìm :{keyword} trên Google"

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
        self.bot_response.text(f" ----- {bot_name} active ૮ ˶ᵔ ᵕ ᵔ˶ ა ----- ")
        self.Program.run()
        while self.Program.is_running:
            self.bot_response.text_voice(f"Hãy đánh thức {bot_name}...")
            query = self.user_command.get()   
            label = dudoanlabel(query)        
            if label == 0:
                self.bot_response.text(f"Xin chào, mình là {bot_name}, hãy yêu cầu mình bất cứ điều gì")
                self.CommandExecutor()
            elif label == 1:
                self.bot_response.text("Tạm biệt")
                break
            else:
                self.bot_response.text(f"{bot_name} không hiểu yêu cầu của bạn, hãy thử lại nhé!")
    def CommandExecutor(self):
        global mode
        while self.Program.is_running:
            self.bot_response.text("Lắng nghe...")
            query = self.user_command.get() 

            label = dudoanlabel(query)
            if label == 3 :
                query = self.NLP.clear_all(query,"mở")
                try: 
                    self.bot_response.text(self.web.open(query))                   
                except:
                    self.bot_response.text(self.web.sreach_open(query))

            elif label == 2 :
                self.bot_response.text(f"{bot_name} đã nhận được câu hỏi, câu hỏi đang xử lý!...") 
                query = self.bing_response.run(query)
                self.bot_response.text(query)
            elif label == 1:
                self.Program.stop()
                # self.Program.pause()
                break
            elif label == 5:
                mode = 0
                self.bot_response.text(f"{bot_name} đã vào trạng thái chat")
            elif label == 4:
                mode = 1
                self.bot_response.text(f"{bot_name} đã vào trạng thái giọng nói")
            elif label == 6:
                pass
            else:
                self.bot_response.text(f"{bot_name} không hiểu yêu cầu của bạn, hãy thử lại nhé!")
        
if __name__ == "__main__":
    friday = Seven()
    friday.main()