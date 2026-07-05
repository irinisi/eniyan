---
id: Obsidian Instruction
title: Obsidian Instruction
---
### Что тебе нужно

- Компьютер с Windows/Mac
- Приложение [Obsidian](https://obsidian.md/) (бесплатно)
- Аккаунт GitHub (попроси Савелия добавить тебя в репозиторий)

---

### Шаг 1 — Установить Git

Скачай и установи Git: **git-scm.com/downloads**

При установке оставь все настройки по умолчанию.

---

### Шаг 2 — Клонировать репозиторий

Открой **PowerShell** (Win+R → напечатай `powershell` → Enter) и выполни:

```
git clone https://github.com/irinisi/eniyan.git C:\teamos-repogit -C C:\teamos-repo checkout claude/cool-turing-vqt4u3git -C C:\teamos-repo config user.email "твой@email.com"git -C C:\teamos-repo config user.name "ТвоёИмя"
```

Когда попросит логин/пароль — введи логин GitHub и **токен** (не пароль, а токен — попроси Савелия создать тебе токен или создай сам на github.com/settings/tokens → Generate new token classic → галочка `repo`).

---

### Шаг 3 — Установить Obsidian

Скачай: **obsidian.md** → Install → установи.

---

### Шаг 4 — Открыть vault

В Obsidian:

1. Нажми **"Open folder as vault"**
2. Выбери папку `C:\teamos-repo\teamos\vault`

Ты увидишь папки Tasks, Projects, Knowledge — это всё содержимое TeamOS.

---

### Шаг 5 — Установить плагин Obsidian Git

1. Настройки (шестерёнка) → **Сторонние плагины** → Отключить безопасный режим
2. **Обзор** → в поиске напечатай `Obsidian Git` → Установить → Включить

---

### Шаг 6 — Настроить автосинхронизацию

В настройках → **Git** → прокрути вверх:

- **Auto commit-and-sync interval** → `5`
-  **Auto pull interval** → `5`


---

тест

---

### Готово

Теперь всё что ты пишешь в Obsidian — через 5 минут появится на сайте TeamOS. И наоборот: задачи созданные в боте или мини-аппе появятся в Obsidian.

**Папка Knowledge** — для общих документов (дизайн-система, заметки по проекту и т.д.), редактируйте их вместе.





