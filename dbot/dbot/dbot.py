import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from discord.utils import get
from discord import FFmpegPCMAudio
import asyncio
import time

bot = commands.Bot(command_prefix='%')

user = []  #유저가 입력한 노래 정보
musictitle = []  #가공된 정보의 노래 제목
song_queue = []  #가공한 정보의 노래 링크
musicnow = []  #현재 출력되는 노래 배열

def title(msg):
    global music
    
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    options = webdriver.ChromeOptions()
    options.add_argument("headless")

    chromedriver_dir = r"C:\Users\jjoon\source\repos\Discord Bot\chromedriver.exe"
    driver = webdriver.Chrome(chromedriver_dir, options = options)
    driver.get("https://www.youtube.com/results?search_query="+msg+"+lyrics")
    source = driver.page_source
    bs = bs4.BeautifulSoup(source, 'lxml')
    entire = bs.find_all('a', {'id': 'video-title'})
    entireNum = entire[0]
    music = entireNum.text.strip()
    
    musictitle.append(music)
    musicnow.append(music)
    test1 = entireNum.get('href')
    url = 'https://www.youtube.com'+test1
    with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
    URL = info['formats'][0]['url']

    driver.quit()
    
    return music, URL

    def play(ctx):
     global vc
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    URL = song_queue[0]
    del user[0]
    del musictitle[0]
    del song_queue[0]
    vc = get(bot.voice_clients, guild=ctx.guild)
    if not vc.is_playing():
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: play_next(ctx)) 

def play_next(ctx):
    if len(musicnow) - len(user) >= 2:
        for i in range(len(musicnow) - len(user) - 1):
            del musicnow[0]
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    if len(user) >= 1:
        if not vc.is_playing():
            del musicnow[0]
            URL = song_queue[0]
            del user[0]
            del musictitle[0]
            del song_queue[0]
            vc.play(discord.FFmpegPCMAudio(URL,**FFMPEG_OPTIONS), after=lambda e: play_next(ctx))

@bot.command()
async def 대기열추가(ctx, *, msg):
    user.append(msg)
    result, URLTEST = title(msg)
    song_queue.append(URLTEST)
    await ctx.send(result + "를 재생목록에 추가했어요!")

@bot.command()
async def 대기열삭제(ctx, *, number):
    try:
        ex = len(musicnow) - len(user)
        del user[int(number) - 1]
        del musictitle[int(number) - 1]
        del song_queue[int(number)-1]
        del musicnow[int(number)-1+ex]
            
        await ctx.send("대기열이 정상적으로 삭제되었습니다.")
    except:
        if len(list) == 0:
            await ctx.send("대기열에 노래가 없어 삭제할 수 없어요!")
        else:
            if len(list) < int(number):
                await ctx.send("숫자의 범위가 목록개수를 벗어났습니다!")
            else:
                await ctx.send("숫자를 입력해주세요!")

@bot.command()
async def 목록(ctx):
    if len(musictitle) == 0:
        await ctx.send("아직 아무노래도 등록하지 않았어요.")
    else:
        global Text
        Text = ""
        for i in range(len(musictitle)):
            Text = Text + "\n" + str(i + 1) + ". " + str(musictitle[i])
            
        await ctx.send(embed = discord.Embed(title= "노래목록", description = Text.strip(), color = 0x00ff00))

@bot.command()
async def 목록초기화(ctx):
    try:
        ex = len(musicnow) - len(user)
        del user[:]
        del musictitle[:]
        del song_queue[:]
        while True:
            try:
                del musicnow[ex]
            except:
                break
        await ctx.send(embed = discord.Embed(title= "목록초기화", description = """목록이 정상적으로 초기화되었습니다. 이제 노래를 등록해볼까요?""", color = 0x00ff00))
    except:
        await ctx.send("아직 아무노래도 등록하지 않았어요.")

@bot.command()
async def 목록재생(ctx):

    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    
    if len(user) == 0:
        await ctx.send("아직 아무노래도 등록하지 않았어요.")
    else:
        if len(musicnow) - len(user) >= 1:
            for i in range(len(musicnow) - len(user)):
                del musicnow[0]
        if not vc.is_playing():
            play(ctx)
        else:
            await ctx.send("노래가 이미 재생되고 있어요!")



#봇이 사용자의 서버에 접속하게 해주는 코드
@bot.event
async def on_ready():
    print('다음으로 로그인합니다: ')
    print(bot.user.name)
    print('connection was succesful')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("넓은 바다를 탐색"))


