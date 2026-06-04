# HackScore — Design Tokens

## Цветовая палитра

### Фоновые
| Token | Value | Назначение |
|-------|-------|-----------|
| `bg` | `#0A0A0F` | Основной фон приложения |
| `bg2` | `#0E0E15` | Фон sidebar |
| `card` | `#12121A` | Фон карточек |
| `card-hover` | `#1A1A28` | Фон карточек при hover |
| `elevated` | `#16161F` | Поднятые элементы (тосты) |
| `input-bg` | `#0A0A0F` | Фон полей ввода |

### Бордеры
| Token | Value | Назначение |
|-------|-------|-----------|
| `border` | `#1E1E2E` | Стандартный бордер |
| `border-light` | `rgba(255,255,255,0.06)` | Тонкий бордер (header) |
| `border-focus` | `#6366F1` | Бордер при фокусе |

### Акцентные цвета
| Token | Value | Назначение |
|-------|-------|-----------|
| `accent` | `#6366F1` | Основной акцент (индиго) |
| `accent-light` | `#818CF8` | Светлый акцент |
| `accent-dark` | `#4F46E5` | Тёмный акцент |
| `accent-15` | `rgba(99,102,241,0.15)` | Фон акцентных элементов |
| `accent-10` | `rgba(99,102,241,0.10)` | Слабый акцентный фон |
| `cyan` | `#06B6D4` | Вторичный акцент (бирюзовый) |
| `cyan-15` | `rgba(6,182,212,0.15)` | Фон бирюзовых элементов |

### Статусные цвета
| Token | Value | Назначение |
|-------|-------|-----------|
| `green` | `#10B981` | Успех |
| `green-15` | `rgba(16,185,129,0.15)` | Фон успеха |
| `red` | `#EF4444` | Ошибка |
| `red-15` | `rgba(239,68,68,0.15)` | Фон ошибки |
| `yellow` | `#F59E0B` | Предупреждение |
| `yellow-15` | `rgba(245,158,11,0.15)` | Фон предупреждения |

### Медали (лидерборд)
| Token | Value |
|-------|-------|
| `gold` | `#FBBF24` |
| `silver` | `#94A3B8` |
| `bronze` | `#D97706` |

### Текст
| Token | Value | Назначение |
|-------|-------|-----------|
| `t1` | `#FFFFFF` | Основной текст |
| `t2` | `rgba(255,255,255,0.6)` | Вторичный текст |
| `t3` | `rgba(255,255,255,0.4)` | Третичный (placeholder) |
| `t4` | `rgba(255,255,255,0.2)` | Приглушённый |

---

## Типографика

### Шрифты
| Роль | Семейство | Вес |
|------|-----------|-----|
| Заголовки | `Space Grotesk` | 600, 700 |
| Основной текст | `DM Sans` | 300–700 |
| Код/моно | `JetBrains Mono` | 400, 500 |

### Google Fonts URL
```
https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=JetBrains+Mono:wght@400;500&display=swap
```

### Размеры текста
| Элемент | Размер | Вес | Шрифт |
|---------|--------|-----|-------|
| h1 (заголовок страницы) | 24px | 700 | Space Grotesk |
| h2 (секция) | 18px | 700 | Space Grotesk |
| h3 (карточка) | 16px | 600 | Space Grotesk |
| Body | 14px | 400 | DM Sans |
| Small | 13px | 400/500 | DM Sans |
| Caption | 12px | 400 | DM Sans |
| Label (sidebar section) | 10px | 600 | DM Sans, uppercase, tracking 0.08em |
| Code | 13px | 400 | JetBrains Mono |
| Stat number | 28px | 700 | Space Grotesk |
| Score big | 22px | 700 | Space Grotesk |
| Badge | 12px | 500 | DM Sans |

---

## Размеры и отступы

### Радиусы
| Token | Value | Назначение |
|-------|-------|-----------|
| `rs` | `6px` | Кнопки, инпуты, мелкие элементы |
| `rm` | `8px` | Средние карточки, дропдауны |
| `rl` | `12px` | Большие карточки |
| `rxl` | `16px` | Модальные окна |
| Badge | `20px` | Бэйджи (pill) |
| Avatar | `50%` | Круглые аватары |

### Лэйаут
| Token | Value |
|-------|-------|
| Header height | `60px` |
| Sidebar width | `240px` |
| Main content max-width | `1200px` |
| Main content padding | `28px` |
| Card padding | `20px` |

### Отступы (gap)
| Контекст | Gap |
|----------|-----|
| Карточки в гриде | `16px` |
| Секции | `20px` |
| Внутри карточек | `14–16px` |
| Кнопки в строке | `8–10px` |
| Иконка + текст | `8–10px` |

---

## Shadows & Effects

### Тени
```css
/* Glow для акцентных элементов */
box-shadow: 0 0 20px rgba(99,102,241, 0.15);

/* Glow для кнопок при hover */
box-shadow: 0 4px 15px rgba(99,102,241, 0.35);

/* Тень для тостов и дропдаунов */
box-shadow: 0 8px 24px rgba(0,0,0, 0.4);

/* Тень для подиума лидерборда */
box-shadow: 0 0 16px rgba(99,102,241, 0.4);

/* Тень для модальных окон */
box-shadow: 0 12px 32px rgba(0,0,0, 0.5);
```

