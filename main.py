import os
import openai
import asyncio
import re
import speech_recognition as sr
from EdgeGPT import Chatbot, ConversationStyle
import json
from gtts import gTTS
from playsound import playsound
import os


# Key OpenAI API
openai.api_key = "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"

# Tạo WAKE_WORD
recognizer = sr.Recognizer()
BING_WAKE_WORD = "alo"
GPT_WAKE_WORD = "linh linh"

def get_wake_word(phrase):
    if BING_WAKE_WORD in phrase.lower():
        return BING_WAKE_WORD
    elif GPT_WAKE_WORD in phrase.lower():
        return GPT_WAKE_WORD
    else:
        return None
    
def play_sound(text):
    tts = gTTS(text, lang='vi')
    tts.save('temp.mp3')
    playsound('temp.mp3')
    os.remove('temp.mp3')

async def main():
    while True:

        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            print(f"'lép' hoặc 'linh linh' chọn đi...")
            while True:
                audio = recognizer.listen(source)
                try:
                    with open("audio.wav", "wb") as f:
                        f.write(audio.get_wav_data())
                    # Use the preloaded tiny_model
                    
                    r = sr.Recognizer()
                    # Mở file audio và đọc dữ liệu từ file
                    with sr.AudioFile('audio.wav') as source1:
                        audio_data = r.record(source1)
                    # Nhận dạng giọng nói và xuất ra văn bản
                    text = r.recognize_google(audio_data, language='vi-VN')
                    
                    # print("đã lưu xong1")
                    # # Use the preloaded tiny_model
                    # model = whisper.load_model("tiny")
                    # print("đã lưu xong 2")
                    # result = model.transcribe("audio/audio.wav")
                    # print("đã lưu xong 3")
            
                    
                    phrase = text
                    print(f"Đại vương nói: {phrase}")

                    wake_word = get_wake_word(phrase)
                    if wake_word is not None:
                        break
                    else:
                        print("Em nào vậy cho thử lại...")
                except Exception as e:
                    print("Lỗi nữa gòy Đại vương ưi {0}".format(e))
                    continue
        
            # Chỗ này để giữ nguyên
            print("Nói đi đừng ngại...")
            play_sound('Nói đi đừng ngại')
            audio = recognizer.listen(source)
            try:
                with open("audio.wav", "wb") as f:
                        f.write(audio.get_wav_data())
                with sr.AudioFile('audio.wav') as source2:
                    audio_data = r.record(source2)
                # Nhận dạng giọng nói và xuất ra văn bản
                text = r.recognize_google(audio_data, language='vi-VN')
                user_input = text 
                print(f"Mày nói: {user_input}")
            except Exception as e:
                print("Lỗi nữa gòy: {0}".format(e))
                continue

            if wake_word == BING_WAKE_WORD:
                print("xong 4")
                
                with open("bing_cookies_my.json", "r") as file:
                    cookies = json.load(file)

                # Khởi tạo Chatbot với cookies
                # bot = Chatbot(cookies=cookies)
                bot = Chatbot('bing_cookies_my.json')

                # bot = Chatbot("bing_cookies_my.json")
                # bot = await Chatbot.create()
                print("xong 5")
                response = await bot.ask(prompt=user_input, conversation_style=ConversationStyle.precise)
                
                # Select only the bot response from the response dictionary
                print("xong 6")
                for message in response["item"]["messages"]:
                    if message["author"] == "bot":
                        bot_response = message["text"]
                # Remove [^#^] citations in response
                print("xong 7")
                pattern = r"Xin chào, đây là Bing|\[\^\d+\^\]"
                bot_response = re.sub(pattern, "", bot_response)

            else:
                # Send prompt to GPT-3.5-turbo API
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content":
                        "You are a helpful assistant."},
                        {"role": "user", "content": user_input},
                    ],
                    temperature=0.5,
                    max_tokens=150,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                    n=1,
                    stop=["\nUser:"],
                )

                bot_response = response["choices"][0]["message"]["content"]
                
        print("Phản hồi của bot:", bot_response)
        # print("Lỗi nữa gòy:")
        play_sound(bot_response)
        # play_audio('response2.mp3')
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
