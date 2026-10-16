# KDE 6 Persian (Farsi) Localization

This repository contains the complete Persian (`fa_IR` / `fa`) localization for **KDE 6** (Plasma 6, KDE Frameworks 6, and KDE Gear applications).

---

## Translation Status

- **Progress:** 100% Complete
- **Catalogs:** 2,076 PO files
- **Total Strings:** 220,000+ messages
- **Technical Validation:** All files strictly validated with `msgfmt --check` with 0 syntax or formatting errors.
- **Orthographic Standards:**
  - Proper use of Zero-Width Non-Joiner (ZWNJ / Nim-faseleh)
  - Pure Persian letterforms (`ی` and `ک` instead of Arabic equivalents `ي` and `ك`)
  - Deterministic preservation of Latin ASCII units of measurement (`%1 MiB`, `%1 GiB`, `%1 KiB/s`) to prevent layout and parsing defects in desktop UI.

---

## Repository Structure

```text
├── work/
│   └── fa/                 # Persian PO translation catalogs (2,076 files across KDE 6)
├── build/
│   └── locale/fa/LC_MESSAGES/ # Compiled binary message catalogs (.mo)
├── dist/                   # Clean upstream-formatted distribution tarball (SVN tree standard)
└── scripts/                # Validation, compilation, and synchronization scripts
```

---

## Local Installation & Testing

You can test and use these translations directly on your Linux desktop without waiting for official distribution packages:

```bash
# Create local locale directory for the current user
mkdir -p ~/.local/share/locale/fa/LC_MESSAGES/

# Copy compiled binary catalogs (.mo)
cp build/locale/fa/LC_MESSAGES/*.mo ~/.local/share/locale/fa/LC_MESSAGES/
```

Launch any KDE application in Persian:
```bash
LANGUAGE=fa dolphin
LANGUAGE=fa systemsettings
```

---

## Upstream KDE Submission

This work is structured for official upstream integration into the KDE localization infrastructure:
- **Upstream SVN Target:** `svn://anonsvn.kde.org/home/kde/trunk/l10n-kf6/fa/messages`
- **Release Tarball:** [kde6-l10n-fa-messages.tar.gz](https://github.com/ZurvanLinux/kde-persian/releases/download/v6.0-fa/kde6-l10n-fa-messages.tar.gz)
- **Mailing List:** `kde-i18n-doc@kde.org`

---

## Maintainer & Translator

- **Mohammad Shafiee Sarvestani**
- **Email:** [muhammad.shafiee@gmail.com](mailto:muhammad.shafiee@gmail.com)
- **Organization:** [ZurvanLinux](https://github.com/ZurvanLinux)

<br/>
<hr/>
<br/>

<div dir="rtl">

# بومی‌سازی فارسی کی‌دی‌ای ۶ (KDE 6 Persian Localization)

این مخزن شامل ترجمه و بومی‌سازی کامل محیط رومیزی **KDE 6** (شامل پلاسما ۶، چارچوب‌های نگارش ۶ و تمامی برنامه‌های رسمی اکوسیستم KDE) به زبان فارسی است.

---

## وضعیت ترجمه

- **پیشرفت:** ۱۰۰٪ کامل
- **تعداد فایل‌های کاتالوگ:** ۲٬۰۷۶ پرونده PO
- **تعداد رشته‌ها:** بیش از ۲۲۰٬۰۰۰ پیام و عبارت
- **بررسی صحت فنی:** تمامی فایل‌ها با `msgfmt --check` بازبینی شده و بدون خطای نحوی هستند.
- **استاندارد خط و رسم:**
  - رعایت دقیق نیم‌فاصله (Zero-Width Non-Joiner / ZWNJ)
  - استفاده از ی و ک فارسی (`ی` و `ک` به جای حروف عربی `ي` و `ك`)
  - حفظ ساختار متغیرها و نمادهای استاندارد یکاهای حافظه و شبکه (`%1 MiB`, `%1 GiB`, `%1 KiB/s`) به صورت نویسه‌های لاتین جهت جلوگیری از اختلال در واسط کاربری.

---

## ساختار مخزن

```text
├── work/
│   └── fa/                 # کاتالوگ‌های ترجمه فارسی (PO files) برای ۲٬۰۷۶ برنامه و بسته KDE 6
├── build/
│   └── locale/fa/LC_MESSAGES/ # فایل‌های باینری کامپایل‌شده (MO files)
├── dist/                   # بسته فشرده استاندارد جهت ارسال به بالادست (Upstream SVN)
└── scripts/                # اسکریپت‌های اعتبارسنجی، همگام‌سازی و کامپایل
```

---

## آزمایش و استفاده محلی

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

## ارسال به بالادست

این پروژه برای هماهنگی و بارگذاری در مخزن رسمی ترجمه بین‌المللی KDE آماده شده است:
- **مسیر رسمی در SVN کی‌دی‌ای:** `svn://anonsvn.kde.org/home/kde/trunk/l10n-kf6/fa/messages`
- **فایل فشرده رسمی:** [kde6-l10n-fa-messages.tar.gz](https://github.com/ZurvanLinux/kde-persian/releases/download/v6.0-fa/kde6-l10n-fa-messages.tar.gz)
- **فهرست پستی هماهنگ‌کنندگان:** `kde-i18n-doc@kde.org`

---

## مترجم و نگه‌دارنده

- **محمد شفیعی سروستانی (Mohammad Shafiee Sarvestani)**
- **ایمیل:** [muhammad.shafiee@gmail.com](mailto:muhammad.shafiee@gmail.com)
- **سازمان:** [ZurvanLinux](https://github.com/ZurvanLinux)

</div>
