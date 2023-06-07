from win10toast import ToastNotifier
from pypresence import Presence
from colorama import init, Fore
import selfcord
import asyncio
import logging
import ctypes
import httpx
import time
import json
import re
import os

init(autoreset=True)

title = "Poseidon"
title_bytes = title.encode('cp1252')
ctypes.windll.kernel32.SetConsoleTitleA(title_bytes)

def configure_presence():
    RPC = Presence(client_id="1116074073487839292")
    RPC.connect()
    RPC.update(
        state="Poseidon | Sniping nitro..",
        details="Developed By Hisako | Using Selfcord Library! ",
        large_image="poseidonlarge",
        large_text="Poseidon Sniper | Thanks Shell the dev of Selfcord for help <3 "
    )
    return RPC

CODE_REGEX = re.compile(r"(http://|https://|)(discord.com/gifts/|discordapp.com/gifts/|discord.gift/|canary.discord.com/gifts/|ptb.discord.com/gifts)([a-zA-Z0-9]{5,18})")
logging.getLogger("httpcore.http11").disabled = True
logging.getLogger("httpcore.connection").disabled = True
toaster = ToastNotifier()
bot = selfcord.Bot()
RPC = configure_presence()

ascii_text = r"""
{blue}
╔═╗┌─┐┌─┐┌─┐┬┌┬┐┌─┐┌┐┌
╠═╝│ │└─┐├┤ │ │││ ││││
╩  └─┘└─┘└─┘┴─┴┘└─┘┘└┘
{reset}
""".format(blue=Fore.BLUE, reset=Fore.RESET)

@bot.on("ready")
async def ready(t):
    print(f"{Fore.GREEN}Connected to {bot.user.name}.{Fore.RESET}")
    send_windows_notification("Welcome", "The program has been successfully launched!")

def extract_nitro_code(content):
    match = CODE_REGEX.search(content)
    if match:
        return match.group(3)
    return None

async def send_webhook_message(content, webhook_url):
    payload = {
        "embeds": [{
            "description": content,
            "color": 10181046
        }],
        "username": "Poseidon",
        "avatar_url": "https://i.pinimg.com/564x/1e/d6/f2/1ed6f23f334c12ecb90e2ecf55181a95.jpg"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(webhook_url, json=payload)

        if response.status_code == 200:
            print(f"{Fore.GREEN}Message sent successfully via webhook.{Fore.RESET}")
        elif response.status_code == 204:
            print(f"{Fore.YELLOW}Message sent successfully via webhook, but no response from the server.{Fore.RESET}")
        else:
            print(f"{Fore.RED}Error sending message via webhook. Response code: {response.status_code}{Fore.RESET}")


@bot.on("message")
async def on_message(message):
    if isinstance(message.channel, (selfcord.TextChannel, selfcord.DMChannel)):
        if "discord.gift/" in message.content:
            nitro_code = extract_nitro_code(message.content)
            config = load_config()
            await redeem_nitro(nitro_code, config["token"], config["webhook_url"])

async def redeem_nitro(code, token, webhook_url):
    headers = {
        "Authorization": token
    }

    url = f"https://discordapp.com/api/v9/entitlements/gift-codes/{code}/redeem"

    async with httpx.AsyncClient() as client:
        start_time = time.perf_counter()
        response = await client.post(url, headers=headers)
        elapsed_time = (time.perf_counter() - start_time) * 1000

        if elapsed_time < 100:
            await asyncio.sleep(0.1 - elapsed_time / 1000)

        if response.status_code == 200:
            message = f"Nitro sniped! Code: {code}. Elapsed time: {elapsed_time:.2f} ms."
            await send_webhook_message(message, webhook_url)
            send_windows_notification("Nitro Code Sniped!", message)
        else:
            message = f"Failed to snipe Nitro: {code}. Elapsed time: {elapsed_time:.2f} ms."
            await send_webhook_message(message, webhook_url)

def load_config():
    try:
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
            return config
    except FileNotFoundError:
        return {}

def save_config(config):
    with open("config.json", "w") as config_file:
        json.dump(config, config_file)

def send_windows_notification(title, message):
    toaster.show_toast(title, message, duration=5)

def close_rpc():
    rpc.close()

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(ascii_text)
    config = load_config()
    if "token" not in config:
        token = input("Enter your token: ")
        config["token"] = token
        webhook_url = input("Enter your Discord webhook URL: ")
        config["webhook_url"] = webhook_url
        save_config(config)
    else:
        token = config["token"]
        webhook_url = config["webhook_url"]

    bot.run(token)
    

if __name__ == "__main__":
    main()
