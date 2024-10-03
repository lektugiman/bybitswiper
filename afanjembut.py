import os
import json
import time
import requests
import urllib3
import sys
import re
import hmac
import hashlib
import random
import math
from datetime import datetime
import urllib.parse
from colorama import Fore, Style, init
from multiprocessing import Pool

init(autoreset=True)

def generate_hash(key, message):
    hmac_obj = hmac.new(key.encode(), message.encode(), hashlib.sha256)
    return hmac_obj.hexdigest()

def url_decode(encoded_url):
    return urllib.parse.unquote(encoded_url)

def value(input_str):
    return sum(ord(char) for char in input_str) / 1e5

def calculate(i, game_time, game_id):
    result = math.floor(10 * value(i) + max(0, 1200 - 10 * game_time) + 2000) * (1 + 9 / 54)
    return math.floor(result) / 10 + value(game_id)

def print_banner():
    print(Fore.GREEN + r"""
 █████  ██     ██ ███████ ███████ ███████  ██████  ██    ██  █████  ██████  
██   ██ ██     ██ ██           ██ ██      ██    ██ ██    ██ ██   ██ ██   ██ 
███████ ██  █  ██ ███████     ██  ███████ ██    ██ ██    ██ ███████ ██   ██ 
██   ██ ██ ███ ██      ██    ██        ██ ██ ▄▄ ██ ██    ██ ██   ██ ██   ██ 
██   ██  ███ ███  ███████    ██   ███████  ██████   ██████  ██   ██ ██████  
                                              ▀▀                           
    """ + Style.RESET_ALL)
    print(Fore.GREEN + "Bybitcoinswiper" + Style.RESET_ALL)

class ByBit:
    def __init__(self, init_data, proxy=None):
        self.session = requests.session()
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,fr-FR;q=0.8,fr;q=0.7,vi-VN;q=0.6,vi;q=0.5",
            "Content-Type": "application/json",
            "Origin": "https://bybitcoinsweeper.com",
            "Referer": "https://bybitcoinsweeper.com/",
            "tl-init-data": None,
            "Sec-Ch-Ua": '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Ch-Ua-Platform": '"Android"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Linux; Android 14; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.146 Mobile Safari/537.36"
        }
        self.info = {"score": 0}
        self.init_data = init_data
        if proxy:
            self.session.proxies.update({'http': proxy, 'https': proxy})

    def log(self, message, level, account_number=None):
        levels = {
            "infoA1": Fore.RED,
            "gaiso": Fore.RED,
            "valid bolo": Fore.GREEN,
            "sekyo": Fore.YELLOW
        }
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        account_info = f"Akun{account_number} : " if account_number else ""
        print(f"{Fore.GREEN}{current_time} | {levels.get(level, Fore.RED)}{level} | {account_info}{message}" + Style.RESET_ALL)

    def wait(self, seconds):
        for i in range(seconds, 0, -1):
            sys.stdout.write(f"\r{Fore.YELLOW}ENTENI {i} detikngkas...{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("\r")
        sys.stdout.flush()

    def login(self):
        try:
            self.headers["tl-init-data"] = self.init_data
            response = self.session.post("https://api.bybitcoinsweeper.com/api/auth/login", json={"initData": self.init_data}, headers=self.headers)
            if response.status_code == 201:
                data = response.json()
                self.headers['Authorization'] = f"Bearer {data['accessToken']}"
                return {
                    "success": True,
                    "accessToken": data['accessToken'],
                    "refreshToken": data['refreshToken'],
                    "userId": data['id'],
                    "first_name": data.get("first_name", ""),
                    "last_name": data.get("last_name", "")
                }
            else:
                return {"success": False, "error": "Unexpected status code"}
        except requests.RequestException as error:
            return {"success": False, "error": str(error)}

    def score(self, account_number):
        for i in range(3):
            try:
                min_game_time = 60
                max_game_time = 180
                game_time = random.randint(min_game_time, max_game_time)
                starttime = int(time.time() * 1000)
                playgame = self.session.post("https://api.bybitcoinsweeper.com/api/games/start", json={}, headers=self.headers).json()
                if "message" in playgame:
                    if "expired" in playgame["message"]:
                        self.log("jikuko queryneh", "gaiso")
                        sys.exit(0)
                gameid = playgame["id"]
                rewarddata = playgame["rewards"]
                self.log(f"Game mulai menengosek {i + 1}/3. timing: {game_time} detik", 'infoA1', account_number)
                self.wait(game_time)
                i = "66f259c3bc25ac58ea3605fcv$2f1"
                first = f"{i}-{gameid}-{starttime}"
                last = f"{game_time}-{gameid}"
                score = calculate(i, game_time, gameid)
                game_data = {
                    "bagCoins": rewarddata["bagCoins"],
                    "bits": rewarddata["bits"],
                    "gifts": rewarddata["gifts"],
                    "gameId": gameid,
                    'gameTime': game_time,
                    "h": generate_hash(first, last),
                    'score': float(score)
                }
                res = self.session.post('https://api.bybitcoinsweeper.com/api/games/win', json=game_data, headers=self.headers)
                print(res.text)
                if res.status_code == 201:
                    self.info["score"] += score
                    self.log(f"game sampun: oleh+ {score} points | Total: {self.info['score']}", "valid bolo", account_number)
                elif res.status_code == 401:
                    self.log('Token expiredsu, jikuko queryneh', "gaiso", account_number)
                    return False
                else:
                    self.log(f"Error dengan kode {res.status_code}", 'gaiso', account_number)
                self.wait(5)
            except requests.RequestException:
                self.log('kaken request, entenisek', 'sekyo', account_number)
                self.wait(60)
        self.log("Jeda 5 menit sebelum kembali bermain...", "infoA1", account_number)
        self.wait(300)
        self.score(account_number)

    def run(self, account_number):
        login_result = self.login()
        if login_result["success"]:
            first_name = login_result.get("first_name", "")
            last_name = login_result.get("last_name", "")
            full_name = f"{first_name} {last_name}"
            self.log(f"{full_name}", 'infoA1', account_number)
            self.log(f'login sukses! AKUN {account_number}', "valid bolo", account_number)
            game_result = self.score(account_number)
            if not game_result:
                self.log('Logino neh, taklanjut liane', 'sekyo', account_number)
        else:
            self.log(f"login gagal! {login_result['error']}", 'gaiso', account_number)

def run_account(init_data, proxy, account_number):
    client = ByBit(init_data, proxy)
    try:
        client.run(account_number)
    except KeyboardInterrupt:
        print(f"{Fore.RED}Proses dihentikan untuk akun {init_data}{Style.RESET_ALL}")
        sys.exit(0)

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print_banner()
    data_file = os.path.join(os.path.dirname(__file__), 'data.txt')
    with open(data_file, 'r', encoding='utf8') as f:
        data = [line.strip() for line in f if line.strip()]

    proxies = [line.strip() for line in open('proxy.txt') if line.strip()]

    accounts = []
    for i, init_data in enumerate(data):
        proxy = proxies[(i - 1) % len(proxies)] if proxies else None
        accounts.append((init_data, proxy, i + 1))

    with Pool(processes=6) as pool:
        try:
            pool.starmap(run_account, accounts)
        except KeyboardInterrupt:
            print(f"{Fore.RED}Menghentikan semua proses...{Style.RESET_ALL}")
            pool.terminate()
            pool.join()

if __name__ == "__main__":
    main()
