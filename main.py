import asyncio
import os
import discord
import shortuuid as shortuuid
from dotenv import load_dotenv
import datetime
import re
import sqlite3
import json
import requests

s = requests.Session()

intents = discord.Intents.all()
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
loginfo = os.getenv('login')
APISecret = os.getenv('APISecret')
client = discord.Client(intents=intents)
sqlite_file = 'TicketLogs.db'

conn = sqlite3.connect(sqlite_file)
c = conn.cursor()


@client.event
async def on_ready():
    global channelsend, logchannel, statchannel
    for guild in client.guilds:
        print(
            f'{client.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )

    channelsend = client.get_channel(781295076390731807)
    logchannel = [client.get_channel(739608559175729232), client.get_channel(740337206354509911)]
    statchannel = client.get_channel(824429053284843570)


allowedformats = ['mp4', 'mov', 'webm']
reportchannelid = 781295076390731807
staffroleid = 736560592722067518
gamereportroleid = 833823937489534976
reportchannelsid = [824447905343078410, 824447928512937994, 824447944085340160]
formatguide = [".report", "offender", "offence", "your class", "offender's class", "context", "evidence"]
formatguide2 = [".report offender", "offence", "your class", "offender's class", "context", "evidence"]
channelstats = [0, 0, 0]
approvedusers = [415158701331185673, 157961125915394048, 332771985853513729]
ingamereportchannels = [819248574323884072, 819251918160920586]


async def purgereports():
    while True:
        for b in range(len(reportchannelsid)):
            async for message in client.get_channel(reportchannelsid[b]).history(limit=1000):
                if not message.pinned:
                    await message.delete()
        print("purged")
        c.execute("SELECT * FROM Ticketlogs")
        rows = c.fetchall()
        await client.change_presence(activity=discord.Game(name=("Logged " + str(len(rows)) + " reports")))
        last_date_time = str(datetime.datetime.now() - datetime.timedelta(hours=24))[:-7]
        last_date_time = datetime.datetime.strptime(last_date_time, '%Y-%m-%d %H:%M:%S')
        print(last_date_time)
        for row in rows:
            if (datetime.datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S')) >= last_date_time:
                for i in range(len(reportchannelsid)):
                    if str(row[3]) == client.get_channel(reportchannelsid[i]).name:
                        channelstats[i] += 1
        embed = discord.Embed(title='Report Statistics')
        for i in range(len(reportchannelsid)):
            embed.add_field(
                name=('Number of reports from the last 24h in ' + client.get_channel(reportchannelsid[i]).name),
                value=str(channelstats[i]), inline=False)
            channelstats[i] = 0
        await statchannel.send(embed=embed)
        await asyncio.sleep(86400)


async def dbexit():
    c.close()
    print("disconnected")


async def dbconnect():
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()


async def dbtoday(message3):
    global statchannel
    print("attempting")
    msglist = message3.content.lower().split()
    c.execute("SELECT * FROM Ticketlogs")
    rows = c.fetchall()
    try:
        tomp3 = msglist[1]
    except:
        tomp3 = ""
    if tomp3 == "":
        last_date_time = str(datetime.datetime.now().date()) + " 00:00:00"
        print(str(datetime.datetime.now().date()))
        last_date_time = datetime.datetime.strptime(last_date_time, '%Y-%m-%d %H:%M:%S')
        print(last_date_time)
        for row in rows:
            if (datetime.datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S')) >= last_date_time:
                for i in range(len(reportchannelsid)):
                    if str(row[3]) == client.get_channel(reportchannelsid[i]).name:
                        channelstats[i] += 1
        embed = discord.Embed(title='Report Statistics')
        for i in range(len(reportchannelsid)):
            embed.add_field(name=('Number of reports today in ' + client.get_channel(reportchannelsid[i]).name),
                            value=str(channelstats[i]), inline=False)
            channelstats[i] = 0
    else:
        print(tomp3)
        print(tomp3.strip())
        last_date_time = str(tomp3).strip() + " 00:00:00"
        last_date_time2 = str(tomp3).strip() + " 23:59:59"
        try:
            last_date_time3 = datetime.datetime.strptime(last_date_time, '%Y-%m-%d %H:%M:%S')
            last_date_time4 = datetime.datetime.strptime(last_date_time2, '%Y-%m-%d %H:%M:%S')
            print(last_date_time)
            print(last_date_time2)
            for row in rows:
                if last_date_time4 >= (datetime.datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S')) >= last_date_time3:
                    for i in range(len(reportchannelsid)):
                        if str(row[3]) == client.get_channel(reportchannelsid[i]).name:
                            channelstats[i] += 1
            embed = discord.Embed(title='Report Statistics')
            for i in range(len(reportchannelsid)):
                embed.add_field(
                    name=('Number of reports on ' + str(tomp3) + ' in ' + client.get_channel(reportchannelsid[i]).name),
                    value=str(channelstats[i]), inline=False)
                channelstats[i] = 0
        except:
            embed = discord.Embed(title='Incorect Statistics Format')
            embed.add_field(name="Please send dates in a YYYY-MM-DD format", value="Example: .stats 2021-03-24")
    await statchannel.send(embed=embed)


@client.event
async def on_message(message):
    global found, link, channelsend, logchannel
    tosend = ""
    if message.author == client.user:
        return

    if str(message.content).lower().startswith(".report"):
        doit = False
        if str(message.content).lower().strip() == ".report":
            embed = discord.Embed(title='How to report')
            embed.add_field(name="Format",
                            value=(""".report Offender's IGN:
Offence:
Your Class:
Offender's Class:
Context:
Evidence:"""),
                            inline=False)
            embed.set_footer(icon_url=r'https://images-ext-1.discordapp.net/external'
                                      r'/ULH3rEZ2h73MO7tcigZ6vJsYRBBmDP4ywDsA6b1p8OY/https/cdn.discordapp.com/icons'
                                      r'/611313544780316722/a_57a86574127aa12d76d876f462432a6d.webp', text=("The Coop "
                                                                                                            "Community ( "
                                                                                                            "Facility "
                                                                                                            "Home) • "
                                                                                                            "" + str(
                datetime.datetime.now())[:-7]))
            await message.channel.send(embed=embed)
            await message.delete()
            return

        if message.channel.id in reportchannelsid:
            doit = True
        if not doit:
            return
        await message.add_reaction('👍')
        m = False
        n = False
        m2 = False
        tkbans = [15, 1440, 26280000]
        racismbans = [1440, 26280000]
        kosbans = [5, 30, 1440, 26280000]
        toxicitybans = [1, 1440, 26280000]
        bantimelist = [tkbans, racismbans, kosbans, toxicitybans]
        bannames = ["TK", "Racism", "KOS", "Toxicity"]
        bantimenum = [3, 2, 4, 3]
        banmessage = ""
        readoffence = ""
        messagelist = str(message.content).lower().splitlines()
        timeofreport = str(datetime.datetime.now())[:-7]
        channelname = str(message.channel.name)
        mauthorid = str(message.author.id)
        checker = 0
        for i in range(len(messagelist)):
            if len(messagelist) == 7:
                if messagelist[i].startswith(formatguide[i]):
                    checker += 1
            elif len(messagelist) == 6:
                if messagelist[i].startswith(formatguide2[i]):
                    checker += 1
        if checker != len(messagelist):
            embed = discord.Embed(title='Please use the correct format next time')
            embed.add_field(name="Format",
                            value=(""".report Offender's IGN:
                    Offence:
                    Your Class:
                    Offender's Class:
                    Context:
                    Evidence:"""),
                            inline=False)
            embed.set_footer(icon_url=r'https://images-ext-1.discordapp.net/external'
                                      r'/ULH3rEZ2h73MO7tcigZ6vJsYRBBmDP4ywDsA6b1p8OY/https/cdn.discordapp.com/icons'
                                      r'/611313544780316722/a_57a86574127aa12d76d876f462432a6d.webp', text=("The Coop "
                                                                                                            "Community ("
                                                                                                            "Facility "
                                                                                                            "Home) • "
                                                                                                            "" + timeofreport))
            await message.channel.send(embed=embed)
        messageline = messagelist[0].lower()
        if messageline.rstrip() == ".report":
            messageline = messagelist[1].lower()
        messageline = messageline.replace(".report", "")
        messageline = messageline.replace("offender", "")
        messageline = messageline.replace("'s", "")
        messageline = messageline.replace("ign", "")
        messageline = messageline.replace(":", "").lstrip()
        messageline = " " + messageline.rstrip()

        print(messageline)
        if messageline.strip() != "":
            for i in range(len(logchannel)):
                messages = await logchannel[i].history(limit=500).flatten()
                for msg in messages:
                    msglines = msg.content.lower().splitlines()
                    for qs in range(len(msglines)):
                        if messageline in msglines[qs]:
                            print("found")
                            print(messageline)
                            print(msglines[qs])
                            word_to_search = str(str(messageline) + " (")
                            try:
                                start = int(msglines[qs].rindex(word_to_search)) + len(word_to_search)
                            except Exception as e:
                                print(e)
                                print("failed to find, MAJOR ERROR")
                                break
                            print(start)
                            found = msglines[qs][start:(start + 23)]
                            link = msg.jump_url
                            m = True

                            headers = {
                                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'}
                            cookies = s.cookies.get_dict()
                            tosenddata = {'APISecret': APISecret, 'SearchType': 0, 'SearchValue': str(found)}
                            try:
                                response = s.post('https://api.pmf2.scpfacility.uk/banSearch.php',
                                                  headers=headers, data=tosenddata, cookies=cookies,
                                                  allow_redirects=True, verify=False)
                            except Exception as e:
                                print(e)
                                print("MAJOR FAIL")
                                break
                            print(response.text)
                            print(response.status_code)
                            haystack = json.loads(response.text)
                            offences = []
                            try:
                                for ban in haystack['Bans']:
                                    offences.append(ban["Offence"])
                            except:
                                print("no bans")
                            tk = False
                            racism = False
                            kos = False
                            toxicity = False
                            if len(offences) != 0:
                                m2 = True
                                for po in range(len(offences)):
                                    susoffence = offences[po].lower()
                                    if 'tk' in susoffence or 'teamkill' in susoffence or 'team kill' in susoffence:
                                        tk = True
                                    if 'racism' in susoffence or 'racist' in susoffence or 'n word' in susoffence or 'n-word' in susoffence:
                                        racism = True
                                    if 'kos' in susoffence:
                                        kos = True
                                    if 'mic' in susoffence or 'spam' in susoffence:
                                        toxicity = True
                                    listcalc = [tk, racism, kos, toxicity]
                                    for j in range(len(listcalc)):
                                        if listcalc[j] == True:
                                            bantimelist[j].pop(0)
                                            if len(bantimelist[j]) == 0:
                                                bantimelist[j].append(26280000)
                                for poo in range(len(offences)):
                                    readoffence += offences[::-1][poo] + "\n"
                            try:
                                messageline2 = messagelist[1].lower()
                            except:
                                break
                            if messagelist[0].rstrip().lower() == ".report":
                                messageline2 = messagelist[2].lower()
                            messageline2 = messageline2.replace("offence", "")
                            messageline2 = messageline2.replace(":", "")
                            susoffence = messageline2.strip()
                            mass = False
                            tk = False
                            racism = False
                            kos = False
                            toxicity = False
                            if 'mass' in susoffence:
                                mass = True
                            if 'tk' in susoffence or 'teamkill' in susoffence or 'team kill' in susoffence:
                                tk = True
                            if 'racism' in susoffence or 'racist' in susoffence:
                                racism = True
                            if 'kos' in susoffence:
                                kos = True
                            if 'mic' in susoffence or 'spam' in susoffence:
                                toxicity = True
                            listcalc = [tk, racism, kos, toxicity]
                            tobantime = 0
                            reasons = ""
                            for po in range(len(listcalc)):
                                if listcalc[po] == True:
                                    tobantime += bantimelist[po][0]
                                    if reasons == "":
                                        reasons += bannames[po]
                                    else:
                                        reasons += (", " + bannames[po])
                            if reasons == "":
                                break
                            if mass:
                                tobantime = tobantime * 2
                                reasons = "Mass " + reasons
                            banmessage = "ban ID " + str(tobantime) + " " + str(reasons) + " (" + str(
                                tobantime) + " minutes) - See the discord for more information"
                            n = True

                            break
                    else:
                        continue
                    break
                else:
                    continue
                break
        reportid = shortuuid.ShortUUID().random(length=22)
        embed = discord.Embed(title=('New Report from ' + str(message.author.name)), colour=0xe74c3c)
        embed.add_field(name="Reported by", value=("<@!" + str(message.author.id) + "> - ID:" + str(message.author.id)),
                        inline=True)
        embed.add_field(name="Channel", value=(str(message.channel.mention)),
                        inline=True)
        embed.add_field(name='Report Content:', value=str(message.content)[7:].lstrip(), inline=False)
        if m:
            embed.add_field(name='Suspected offender:', value=(str(found) + "\n" + link), inline=False)
        if m2:
            embed.add_field(name='Suspected offender bans:', value=readoffence, inline=False)
        if n:
            embed.add_field(name='Suspected ban command:', value=str(banmessage), inline=False)
        embed.add_field(name='Report ID', value=("`" + str(reportid) + "`"))
        embed.set_footer(icon_url=r'https://images-ext-1.discordapp.net/external'
                                  r'/ULH3rEZ2h73MO7tcigZ6vJsYRBBmDP4ywDsA6b1p8OY/https/cdn.discordapp.com/icons'
                                  r'/611313544780316722/a_57a86574127aa12d76d876f462432a6d.webp', text=("The Coop "
                                                                                                        "Community ("
                                                                                                        "Facility "
                                                                                                        "Home) • "
                                                                                                        "" + timeofreport))
        file = None
        if message.attachments:
            for i in range(len(allowedformats)):
                if allowedformats[i] in message.attachments[0].url:
                    attachmentpath = os.path.join("files/" + message.attachments[0].filename)
                    await message.attachments[0].save(attachmentpath)
                    if os.path.getsize(attachmentpath) > 8388119:
                        tosend = str(message.attachments[0].url)
                    else:
                        await message.attachments[0].save(attachmentpath)
                        file = discord.File(str(attachmentpath), filename=message.attachments[0].filename)
                    break
                else:
                    attachmentpath = os.path.join("files/" + message.attachments[0].filename)
                    await message.attachments[0].save(attachmentpath)
                    file = discord.File(str(attachmentpath), filename=message.attachments[0].filename)
                    embed.set_image(url=str('attachment://' + str(message.attachments[0].filename)))

        try:
            if file:
                await channelsend.send(("<@&" + str(staffroleid) + ">").format(discord.role.Role.mention), file=file,
                                       embed=embed)
            else:
                await channelsend.send(("<@&" + str(staffroleid) + ">").format(discord.role.Role.mention), embed=embed)

            if len(tosend) > 0:
                await channelsend.send(tosend)
                await asyncio.sleep(5)
        except:
            await message.channel.send("Please send a valid report using the format")

        try:
            await message.delete()
        except:
            print("fail lol")
        embed = discord.Embed(title="Report", description="Thank you for logging a report")
        embed.add_field(name='Report ID', value=("`" + str(reportid) + "`"))
        embed.set_footer(icon_url=r'https://images-ext-1.discordapp.net/external'
                                  r'/ULH3rEZ2h73MO7tcigZ6vJsYRBBmDP4ywDsA6b1p8OY/https/cdn.discordapp.com/icons'
                                  r'/611313544780316722/a_57a86574127aa12d76d876f462432a6d.webp', text=("The Coop "
                                                                                                        "Community ("
                                                                                                        "Facility "
                                                                                                        "Home) • "
                                                                                                        "" + timeofreport))
        await message.channel.send(embed=embed)
        if message.author.dm_channel is None:
            channel2 = await message.author.create_dm()
        else:
            channel2 = message.author.dm_channel
        await channel2.send(embed=embed)
        sql = """INSERT INTO Ticketlogs (ReportID,UserID,Channel,Datetime) Values(?,?,?,?)"""
        c.execute(sql, (reportid, mauthorid, channelname, timeofreport))
        conn.commit()
    elif str(message.content).lower().startswith(".format"):
        embed = discord.Embed(title='How to report')
        embed.add_field(name="Format",
                        value=(""".report Offender's IGN:
        Offence:
        Your Class:
        Offender's Class:
        Context:
        Evidence:"""),
                        inline=False)
        embed.set_footer(icon_url=r'https://images-ext-1.discordapp.net/external'
                                  r'/ULH3rEZ2h73MO7tcigZ6vJsYRBBmDP4ywDsA6b1p8OY/https/cdn.discordapp.com/icons'
                                  r'/611313544780316722/a_57a86574127aa12d76d876f462432a6d.webp', text=("The Coop "
                                                                                                        "Community ("
                                                                                                        "Facility "
                                                                                                        "Home) • "
                                                                                                        "" + str(
            datetime.datetime.now())[:-7]))
        await message.channel.send(embed=embed)
        await message.delete()
    elif str(message.content).lower().startswith(".purge"):
        if message.author.id in approvedusers:
            await purgereports()
    elif str(message.content).lower().startswith(".disconnect"):
        if message.author.id in approvedusers:
            await dbexit()
    elif str(message.content).lower().startswith(".stats"):
        if message.author.id in approvedusers:
            await dbtoday(message)
    elif str(message.content).lower().startswith(".connect"):
        if message.author.id in approvedusers:
            await dbconnect()
    if message.channel.id in ingamereportchannels:
        await message.add_reaction('👍')
        m = False
        n = False
        m2 = False
        tkbans = [15, 1440, 26280000]
        racismbans = [1440, 26280000]
        kosbans = [5, 30, 1440, 26280000]
        toxicitybans = [1, 1440, 26280000]
        bantimelist = [tkbans, racismbans, kosbans, toxicitybans]
        bannames = ["TK", "Racism", "KOS", "Toxicity"]
        bantimenum = [3, 2, 4, 3]
        banmessage = ""
        readoffence = ""
        timeofreport = str(datetime.datetime.now())[:-7]
        channelname = str(message.channel.name)
        messagered = message.content[message.content.index("report filled:") + 15:]
        print(messagered)
        found = messagered[messagered.rindex(") [") - 23:messagered.rindex(") [")]
        print(messagered.rindex(") [") - 23)
        foundname = messagered[messagered.index("reported ") + 9:messagered.rindex(" (")]
        print(found)
        print(foundname)
        m = True
        mauthorid = messagered[messagered.index("(") + 1:messagered.index("(") + 24]
        mauthor = messagered[:messagered.index("(") - 1]
        checker = 0
        while True:
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'}
            cookies = s.cookies.get_dict()
            tosenddata = {'APISecret': APISecret, 'SearchType': 0, 'SearchValue': str(found)}
            try:
                response = s.post('https://api.pmf2.scpfacility.uk/banSearch.php',
                                  headers=headers, data=tosenddata, cookies=cookies,
                                  allow_redirects=True, verify=False)
            except Exception as e:
                print(e)
                print("MAJOR FAIL")
                break
            print(response.text)
            print(response.status_code)
            haystack = json.loads(response.text)
            offences = []
            try:
                for ban in haystack['Bans']:
                    offences.append(ban["Offence"])
            except:
                print("no bans")
            tk = False
            racism = False
            kos = False
            toxicity = False
            if len(offences) != 0:
                m2 = True
                for po in range(len(offences)):
                    susoffence = offences[po].lower()
                    if 'tk' in susoffence or 'teamkill' in susoffence or 'team kill' in susoffence:
                        tk = True
                    if 'racism' in susoffence or 'racist' in susoffence:
                        racism = True
                    if 'kos' in susoffence:
                        kos = True
                    if 'mic' in susoffence or 'spam' in susoffence:
                        toxicity = True
                    listcalc = [tk, racism, kos, toxicity]
                    for j in range(len(listcalc)):
                        if listcalc[j]:
                            bantimelist[j].pop(0)
                            if len(bantimelist[j]) == 0:
                                bantimelist[j].append(26280000)
                for poo in range(len(offences)):
                    readoffence += offences[::-1][poo] + "\n"
            messageline2 = messagered[messagered.rindex("] for") + 6:-1]
            susoffence = messageline2.strip().lower()
            mass = False
            tk = False
            racism = False
            kos = False
            toxicity = False
            if 'mass' in susoffence:
                mass = True
            if 'tk' in susoffence or 'teamkill' in susoffence or 'team kill' in susoffence:
                tk = True
            if 'racism' in susoffence or 'racist' in susoffence or 'n word' in susoffence or 'n-word' in susoffence:
                racism = True
            if 'kos' in susoffence:
                kos = True
            if 'mic' in susoffence or 'spam' in susoffence:
                toxicity = True
            listcalc = [tk, racism, kos, toxicity]
            tobantime = 0
            reasons = ""
            for po in range(len(listcalc)):
                if listcalc[po] == True:
                    tobantime += bantimelist[po][0]
                    if reasons == "":
                        reasons += bannames[po]
                    else:
                        reasons += (", " + bannames[po])
            if reasons == "":
                break
            if mass:
                tobantime = tobantime * 2
                reasons = "Mass " + reasons
            banmessage = "ban ID " + str(tobantime) + " " + str(reasons) + " (" + str(
                tobantime) + " minutes) - See the discord for more information"
            n = True
            break

        reportid = shortuuid.ShortUUID().random(length=22)
        embed = discord.Embed(title=('New Report from ' + mauthor), colour=0xe74c3c)
        embed.add_field(name="Reported by", value=(mauthor + " - ID: " + mauthorid),
                        inline=True)
        embed.add_field(name="Channel", value=(str(message.channel.mention)),
                        inline=True)
        embed.add_field(name='Report Content:', value=messagered.lstrip(), inline=False)
        if m:
            embed.add_field(name='Offender:', value=found + " - " + foundname, inline=False)
        if m2:
            embed.add_field(name='Offender bans:', value=readoffence, inline=False)
        if n:
            embed.add_field(name='Suspected ban command:', value=str(banmessage), inline=False)
        embed.add_field(name='Report ID', value=("`" + str(reportid) + "`"))
        embed.set_footer(icon_url=r'https://images-ext-1.discordapp.net/external'
                                  r'/ULH3rEZ2h73MO7tcigZ6vJsYRBBmDP4ywDsA6b1p8OY/https/cdn.discordapp.com/icons'
                                  r'/611313544780316722/a_57a86574127aa12d76d876f462432a6d.webp', text=("The Coop "
                                                                                                        "Community ("
                                                                                                        "Facility "
                                                                                                        "Home) • "
                                                                                                        "" + timeofreport))

        await channelsend.send(("<@&" + str(gamereportroleid) + ">").format(discord.role.Role.mention), embed=embed)
        sql = """INSERT INTO Ticketlogs (ReportID,UserID,Channel,Datetime) Values(?,?,?,?)"""
        c.execute(sql, (reportid, mauthorid, channelname, timeofreport))
        conn.commit()


@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    user = client.get_user(payload.user_id)
    global channelsend, logchannel
    if message.channel.id != reportchannelid:
        print("unbased")
        return
    if user == client.user:
        print("cringe")
        return

    try:
        newEmbed = message.embeds[0]
    except:
        return
    print("yes")
    tkbans = [15, 1440, 26280000]
    racismbans = [1440, 26280000]
    kosbans = [5, 30, 1440, 26280000]
    toxicitybans = [1, 1440, 26280000]
    bantimelist = [tkbans, racismbans, kosbans, toxicitybans]
    bannames = ["TK", "Racism", "KOS", "Toxicity"]
    embed_dict = newEmbed.to_dict()
    print(embed_dict)

    if payload.emoji == '👁️':
        print("oh yeah it's all coming together")
        tolookat = ""
        susoffender = ""
        for field in newEmbed.fields:
            if field.name == 'Suspected offender:':
                susoffender = field.value.split()[0]
            if field.name == 'Suspected ban command:':
                tolookat = field.value
        tolookat = tolookat.replace("ban ID ", "")
        tolookat = tolookat.replace(" - See the discord for more information", "")
        tolookatlist = tolookat.split()
        try:
            offencetime = tolookatlist[0]
        except:
            return
        offencedonelist = []
        offencenum = 1
        print(tolookatlist)
        if len(tolookatlist) == 4 or (len(tolookatlist) == 5 and 'mass' in tolookat.lower()):
            print("yes it's that one")
            offencedone = tolookatlist[1]
            for i in range(len(bannames)):
                if offencedone == bannames[i]:
                    print("standard insertion")
                    for j in range(len(bantimelist[i])):
                        print(str(bantimelist[i][j]))
                        if 'mass' in tolookat.lower():
                            if str(int(offencetime) / 2) == str(bantimelist[i][j]):
                                offencenum = j + 1
                        else:
                            if offencetime == str(bantimelist[i][j]):
                                offencenum = j + 1
            watchlistdetails = {'inputUserID': susoffender, 'inputOffence': offencedone,
                                'inputOffenceNo': offencenum,
                                'inputBanDuration': str(offencetime),
                                'inputComments': str('Watchlist provided from ReportPlus V2 by ' + user.name),
                                'submit': 'Add Entry'}
            print(watchlistdetails)
            r = s.get('https://thecoop.pmf2.somewhatsane.co.uk/home.php', allow_redirects=True)
            headers = {'User-Agent': 'Mozilla/5.0 (Nintendo 3DS; U; ; en) Version/1.7639.EU',
                       'Content-Type': 'application/x-www-form-urlencoded'}
            cookies = s.cookies.get_dict()
            if r.history:
                userdata = {'username': 'TemmieGamerGuy', 'password': loginfo, 'login': 'Login'}
                response = s.post('https://thecoop.pmf2.somewhatsane.co.uk/index.php', headers=headers,
                                  data=userdata, cookies=cookies, allow_redirects=True)
                print(response.url)
            try:
                s.post('https://thecoop.pmf2.somewhatsane.co.uk/watchlistAdd.php',
                       headers=headers, data=watchlistdetails, cookies=cookies,
                       allow_redirects=True)
                dmembed = discord.Embed(title="Watchlist Succesful",
                                        description="Your watchlist for report " + message.jump_url + " was succesful")
                if user.dm_channel is None:
                    channel3 = await user.create_dm()
                else:
                    channel3 = user.dm_channel
                await channel3.send(embed=dmembed)
            except:
                print("didn't like that, MAJOR ERROR")
        else:
            print("big fuck")
            '''tolookat = tolookat.replace(",", "")
            tolookatlist = tolookat.split()
            for i in range(len(tolookatlist) - 3):
                offencedonelist.append(tolookatlist[i + 1])'''
    if embed_dict['color'] != 0x00FF00:
        embed_dict['color'] = 0x00FF00
        embed_dict['image'] = None
        newEmbed = discord.Embed.from_dict(embed_dict)
        newEmbed.add_field(name='Report dealt with by:', value=("<@!" + str(user.id) + ">"))
        await message.edit(embed=newEmbed)
    if payload.emoji == '🔨':
        print("oh yeah it's all coming together")
        tolookat = ""
        susoffender = ""
        susoffendername = ""
        for field in newEmbed.fields:
            if field.name == 'Report Content:':
                susoffendername = field.value.splitlines()[0].strip()
            if field.name == 'Suspected offender:':
                susoffender = field.value.split()[0]
            if field.name == 'Suspected ban command:':
                tolookat = field.value
        tolookat = tolookat.replace("ban ID ", "")
        tolookat = tolookat.replace(" - See the discord for more information", "")
        tolookatlist = tolookat.split()
        try:
            offencetime = tolookatlist[0]
        except:
            return
        offencedonelist = []
        offencenum = 1
        print(tolookatlist)
        if len(tolookatlist) == 4 or (len(tolookatlist) == 5 and 'mass' in tolookat.lower()):
            print("yes it's that one")
            offencedone = tolookatlist[1]
            for i in range(len(bannames)):
                if offencedone == bannames[i]:
                    print("standard insertion")
                    for j in range(len(bantimelist[i])):
                        print(str(bantimelist[i][j]))
                        if 'mass' in tolookat.lower():
                            if str(int(offencetime) / 2) == str(bantimelist[i][j]):
                                offencenum = j + 1
                        else:
                            if offencetime == str(bantimelist[i][j]):
                                offencenum = j + 1
            banlistdetails = {'inputUsername': str(susoffendername), 'inputUserID': susoffender,
                              'inputOffence': offencedone,
                              'inputOffenceNo': str(offencenum),
                              'inputBanDuration': str(offencetime),
                              'inputComments': str('Ban log provided from ReportPlus V2 by ' + user.name),
                              'submit': 'Add Ban'}
            print(banlistdetails)
            r = s.get('https://thecoop.pmf2.somewhatsane.co.uk/home.php', allow_redirects=True)
            headers = {'User-Agent': 'Mozilla/5.0 (Nintendo 3DS; U; ; en) Version/1.7639.EU',
                       'Content-Type': 'application/x-www-form-urlencoded'}
            cookies = s.cookies.get_dict()
            if r.history:
                userdata = {'username': 'TemmieGamerGuy', 'password': loginfo, 'login': 'Login'}
                response = s.post('https://thecoop.pmf2.somewhatsane.co.uk/index.php', headers=headers,
                                  data=userdata, cookies=cookies, allow_redirects=True)
                print(response.url)
            try:
                s.post('https://thecoop.pmf2.somewhatsane.co.uk/banAdd.php',
                       headers=headers, data=banlistdetails, cookies=cookies,
                       allow_redirects=True)
                dmembed = discord.Embed(title="Ban Succesful",
                                        description="Your ban log for report " + message.jump_url + " was succesful")
                if user.dm_channel is None:
                    channel3 = await user.create_dm()
                else:
                    channel3 = user.dm_channel
                await channel3.send(embed=dmembed)
            except:
                print("didn't like that, MAJOR ERROR")

        else:
            print("big fuck")
            '''tolookat = tolookat.replace(",", "")
            tolookatlist = tolookat.split()
            for i in range(len(tolookatlist) - 3):
                offencedonelist.append(tolookatlist[i + 1])'''


client.run(TOKEN)
