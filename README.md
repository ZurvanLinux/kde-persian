# KDE 6 Persian (Farsi) Localization | بومی‌سازی فارسی کی‌دی‌ای ۶

این مخزن شامل ترجمه و بومی‌سازی کامل محیط رومیزی **KDE 6** (شامل پلاسما ۶، چارچوب‌های نگارش ۶ و تمامی برنامه‌های رسمی اکوسیستم KDE) به زبان فارسی است.

This repository contains the complete Persian (`fa_IR` / `fa`) localization for **KDE 6** (Plasma 6, KDE Frameworks 6, and KDE Gear applications).

---

## وضعیت ترجمه (Translation Status)

- **پیشرفت:** ۱۰۰٪ کامل (100% Complete)
- **تعداد فایل‌های کاتالوگ:** ۲٬۰۷۶ پرونده PO
- **تعداد رشته‌ها:** بیش از ۲۲۰٬۰۰۰ پیام و عبارت
- **بررسی صحت فنی:** تمامی فایل‌ها با `msgfmt --check` بازبینی شده و بدون خطای نحوی هستند.
- **استاندارد خط و رسم:**
  - رعایت دقیق نیم‌فاصله (Zero-Width Non-Joiner / ZWNJ)
  - استفاده از ی و ک فارسی (`ی` و `ک` به جای حروف عربی `ي` و `ك`)
  - حفظ ساختار متغیرها و نمادهای استاندارد یکاهای حافظه و شبکه (`%1 MiB`, `%1 GiB`, `%1 KiB/s`) به صورت نویسه‌های لاتین جهت جلوگیری از اختلال در واسط کاربری.

---

## ساختار مخزن (Repository Structure)

```text
├── work/
│   └── fa/                 # کاتالوگ‌های ترجمه فارسی (PO files) برای ۲٬۰۷۶ برنامه و بسته KDE 6
├── build/
│   └── locale/fa/LC_MESSAGES/ # فایل‌های باینری کامپایل‌شده (MO files)
├── dist/                   # بسته فشرده استاندارد جهت ارسال به بالادست (Upstream SVN)
└── scripts/                # اسکریپت‌های اعتبارسنجی، همگام‌سازی و کامپایل
```

---

## آزمایش و استفاده محلی (Local Testing)

برای استفاده مستقیم از ترجمه‌ها در سیستم لینوکسی خود بدون نیاز به بسته‌های رسمی:

```bash
# ایجاد دایرکتوری محلی کاربر
mkdir -p ~/.local/share/locale/fa/LC_MESSAGES/

# کپی کردن فایل‌های باینری کامپایل‌شده
cp build/locale/fa/LC_MESSAGES/*.mo ~/.local/share/locale/fa/LC_MESSAGES/
```

سپس هر برنامه‌ای از KDE را می‌توانید با متغیر زبان فارسی اجرا کنید:
```bash
LANGUAGE=fa dolphin
LANGUAGE=fa systemsettings
```

---

## ارسال به بالادست (Upstream KDE Submission)

این پروژه برای هماهنگی و بارگذاری در مخزن رسمی ترجمه بین‌المللی KDE آماده شده است:
- **Upstream SVN Target:** `svn://anonsvn.kde.org/home/kde/trunk/l10n-kf6/fa/messages`
- **Mailing list:** `kde-i18n-doc@kde.org`

---

## مترجم و نگه‌دارنده (Translator & Maintainer)

- **محمد شفیعی سروستانی (Mohammad Shafiee Sarvestani)**
- **ایمیل:** [muhammad.shafiee@gmail.com](mailto:muhammad.shafiee@gmail.com)
- **سازمان:** [ZurvanLinux](https://github.com/ZurvanLinux)
