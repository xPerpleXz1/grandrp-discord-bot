import os
import discord
from discord.ext import commands, tasks
import datetime
import matplotlib.pyplot as plt
import io

from db import add_preis, get_preise, get_aktueller_preis

# ---- Konfiguration ----
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", 0))  # Falls Auto-Report gewünscht
PREFIX = "!"
bot = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())


# ---- Befehle ----
@bot.command()
async def preis(ctx, artikel: str, preis: float):
    add_preis(artikel, preis)
    await ctx.send(f"📈 Preis für **{artikel}** wurde auf **{preis}** gesetzt.")


@bot.command()
async def liste(ctx):
    preise = get_aktueller_preis()
    if not preise:
        await ctx.send("❌ Noch keine Daten vorhanden.")
        return

    msg = "📋 **Marktübersicht**\n"
    for a, p in preise:
        msg += f"- {a}: {p}\n"
    await ctx.send(msg)


@bot.command()
async def avg(ctx, artikel: str):
    preise = get_preise(artikel)
    if not preise:
        await ctx.send("❌ Keine Daten für diesen Artikel.")
        return
    avg = sum(p[0] for p in preise) / len(preise)
    await ctx.send(f"📊 Durchschnittspreis von **{artikel}**: {avg:.2f}")


@bot.command()
async def graph(ctx, artikel: str):
    preise = get_preise(artikel)
    if not preise:
        await ctx.send("❌ Keine Daten für diesen Artikel.")
        return

    x = [p[1] for p in preise]
    y = [p[0] for p in preise]

    plt.figure(figsize=(6, 4))
    plt.plot(x, y, marker="o")
    plt.title(f"Preisverlauf: {artikel}")
    plt.xlabel("Zeit")
    plt.ylabel("Preis")
    plt.grid(True)

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()

    await ctx.send(file=discord.File(fp=buf, filename=f"{artikel}_graph.png"))


# ---- Automatischer Tagesreport ----
@tasks.loop(hours=24)
async def daily_report():
    if not CHANNEL_ID:
        return
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        return

    preise = get_aktueller_preis()
    if not preise:
        await channel.send("❌ Noch keine Marktdaten vorhanden.")
        return

    msg = "📋 **Tägliche Marktübersicht**\n"
    for a, p in preise:
        msg += f"- {a}: {p}\n"
    await channel.send(msg)

    for a, _ in preise:
        buf = io.BytesIO()
        artikel_preise = get_preise(a)
        if artikel_preise:
            x = [p[1] for p in artikel_preise]
            y = [p[0] for p in artikel_preise]
            plt.figure(figsize=(6, 4))
            plt.plot(x, y, marker="o")
            plt.title(f"Preisverlauf: {a}")
            plt.xlabel("Zeit")
            plt.ylabel("Preis")
            plt.grid(True)
            plt.savefig(buf, format="png")
            buf.seek(0)
            plt.close()
            await channel.send(file=discord.File(fp=buf, filename=f"{a}_graph.png"))


@bot.event
async def on_ready():
    print(f"✅ Bot eingeloggt als {bot.user}")
    if CHANNEL_ID:
        daily_report.start()


# ---- Bot starten ----
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ Fehler: DISCORD_TOKEN nicht gesetzt!")
