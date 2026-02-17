# 🚀 Deployment Guide - Binary Top3 Bot

## ✅ GitHub Repository

**Repository:** https://github.com/jswralamar1-cmyk/binary-top3-bot

---

## 📦 Deploy على Render

### **الخطوات:**

#### **1️⃣ إنشاء Web Service:**

1. روح [dashboard.render.com](https://dashboard.render.com)
2. اضغط **New** → **Web Service**
3. Connect GitHub repository: `jswralamar1-cmyk/binary-top3-bot`

#### **2️⃣ الإعدادات:**

```
Name: binary-top3-bot
Region: Frankfurt (EU Central)
Branch: master
Runtime: Docker
Instance Type: Free
```

#### **3️⃣ Environment Variables:**

أضف المتغيرات التالية:

```
TELEGRAM_BOT_TOKEN = 8200307369:AAGEi7RYg-3v4s66o_frhAtKtBgyEljUTns
TWELVEDATA_API_KEY = ffedb7c48be644e1bd4cf3d79ca19a31
```

#### **4️⃣ Deploy:**

- اضغط **Create Web Service**
- انتظر 3-5 دقائق للـ build
- تأكد من Status = **Live**

---

## 🧪 الاختبار

### **بعد Deploy:**

1. افتح Telegram
2. ابحث عن: `@Mohammedjadim11998_bot`
3. أرسل `/start`
4. اختر النمط والإعدادات
5. اضغط **🚀 بدء الفحص**

### **المتوقع:**

- ✅ رسالة ترحيب
- ✅ أزرار تفاعلية
- ✅ فحص 25 زوج
- ✅ Top 3 إشارات مع شارتات
- ✅ رسائل مفصلة بالعربي

---

## 📊 المراقبة

### **Render Logs:**

```
Dashboard → Service → Logs
```

**ابحث عن:**
- ✅ `🚀 Binary Top3 Bot Starting...`
- ✅ `✅ Bot is ready!`
- ✅ `🔍 Running in polling mode`

### **إذا حدث خطأ:**

1. تأكد من Environment Variables
2. تأكد من TwelveData API Key صحيح
3. تأكد من Telegram Bot Token صحيح
4. شوف Logs للتفاصيل

---

## 🔧 التحديثات

### **لتحديث الكود:**

```bash
cd /path/to/binary_top3_bot
git add .
git commit -m "Update: description"
git push origin master
```

**Render سيعمل auto-deploy تلقائياً!**

---

## 📋 الملاحظات

### **Free Tier Limits:**

- ✅ **Render Free:** 750 hours/month
- ✅ **TwelveData Free:** 800 calls/day
- ⚠️ **Sleep after 15 min inactivity** (Render Free)

### **للاستخدام المستمر:**

- ترقية Render إلى Starter ($7/month)
- ترقية TwelveData إلى Basic ($8/month)

---

## 🎯 الخلاصة

✅ **الكود على GitHub:** https://github.com/jswralamar1-cmyk/binary-top3-bot
✅ **جاهز للـ Deploy على Render**
✅ **جميع الملفات موجودة**
✅ **Docker + render.yaml محضّرين**

**🚀 Deploy الآن واستمتع!**
