# Stars Store — Telegram WebApp

## Sozlash

### 1. Netlify Environment Variables
Netlify → Site configuration → Environment variables ga qo'shing:

| Key | Value |
|-----|-------|
| `JB_BIN_ID` | JSONBin.io dan Bin ID |
| `JB_API_KEY` | JSONBin.io Master Key |
| `SS_API_KEY` | `stars_store_secret_2024` |

### 2. index.html da CONFIG ni o'zgartiring
```js
const CONFIG = {
  BOT_TOKEN: 'sizning_bot_token',
  ADMIN_ID: 'sizning_telegram_id',
  ADMIN_PASSWORD: 'parol_raqam',
  SS_API_KEY: 'stars_store_secret_2024',
};
```

### 3. GitHub orqali deploy
1. GitHub da yangi repo yarating
2. Bu fayllarni push qiling
3. Netlify → New project → GitHub → repo tanlang
4. Environment variables qo'shing
5. Deploy!

## Qanday ishlaydi
- Zakaz berilganda → JSONBin ga saqlanadi (server orqali)
- Admin panel → 5 soniyada avtomatik yangilanadi
- Barcha qurilmalardan zakazlar ko'rinadi
