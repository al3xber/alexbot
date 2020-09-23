import discord
import random
import time
import ast
import matplotlib.pyplot as plt
from discord.ext import commands

client = commands.Bot(command_prefix = "!")

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(client.latency*1000)}ms")

@client.command()
async def Frage(ctx, *, question):
    responses=["ja","vielleicht","nein"]
    await ctx.send(f"Frage: {question}\nAntwort: {random.choice(responses)}")

@client.command()
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)

@client.command()
async def dice(ctx):
    wurfel=["1","2","3","4","5","6"]
    await ctx.send(f"@{ctx.author} Du hast eine {random.choice(wurfel)} gewürfelt!")
    
@client.command()
async def clearall(ctx, amount=5):
    await ctx.channel.purge()
    
#@client.event
#async def on_typing(ctx,user,when):
#    await ctx.send(f"{user} schreibt gerade eine Nachricht")

jointime=dict()    
leavetime=dict()
emoji=[0,None,None]

@client.event
async def on_voice_state_update(member, before, after=None):
    print("MEMBER:",member)
    print("BEFORE:", before)
    print("AFTER:",after)
    try:
        if before.channel==None and len(after.channel.members)==1 and after.channel.id!=754786375055835216:
            channel = client.get_channel(752232363576000612)
            await channel.send(f'@everyone {member.name} wartet geduldig auf Gesellschaft!')
    except:
        pass
    try:
        if (before.channel.id==751920100940185723 or before.channel.id==754786375055835216) and len(before.channel.members)==0 and after.channel==None:
            channel = client.get_channel(752232363576000612)
            await channel.purge()
    except:
        pass
    try:
        if after.channel.id==751920100940185723 and before.channel.id!=751920100940185723:
            jointime[str(member.name)]= time.time()
    except: #wichtig
        try:
            if after.channel.id==751920100940185723 and before.channel==None:
                jointime[str(member.name)]= time.time()
        except:
            pass
    try:
        if before.channel.id==751920100940185723 and (after.channel==None or after.channel.id==754786375055835216):              #hier vllt fehler
            leavetime[str(member.name)]= time.time()
            f = open("dict.txt","r")
            string=f.readline()
            f.close()
            string=ast.literal_eval(string)
            try:
                string[str(member.name)]+=leavetime[str(member.name)]-jointime[str(member.name)]
            except:
                string[str(member.name)]=leavetime[str(member.name)]-jointime[str(member.name)]
            print(string)
            g = open("dict.txt","w")
            g.write( str(string) )
            g.close()
    except:
        pass 

@client.command()
async def stats(ctx):
    cha = client.get_channel(751920100940185723)
    for mem in cha.members:
        leavetime[str(mem.name)]= time.time()
        
        f = open("dict.txt","r")
        string=f.readline()
        f.close()
        string=ast.literal_eval(string)
        try:
            string[str(mem.name)]+=leavetime[str(mem.name)]-jointime[str(mem.name)]
        except:
            string[str(mem.name)]=leavetime[str(mem.name)]-jointime[str(mem.name)]
        jointime[str(mem.name)]= time.time()
        g = open("dict.txt","w")
        g.write( str(string) )
        g.close()
    
    f = open("dict.txt","r")
    string=f.readline()
    f.close()
    string=ast.literal_eval(string)

    string=dict({k: v for k, v in sorted(string.items(),reverse=True, key=lambda item: item[1])})
    keys = list(list(string.keys()))[0:5]
    values = list(string.values())[0:5]

    fig = plt.figure()   
    plt.title("Top 5")
    plt.bar(keys, [x/3600 for x in values])
    emoji[2] = plt.gca().get_ylim()
    plt.ylabel('Zeit in Stunden')
    plt.savefig('stats.png')
    pic = await ctx.channel.send(file=discord.File('stats.png'))
    
    await pic.add_reaction("⬅")
    await pic.add_reaction("➡")
    emoji[1]=str(pic.id)
    emoji[0]=0

@client.event
async def on_reaction_add(reaction, user):
    if str(reaction.message.id)==emoji[1] and user.bot==False:
        print(reaction.message.type)
        
        f = open("dict.txt","r")
        string=f.readline()
        f.close()
        string=ast.literal_eval(string)
        string=dict({k: v for k, v in sorted(string.items(),reverse=True, key=lambda item: item[1])})
        gesamt=len(list(string.keys()))
        if reaction.emoji=="⬅" and emoji[0]>0:
            keys = list(list(string.keys()))[(emoji[0]-1)*5:(emoji[0])*5]#hier -1 hab ich weg
            values = list(list(string.values()))[(emoji[0]-1)*5:(emoji[0])*5]

            fig = plt.figure()
            if  emoji[0]==1:
                plt.title("Top 5")
            else:
                plt.title(f"Plätze {(emoji[0]-1)*5+1} bis {(emoji[0])*5}")
            plt.bar(keys, [x/3600 for x in values])

            plt.ylim(emoji[2])
            
            plt.ylabel('Zeit in Stunden')
            plt.savefig('stats.png')
            await reaction.message.delete()
            pic = await reaction.message.channel.send(file=discord.File('stats.png'))
            emoji[0]-=1
            emoji[1]=str(pic.id)
            await pic.add_reaction("⬅")
            await pic.add_reaction("➡")



        elif reaction.emoji=="➡" and emoji[0]<(gesamt-1)//5:
            emoji[0]+=1
    
            keys = list(list(string.keys()))[(emoji[0])*5:(emoji[0]+1)*5]
            values = list(list(string.values()))[(emoji[0])*5:(emoji[0]+1)*5]

            fig = plt.figure()            
            if  emoji[0]==(gesamt-1)//5:
                plt.title("Die Letzten")
            else:
                plt.title(f"Plätze {(emoji[0])*5+1} bis {(emoji[0]+1)*5}")
            plt.bar(keys, [x/3600 for x in values])
            plt.ylim(emoji[2])
            plt.ylabel('Zeit in Stunden')
            plt.savefig('stats.png')
            
            await reaction.message.delete()
            pic = await reaction.message.channel.send(file=discord.File('stats.png'))
            
            emoji[1]=str(pic.id)
            await pic.add_reaction("⬅")
            await pic.add_reaction("➡")
        
client.run('NzUyMTkxNjkyNDcxMjcxNTI1.X1UDGg.1yt7yqNL7bvoWLroGyGrQFHrkpI')