#봇의 출입을 결정하는 코드
@bot.command()
async def 들어와(ctx):
    try:
           global vc
           vc = await ctx.message.author.voice.channel.connect()
    except:
        try:
            await vc.move_to(ctx.message.author.voice.channel)
        except:
            await ctx.send("나 혼자 놀라고?")

@bot.command()
async def 나가(ctx):
    try:
        await vc.disconnect()
    except:
        await ctx.send("나 거기 없지롱~")

#유튜브에서 URL로 노래 다운후 재생하는 코드
@bot.command()
async def URL재생(ctx, *, url):
    YDL_OPTIONS = {'format': 'bestaudio','noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    if not vc.is_playing():
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        await ctx.send(embed = discord.Embed(title= "노래 재생", description = "현재 " + url + "을(를) 재생하고 있습니다.", color = 0x00ff00))
    else:
        await ctx.send("이미 듣고 있잖아 ㅋㅋ")



#재생 명령어를 만드는 코드입니다!
@bot.command()
async def 재생(ctx, *, msg):
    if not vc.is_playing():

         options = webdriver.ChromeOptions()      #노래 재생시 원래 나오는 크롬 창을 제거해주는 코드
         options.add_argument("headless")


         global entireText
         #밑의 두줄은 ffmpeg와 youtube_dl의 기본설정
         YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
         FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            
         #chromdriver와 셀리니움을 활용하여 유튜브에서 영상 제목과 링크 등을 가져오는 코드
         chromedriver_dir = r"C:\Users\jjoon\source\repos\Discord Bot\chromedriver.exe"
         driver = webdriver.Chrome(chromedriver_dir, options = options)
         driver.get("https://www.youtube.com/results?search_query="+msg+"+lyrics")
         source = driver.page_source
         bs = bs4.BeautifulSoup(source, 'lxml')
         entire = bs.find_all('a', {'id': 'video-title'})
         entireNum = entire[0]
         entireText = entireNum.text.strip()
         musicurl = entireNum.get('href')
         url = 'https://www.youtube.com'+musicurl 

         driver.quit()                                            #노래 재생시 원래 나오는 크롬 창을 제거해주는 코드2

         musicnow.insert(0, entireText)

         #URL재생과 마찬가지로 음악을 재생하는 코드, 검색을 한다는 점에서 URL 재생과는 차이가 있다
         with YoutubeDL(YDL_OPTIONS) as ydl:
             info = ydl.extract_info(url, download=False)
         URL = info['formats'][0]['url']
         await ctx.send(embed = discord.Embed(title= "노래 재생", description = "현재 " + musicnow[0] + "을(를) 재생하고 있습니다.", color = 0x00ff00))
         vc.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e:play_next(ctx))
    else:
         await ctx.send("미안 내가 멀티테스킹이 좀 어려워...")

#일시정지 다시재생 만드는 코드
@bot.command()
async def 일시정지(ctx):
    if vc.is_playing():
        vc.pause()
        await ctx.send(embed = discord.Embed(title= "일시정지", description = musicnow[0] + "을(를) 일시정지 했습니다.", color = 0x00ff00))
    else:
        await ctx.send("우리 노래는 틀어놓고 끄라고 부탁하자?")

@bot.command()
async def 다시재생(ctx):
    try:
        vc.resume()
    except:
         await ctx.send("일단 노래부터 틀어")
    else:
         await ctx.send(embed = discord.Embed(title= "다시재생", description = musicnow[0]  + "을(를) 다시 재생했습니다.", color = 0x00ff00))

@bot.command()
async def 노래끄기(ctx):
    if vc.is_playing():
        vc.stop()
        await ctx.send(embed = discord.Embed(title= "노래끄기", description = musicnow[0]  + "을(를) 종료했습니다.", color = 0x00ff00))
    else:
        await ctx.send("노래를 틀어야 끄지 ㅋㅋㅋ")

#현재 나오는 노래를 알려주는 코드
@bot.command()
async def 지금노래(ctx):
    if not vc.is_playing():
        await ctx.send("뭔 노래가 궁금하단거야")
    else:
        await ctx.send(embed = discord.Embed(title = "지금노래", description = "현재 " + musicnow[0] + "을(를) 재생하고 있습니다.", color = 0x00ff00))



bot.run('ODkzMTA2Mzk5NDQ0MzYxMjI3.YVWoJg.cwhGFRYqguCnatYbUTPmjbCfwvQ')