### Backdrop blur
```css
/* Header glass effect */
backdrop-filter: blur(24px);
background: rgba(18,18,26, 0.75);

/* Modal overlay */
backdrop-filter: blur(8px);
background: rgba(0,0,0, 0.6);
```

### Градиенты
```css
/* Primary gradient (кнопки, акценты) */
background: linear-gradient(135deg, #6366F1, #4F5BD5 50%, #06B6D4);

/* Gradient text (логотип) */
background: linear-gradient(135deg, #6366F1 0%, #06B6D4 100%);
-webkit-background-clip: text;

/* Score bar gradient */
background: linear-gradient(90deg, #6366F1, #06B6D4);

/* Mesh background (login page) */
background:
  radial-gradient(ellipse at 20% 40%, rgba(99,102,241,0.28) 0%, transparent 55%),
  radial-gradient(ellipse at 75% 20%, rgba(6,182,212,0.22) 0%, transparent 50%),
  radial-gradient(ellipse at 50% 85%, rgba(99,102,241,0.18) 0%, transparent 55%),
  radial-gradient(ellipse at 80% 70%, rgba(6,182,212,0.12) 0%, transparent 45%),
  #0A0A0F;
```

---

## Анимации

| Имя | Назначение | Длительность |
|-----|-----------|-------------|
| `fadeIn` | Появление элементов (translateY 6px) | 300ms ease |
| `fadeUp` | Появление блоков (translateY 16px) | 400ms ease |
| `slideR` | Тосты (translateX 10px) | 250ms ease |
| `scaleIn` | Модальные окна (scale 0.96) | 200ms ease |
| `pulse` | Пульсация точки статуса | 2s infinite |
| `spin` | Спиннер загрузки | 1s linear infinite |
| `shimmer` | Skeleton loading | 1.5s infinite |
| `meshMove` | Анимация mesh-gradient на логине | 15s ease-in-out infinite |
| `floatUp/floatDown` | Декоративные элементы на логине | 6-8s ease-in-out infinite |

### Transition tokens
```css
--fast: 150ms ease;   /* hover, focus */
--tr: 250ms ease;     /* стандартный переход */
--slow: 350ms ease;   /* крупные анимации */
```

---

## Компоненты — спецификации

### Button
| Variant | Background | Color | Border |
|---------|-----------|-------|--------|
| `primary` | gradient indigo→cyan | white | none |
| `secondary` | transparent | t1 | 1px border |
| `ghost` | transparent | t2 | none |
| `danger` | red-15 | red | 1px red/20% |

| Size | Padding | Font size |
|------|---------|-----------|
| `sm` | 6px 12px | 12px |
| `md` | 8px 16px | 13px |
| `lg` | 12px 24px | 14px |

### Badge
| Variant | Background | Color |
|---------|-----------|-------|
| `default` | card-hover | t2 |
| `success` | green-15 | green |
| `error` | red-15 | red |
| `warning` | yellow-15 | yellow |
| `info` | accent-15 | accent-light |
| `purple` | rgba(168,85,247,0.15) | #A855F7 |
| `orange` | rgba(249,115,22,0.15) | #F97316 |
| `cyan` | cyan-15 | cyan |

### Input
- Background: `input-bg` (#0A0A0F)
- Border: 1px solid `border`, focus → `border-focus` (#6366F1)
- Padding: 10px 14px
- Font size: 14px
- Icon size: 18px, color t3, focus → accent-l

### Card
- Background: `card`
- Border: 1px solid `border`
- Radius: `rl` (12px)
- Padding: 20px
- Hover: border → t3, bg → card-hover, translateY(-2px)
- Glow: box-shadow 0 0 20px rgba(99,102,241,0.2)

### Sidebar nav item
- Padding: 9px 12px
- Font size: 13px
- Active: bg accent-15, color accent-light, icon accent-light
- Hover: bg rgba(255,255,255,0.04)

### Table
- Header: font-size 12px, weight 500, color t3, padding 12px 16px
- Row: padding 14px 16px, border-bottom 1px border
- Row hover: bg card-hover

### Tabs
- Font size: 13px
- Active: color accent-light, border-bottom 2px accent, weight 600
- Inactive: color t3, weight 400

### Modal
- Max-width: 480px (default)
- Header: padding 16px 20px, border-bottom
- Body: padding 20px
- Overlay: rgba(0,0,0,0.6) + backdrop-blur(8px)

### Toast
- Position: fixed bottom-right
- Background: card, border 1px, border-left 3px (color)
- Padding: 12px 16px
- Animation: slideR 0.25s
- Auto-dismiss: 3s

### Score slider
- Track: height 6px, bg border, radius 3px
- Fill: bg accent (or gradient), transition width 0.15s
- Range: hidden native input layered on top

### Stepper
- Circle: 28px, border-radius 50%
- Done: bg accent, icon check
- Active: bg accent-15, border 2px accent
- Future: bg border, color t3
- Connector: height 2px, done → accent, future → border

### File upload zone
- Border: 2px dashed border (drag → accent)
- Padding: 32px 24px
- Icon: 32px, color t3 (drag → accent-l)
- Drag state: bg accent-10

### StatCard
- Number: 28px, weight 700, Space Grotesk
- Label: 13px, color t3
- Icon container: 40px, radius rm, bg color-mix 15%
