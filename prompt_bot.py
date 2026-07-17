# -*- coding: utf-8 -*-
"""
Discord Prompt Bot
Kullanıcılara istedikleri promptu özel mesaj (DM) yoluyla .md dosyası olarak gönderir.
"""

import os
import io
import discord
from discord import app_commands
from discord.ext import commands

# --- PROMPT TANIMLAMALARI ---
# İstediğiniz prompt metinlerini ve dosyalarını buradan kolayca düzenleyebilirsiniz.
PROMPTS = {
    "deepseek": {
        "name": "DeepSeek Promptu",
        "filename": "deepseek_prompt.md",
        "description": "DeepSeek için özel olarak optimize edilmiş prompt.",
        "content": """# DeepSeek Özel Promptu

Bu dosya DeepSeek modeli için hazırlanmıştır. Aşağıdaki promptu kopyalayıp kullanabilirsiniz:

```text
[Buraya DeepSeek için kullanmak istediğiniz ana prompt metnini girin]
Örn: Sen uzman bir Python geliştiricisisin. Kodlarımı en verimli şekilde optimize et...
```
"""
    },
    "gpt4": {
        "name": "GPT-4 Promptu",
        "filename": "gpt4_prompt.md",
        "description": "GPT-4 / ChatGPT için genel amaçlı prompt.",
        "content": """# GPT-4 Özel Promptu

Bu dosya GPT-4 modeli için hazırlanmıştır. Aşağıdaki promptu kopyalayıp kullanabilirsiniz:

```text
[Buraya GPT-4 için kullanmak istediğiniz ana prompt metnini girin]
Örn: Lütfen karmaşık konuları bana 5 yaşındaki birine anlatır gibi açıkla...
```
"""
    },
    "midjourney": {
        "name": "Midjourney Promptu",
        "filename": "midjourney_prompt.md",
        "description": "Görsel üretimi için Midjourney prompt şablonu.",
        "content": """# Midjourney Görsel Üretim Promptu

Bu dosya Midjourney görsel üretimi için hazırlanmıştır:

```text
[Buraya görsel promptunu girin]
Örn: A futuristic cyberpunk city street, neon signs, rainy night, cinematic lighting, 8k resolution --ar 16:9
```
"""
    }
}

# --- YARDIMCI FONKSİYONLAR ---
async def send_prompt_via_dm(interaction: discord.Interaction, prompt_key: str):
    """Belirtilen promptu kullanıcının DM'ine gönderir."""
    prompt_info = PROMPTS.get(prompt_key.lower())
    
    if not prompt_info:
        await interaction.response.send_message(
            f"❌ **'{prompt_key}'** adında bir prompt bulunamadı.\n"
            f"Mevcut seçenekler: `{', '.join(PROMPTS.keys())}`",
            ephemeral=True
        )
        return

    # Dosya içeriğini diskte geçici dosya oluşturmadan bellek üzerinden gönderiyoruz
    content = prompt_info["content"]
    file_bytes = io.BytesIO(content.encode("utf-8"))
    discord_file = discord.File(file_bytes, filename=prompt_info["filename"])

    try:
        # Kullanıcının DM kutusuna gönder
        await interaction.user.send(
            content=f"👋 Merhaba! İstediğiniz **{prompt_info['name']}** dosyası aşağıdadır:",
            file=discord_file
        )
        # Kanala bildirim mesajı gönder (sadece komutu yazan görsün: ephemeral=True)
        await interaction.response.send_message(
            f"✅ **{prompt_info['name']}** özel mesaj (DM) kutunuza gönderildi!",
            ephemeral=True
        )
    except discord.Forbidden:
        # Eğer kullanıcının DM kutusu kapalıysa hata verir
        await interaction.response.send_message(
            "❌ Özel mesaj gönderilemedi. Lütfen sunucu ayarlarından **'Gizlilik Ayarları -> Sunucu Üyelerinden Gelen Doğrudan Mesajlara İzin Ver'** seçeneğini aktif edin.",
            ephemeral=True
        )

# --- ETKİLEŞİMLİ ARAYÜZ (SELECT MENU) ---
class PromptDropdown(discord.ui.Select):
    def __init__(self):
        # Dropdown seçeneklerini oluşturuyoruz
        options = [
            discord.SelectOption(
                label=info["name"],
                value=key,
                description=info["description"]
            ) for key, info in PROMPTS.items()
        ]
        super().__init__(
            placeholder="Bir prompt seçin...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        # Kullanıcı dropdown'dan seçim yaptığında tetiklenir
        selected_prompt = self.values[0]
        # Seçim yapıldıktan sonra menü mesajını güncelle ve DM gönder
        await interaction.response.edit_message(content="🔄 Seçiminiz işleniyor, DM kutunuzu kontrol edin...", view=None)
        await send_prompt_via_dm(interaction, selected_prompt)

class PromptDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60) # 60 saniye sonra menü zaman aşımına uğrar
        self.add_item(PromptDropdown())

# --- BOT KURULUMU ---
class PromptBot(commands.Bot):
    def __init__(self):
        # Botun sunucudaki üyelere DM atabilmesi için gerekli izinleri (intents) tanımlıyoruz
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Slash komutlarını kaydetmek için ağaç yapısını senkronize ediyoruz
        await self.tree.sync()
        print("Slash komutları senkronize edildi.")

bot = PromptBot()

@bot.event
async def on_ready():
    print(f"🤖 Bot aktif! Giriş yapılan hesap: {bot.user}")
    print("Millet /prompt yazarak botu kullanabilir.")

# --- SLASH KOMUTU (/prompt) ---
@bot.tree.command(name="prompt", description="İstediğiniz yapay zeka promptunu DM olarak gönderir.")
@app_commands.describe(secenek="İstediğiniz prompt (Örn: deepseek, gpt4, midjourney)")
async def prompt_slash(interaction: discord.Interaction, secenek: str = None):
    # Eğer parametre (seçenek) girildiyse direkt gönder
    if secenek:
        await send_prompt_via_dm(interaction, secenek)
    else:
        # Eğer parametre girilmediyse, kullanıcıya dropdown (seçenek listesi) göster
        view = PromptDropdownView()
        await interaction.response.send_message(
            "❓ Hangi promptu almak istersiniz? Lütfen aşağıdaki menüden seçin:",
            view=view,
            ephemeral=True
        )

# --- ÇALIŞTIRMA ---
# NOT: Buraya kendi Discord Bot Token'ınızı girmelisiniz.
# Güvenlik amacıyla token'ı environment variable (çevre değişkeni) olarak almak en iyisidir.
TOKEN = os.getenv("DISCORD_TOKEN", "BURAYA_BOT_TOKENINIZI_YAZIN")

if __name__ == "__main__":
    if TOKEN == "BURAYA_BOT_TOKENINIZI_YAZIN":
        print("⚠️ HATA: Lütfen prompt_bot.py içindeki TOKEN kısmına Discord Bot Token'ınızı yazın.")
    else:
        bot.run(TOKEN)
