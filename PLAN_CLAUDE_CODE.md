# HackScore — План разработки для Claude Code

## Название проекта: **HackScore**

> Веб-сервис для автоматического учёта и оценки продуктовых решений команд на хакатонах.

---

## Стек технологий

| Слой | Технология | Почему |
|------|-----------|--------|
| **Frontend** | React 18 + Vite + TypeScript | Быстрая сборка, типизация |
| **Стили** | Tailwind CSS + shadcn/ui | Быстрая стилизация, готовые компоненты |
| **Backend** | Python 3.12 + FastAPI | Async из коробки, автодокументация API |
| **БД** | PostgreSQL 16 | Требование ТЗ, надёжность |
| **ORM** | SQLAlchemy 2.0 + Alembic | Миграции, async support |
| **Очередь задач** | Celery + Redis | Асинхронные проверки |
| **Контейнеризация** | Docker Compose | Требование ТЗ — `docker compose up` |
| **Анализ кода** | pylint, flake8, eslint, radon | Линтеры + метрики сложности |
| **Документация** | python-docx, PyPDF2, markdown | Парсинг PDF/DOCX/MD |
| **Презентации** | python-pptx | Парсинг PPTX |
| **Видео** | ffprobe + OpenAI Whisper (local) | Метаданные + транскрипция |
| **Sandbox** | Docker-in-Docker (DinD) | Изолированный запуск алгоритмических решений |
| **Auth** | JWT (python-jose) + bcrypt | Простая, надёжная аутентификация |

---

## Архитектура

```
┌─────────────────────────────────────────────────┐
│                  Frontend (React)                │
│         Vite + TypeScript + Tailwind             │
└──────────────────────┬──────────────────────────┘
                       │ REST API (JSON)
┌──────────────────────▼──────────────────────────┐
│               Backend (FastAPI)                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ Auth     │ │ API      │ │ File Upload      │ │
│  │ (JWT)    │ │ Routes   │ │ Handler          │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
│  ┌─────────────────────────────────────────────┐ │
│  │           Service Layer                     │ │
│  │  TeamService | CheckService | ScoreService  │ │
│  └─────────────────────────────────────────────┘ │
└──────┬──────────────────┬───────────────────────┘
       │                  │
┌──────▼──────┐   ┌───────▼────────┐
│ PostgreSQL  │   │ Redis + Celery │
│ (данные)    │   │ (очередь задач)│
└─────────────┘   └───────┬────────┘
                          │
              ┌───────────▼───────────┐
              │    Celery Workers     │
              │ ┌───────────────────┐ │
              │ │ CodeAnalyzer      │ │
              │ │ DocValidator      │ │
              │ │ PresentChecker    │ │
              │ │ VideoProcessor    │ │
              │ │ SandboxRunner     │ │
              │ └───────────────────┘ │
              └───────────────────────┘
```

### Структура монорепо

```
hackscore/
├── docker-compose.yml
├── .env.example
├── README.md
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic/
│   ├── app/
│   │   ├── main.py                  # FastAPI app
│   │   ├── config.py                # Settings (pydantic-settings)
│   │   ├── database.py              # SQLAlchemy engine + session
│   │   │
│   │   ├── models/                  # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── team.py
│   │   │   ├── hackathon.py
│   │   │   ├── submission.py
│   │   │   ├── check_result.py
│   │   │   ├── criterion.py
│   │   │   ├── expert_score.py
│   │   │   └── algo_task.py
│   │   │
│   │   ├── schemas/                 # Pydantic schemas
│   │   │   ├── auth.py
│   │   │   ├── team.py
│   │   │   ├── submission.py
│   │   │   ├── score.py
│   │   │   └── algo.py
│   │   │
│   │   ├── api/                     # Route handlers
│   │   │   ├── auth.py
│   │   │   ├── teams.py
│   │   │   ├── submissions.py
│   │   │   ├── checks.py
│   │   │   ├── scoring.py
│   │   │   ├── hackathons.py
│   │   │   └── algo.py
│   │   │
│   │   ├── services/                # Business logic
│   │   │   ├── auth_service.py
│   │   │   ├── team_service.py
│   │   │   ├── submission_service.py
│   │   │   ├── scoring_service.py
│   │   │   └── algo_service.py
│   │   │
│   │   ├── workers/                 # Celery tasks
│   │   │   ├── celery_app.py
│   │   │   ├── code_analyzer.py
│   │   │   ├── doc_validator.py
│   │   │   ├── presentation_checker.py
│   │   │   ├── video_processor.py
│   │   │   └── sandbox_runner.py
│   │   │
│   │   └── utils/
│   │       ├── deps.py              # Dependency injection
│   │       ├── security.py          # JWT + hashing
│   │       └── file_handler.py      # Upload management
│   │
│   └── tests/
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── api/                     # API client (axios)
│   │   ├── store/                   # Zustand stores
│   │   ├── hooks/
│   │   ├── components/
│   │   │   ├── ui/                  # shadcn components
│   │   │   ├── layout/
│   │   │   └── shared/
│   │   ├── pages/
│   │   │   ├── auth/
│   │   │   ├── participant/
│   │   │   ├── jury/
│   │   │   └── organizer/
│   │   └── lib/
│   │       └── utils.ts
│   └── public/
│
└── sandbox/                         # Для алгоритмического модуля
    ├── Dockerfile.runner
    └── runners/
        ├── python_runner.sh
        ├── cpp_runner.sh
        └── java_runner.sh
```

---

## Модель данных (PostgreSQL)

```
users
  id              UUID PK
  email           VARCHAR UNIQUE NOT NULL
  password_hash   VARCHAR NOT NULL
  full_name       VARCHAR NOT NULL
  role            ENUM('participant','jury','organizer') NOT NULL
  avatar_url      VARCHAR
  created_at      TIMESTAMP DEFAULT NOW()

hackathons
  id              UUID PK
  title           VARCHAR NOT NULL
  description     TEXT
  status          ENUM('draft','registration','in_progress','judging','finished')
  start_date      TIMESTAMP
  end_date        TIMESTAMP
  created_by      UUID FK → users
  created_at      TIMESTAMP DEFAULT NOW()

teams
  id              UUID PK
  name            VARCHAR NOT NULL
  hackathon_id    UUID FK → hackathons
  created_at      TIMESTAMP DEFAULT NOW()

team_members
  id              UUID PK
  team_id         UUID FK → teams
  user_id         UUID FK → users
  is_captain      BOOLEAN DEFAULT FALSE

criteria
  id              UUID PK
  hackathon_id    UUID FK → hackathons
  name            VARCHAR NOT NULL
  description     TEXT
  weight          FLOAT NOT NULL          -- доля от 0 до 1, сумма = 1
  max_score       INT DEFAULT 10
  is_auto         BOOLEAN DEFAULT FALSE   -- автоматический или экспертный
  order_index     INT

submissions
  id              UUID PK
  team_id         UUID FK → teams
  hackathon_id    UUID FK → hackathons
  repo_url        VARCHAR
  repo_archive    VARCHAR                 -- путь к загруженному архиву
  doc_file        VARCHAR
  presentation    VARCHAR
  screencast_file VARCHAR
  screencast_url  VARCHAR                 -- ссылка на видеохостинг
  status          ENUM('draft','submitted','checking','checked') DEFAULT 'draft'
  submitted_at    TIMESTAMP
  updated_at      TIMESTAMP DEFAULT NOW()

check_results
  id              UUID PK
  submission_id   UUID FK → submissions
  check_type      ENUM('code','documentation','presentation','screencast')
  status          ENUM('pending','running','completed','failed')
  score           FLOAT                   -- автоматическая оценка 0-10
  report          JSONB                   -- детальный отчёт
  started_at      TIMESTAMP
  completed_at    TIMESTAMP

expert_scores
  id              UUID PK
  submission_id   UUID FK → submissions
  criterion_id    UUID FK → criteria
  jury_id         UUID FK → users
  score           INT                     -- 0-10
  comment         TEXT
  created_at      TIMESTAMP DEFAULT NOW()

-- === Алгоритмический модуль ===

algo_tasks
  id              UUID PK
  hackathon_id    UUID FK → hackathons
  title           VARCHAR NOT NULL
  description     TEXT NOT NULL            -- условие задачи (Markdown)
  time_limit_ms   INT DEFAULT 2000
  memory_limit_mb INT DEFAULT 256
  created_by      UUID FK → users

algo_tests
  id              UUID PK
  task_id         UUID FK → algo_tasks
  input_data      TEXT NOT NULL
  expected_output TEXT NOT NULL
  is_sample       BOOLEAN DEFAULT FALSE   -- пример в условии
  order_index     INT

algo_submissions
  id              UUID PK
  task_id         UUID FK → algo_tasks
  user_id         UUID FK → users
  team_id         UUID FK → teams
  language        ENUM('python','cpp','java')
  source_code     TEXT NOT NULL
  verdict         ENUM('pending','OK','WA','TL','ML','RE','CE')
  execution_time  INT                     -- ms
  memory_used     INT                     -- KB
  test_passed     INT DEFAULT 0
  test_total      INT DEFAULT 0
  error_message   TEXT
  submitted_at    TIMESTAMP DEFAULT NOW()
```

---

## Пошаговый план выполнения

> Каждый шаг — отдельный промпт для Claude Code. Шаги выполняются **строго последовательно**. Каждый следующий шаг опирается на результат предыдущего.

---

### ШАГ 0: Инициализация проекта

**Промпт для Claude Code:**
```
Создай монорепо проекта HackScore со следующей структурой:

1. Корневой docker-compose.yml с сервисами:
   - postgres:16 (порт 5432, volume для данных)
   - redis:7-alpine (порт 6379)
   - backend (build ./backend, порт 8000, зависит от postgres и redis)
   - celery-worker (тот же образ backend, команда celery worker)
   - frontend (build ./frontend, порт 5173, зависит от backend)

2. backend/:
   - Dockerfile (python:3.12-slim, установка системных зависимостей: ffmpeg, git, gcc)
   - requirements.txt (fastapi, uvicorn, sqlalchemy[asyncio], asyncpg, alembic, 
     python-jose[cryptography], passlib[bcrypt], python-multipart, celery, redis,
     radon, pylint, python-docx, PyPDF2, python-pptx, openai-whisper, pydantic-settings)
   - Пустой app/main.py с FastAPI() и health-check эндпоинтом GET /api/health
   - app/config.py с pydantic Settings (DATABASE_URL, REDIS_URL, SECRET_KEY, UPLOAD_DIR)
   - app/database.py с async SQLAlchemy engine и sessionmaker

3. frontend/:
   - Инициализация через: npm create vite@latest . -- --template react-ts
   - Установка: tailwindcss, @tailwindcss/vite, shadcn/ui, axios, zustand, 
     react-router-dom, lucide-react, react-hot-toast
   - Dockerfile (node:20-alpine, multi-stage: build + nginx)
   - vite.config.ts с proxy /api → http://backend:8000

4. .env.example со всеми переменными
5. README.md с описанием проекта и инструкцией запуска

Убедись что docker compose up --build поднимает всё без ошибок.
```

---

### ШАГ 1: Модели БД + миграции

**Промпт:**
```
В проекте HackScore (backend/app/) создай:

1. models/ — SQLAlchemy модели:
   - user.py: User (id UUID, email unique, password_hash, full_name, role ENUM participant/jury/organizer, avatar_url, created_at)
   - hackathon.py: Hackathon (id, title, description, status ENUM draft/registration/in_progress/judging/finished, start_date, end_date, created_by FK user)
   - team.py: Team (id, name, hackathon_id FK, created_at) + TeamMember (id, team_id FK, user_id FK, is_captain bool)
   - criterion.py: Criterion (id, hackathon_id FK, name, description, weight float, max_score int=10, is_auto bool, order_index int)
   - submission.py: Submission (id, team_id FK, hackathon_id FK, repo_url, repo_archive, doc_file, presentation, screencast_file, screencast_url, status ENUM draft/submitted/checking/checked, submitted_at, updated_at)
   - check_result.py: CheckResult (id, submission_id FK, check_type ENUM code/documentation/presentation/screencast, status ENUM pending/running/completed/failed, score float, report JSONB, started_at, completed_at)
   - expert_score.py: ExpertScore (id, submission_id FK, criterion_id FK, jury_id FK user, score int, comment text, created_at)
   - algo_task.py: AlgoTask + AlgoTest + AlgoSubmission (см. модель данных выше)
   - __init__.py с импортом всех моделей и Base

2. Alembic init:
   - alembic.ini + alembic/env.py настроенный на async
   - Первая миграция: alembic revision --autogenerate -m "init"

Все id — UUID с default uuid4. Все FK с ondelete CASCADE.
Используй mapped_column и Mapped из SQLAlchemy 2.0.
```

---

### ШАГ 2: Аутентификация (backend)

**Промпт:**
```
В проекте HackScore реализуй аутентификацию:

1. app/utils/security.py:
   - hash_password(password) → bcrypt hash
   - verify_password(password, hash) → bool
   - create_access_token(user_id, role) → JWT с exp 24h
   - decode_token(token) → payload

2. app/utils/deps.py:
   - get_db() — async session dependency
   - get_current_user(token) — извлекает user из JWT Bearer
   - require_role(*roles) — dependency factory, проверяет роль

3. app/schemas/auth.py:
   - RegisterRequest(email, password, full_name, role)
   - LoginRequest(email, password)
   - TokenResponse(access_token, token_type, user)
   - UserResponse(id, email, full_name, role, avatar_url)

4. app/api/auth.py — роутер /api/auth:
   - POST /register — создание пользователя, возврат токена
   - POST /login — вход, возврат токена
   - GET /me — текущий пользователь

5. Подключи роутер в main.py.

Пароли хешируются bcrypt. Токены JWT с алгоритмом HS256.
Добавь обработку ошибок: 400 если email занят, 401 если неверный пароль.
```

---

### ШАГ 3: CRUD хакатонов + команд + критериев (backend)

**Промпт:**
```
Реализуй CRUD-эндпоинты:

1. app/api/hackathons.py — роутер /api/hackathons:
   - POST / — создать хакатон (только organizer)
   - GET / — список хакатонов
   - GET /{id} — детали хакатона (включая критерии и команды)
   - PUT /{id} — обновить (только organizer-создатель)
   - PUT /{id}/status — сменить статус (organizer)

2. app/api/teams.py — роутер /api/hackathons/{hackathon_id}/teams:
   - POST / — создать команду (participant, автоматически добавляется капитаном)
   - GET / — список команд хакатона
   - POST /{team_id}/members — добавить участника (капитан)
   - DELETE /{team_id}/members/{user_id} — удалить участника

3. app/api/criteria.py — роутер /api/hackathons/{hackathon_id}/criteria:
   - POST / — создать критерий (organizer)
   - GET / — список критериев
   - PUT /{id} — обновить критерий
   - DELETE /{id} — удалить критерий
   - PUT /weights — массовое обновление весов (проверка что сумма = 1.0)

Все Pydantic schemas в app/schemas/. Сервисная логика в app/services/.
```

---

### ШАГ 4: Загрузка артефактов (submissions)

**Промпт:**
```
Реализуй загрузку артефактов решений:

1. app/utils/file_handler.py:
   - save_upload(file: UploadFile, subfolder: str) → path
   - Сохраняет в UPLOAD_DIR/{submission_id}/{subfolder}/filename
   - Валидация расширений: .zip/.tar.gz для архивов, .pdf/.docx/.md для доков, .pptx/.pdf для презентаций, .mp4/.webm/.mov для видео
   - Ограничение размера: 100MB для видео, 50MB для архивов, 20MB для остального

2. app/api/submissions.py — роутер /api/submissions:
   - POST / — создать submission для команды (participant + member of team)
   - GET /{id} — получить submission с check_results
   - PUT /{id}/repo — обновить URL репозитория (или загрузить архив)
   - PUT /{id}/documentation — загрузить документацию (file upload)
   - PUT /{id}/presentation — загрузить презентацию (file upload)
   - PUT /{id}/screencast — загрузить скринкаст (file upload или URL)
   - POST /{id}/submit — отправить на проверку (меняет статус на submitted, запускает Celery задачи)
   - GET /team/{team_id} — submission команды

3. При POST /{id}/submit:
   - Создать CheckResult записи со status=pending для каждого загруженного артефакта
   - Отправить Celery задачи: analyze_code, validate_doc, check_presentation, process_video
   - Обновить submission.status = 'checking'
```

---

### ШАГ 5: Celery worker — анализ кода

**Промпт:**
```
Реализуй Celery worker для анализа кода:

1. app/workers/celery_app.py:
   - Celery app с брокером Redis
   - Конфиг: task_serializer='json', result_backend='redis'

2. app/workers/code_analyzer.py — задача analyze_code(submission_id):
   
   Шаги анализа:
   a) Клонировать репозиторий (git clone --depth 1) или распаковать архив во временную папку
   b) Проверка структуры:
      - Есть README.md/README.rst? (+2 балла)
      - Есть LICENSE? (+0.5 балла)
      - Есть requirements.txt/package.json/Cargo.toml/go.mod? (+1 балл)
      - Есть Dockerfile/docker-compose.yml? (+1 балл)
      - Есть .gitignore? (+0.5 балла)
   c) Метрики кода:
      - LOC (lines of code) — подсчёт через cloc или вручную
      - Для Python: radon cc (цикломатическая сложность), radon mi (maintainability index)
      - Для JS/TS: eslint --format json (если есть)
      - Для Python: pylint --output-format=json (если есть .py файлы)
   d) Детекция секретов:
      - Поиск паттернов: API_KEY=, SECRET=, password=, AWS_ACCESS в коде
      - Проверка наличия .env файлов с реальными значениями
   e) Оценка:
      - structure_score (0-10): наличие файлов
      - complexity_score (0-10): средняя цикломатическая сложность (инвертировать: чем ниже CC, тем выше балл)
      - lint_score (0-10): количество ошибок линтера на 100 строк
      - secrets_penalty: -2 за каждый найденный секрет
      - Итого: weighted average, capped at 0-10
   
   f) Сохранить CheckResult:
      - score = итоговый балл
      - report = {structure: {...}, metrics: {loc, avg_complexity, ...}, lint: {...}, secrets: [...], details: "..."}
      - status = 'completed'

   При любой ошибке: status = 'failed', report = {error: "..."}
   Очистить временные файлы после завершения.
```

---

### ШАГ 6: Celery worker — проверка документации

**Промпт:**
```
Реализуй Celery задачу validate_documentation(submission_id):

1. app/workers/doc_validator.py:

   Поддерживаемые форматы:
   - PDF: извлечь текст через PyPDF2
   - DOCX: извлечь текст через python-docx
   - MD: читать как текст

   Проверки:
   a) Наличие обязательных разделов (искать заголовки или ключевые фразы):
      - "описание" / "description" / "о системе" / "about" (+2)
      - "развёртывание" / "deploy" / "установка" / "install" (+2)
      - "эксплуатация" / "usage" / "использование" (+2)
      Поиск регистронезависимый. Каждый найденный раздел = +балл.
   
   b) Объём:
      - < 500 символов → 0 баллов за объём
      - 500-2000 → 3 балла
      - 2000-5000 → 7 баллов
      - > 5000 → 10 баллов
   
   c) Наличие изображений/схем:
      - DOCX: проверить наличие inline images
      - PDF: проверить наличие image objects
      - MD: поиск ![...](...) паттернов
      - Есть изображения → +1 балл
   
   d) Итоговая оценка: среднее(разделы_score, объём_score, media_bonus), 0-10
   
   Сохранить report JSONB с деталями: 
   {sections_found: [...], total_length: N, has_images: bool, score_breakdown: {...}}
```

---

### ШАГ 7: Celery worker — проверка презентации

**Промпт:**
```
Реализуй Celery задачу check_presentation(submission_id):

1. app/workers/presentation_checker.py:

   Форматы: PPTX (python-pptx), PDF (считать страницы как слайды)

   Проверки:
   a) Количество слайдов:
      - 0 → 0 баллов
      - 1-4 → 3 балла (слишком мало)
      - 5-7 → 7 баллов
      - 8-15 → 10 баллов (идеально)
      - 16-25 → 7 баллов (многовато)
      - > 25 → 5 баллов (слишком много)
   
   b) Проверка структуры (для PPTX — извлечь текст каждого слайда):
      Обязательные разделы (настраиваемые организатором, по умолчанию):
      - "проблема" / "problem" 
      - "решение" / "solution"
      - "целевая аудитория" / "target audience" / "ца"
      - "стек" / "технологи" / "stack" / "tech"
      - "демо" / "demo"
      - "команда" / "team"
      Каждый найденный → +1 (макс +6, нормализовать до 0-10)
   
   c) Наличие визуального контента:
      - Изображения на слайдах → +1
      - Диаграммы/схемы → +1
   
   d) Итоговая оценка 0-10
   
   Report: {slide_count: N, sections_found: [...], sections_missing: [...], has_visuals: bool}
```

---

### ШАГ 8: Celery worker — обработка скринкаста

**Промпт:**
```
Реализуй Celery задачу process_screencast(submission_id):

1. app/workers/video_processor.py:

   a) Получить метаданные через ffprobe (subprocess):
      - duration (секунды)
      - resolution (width x height)
      - codec (video + audio)
      - file size
   
   b) Проверка длительности:
      - < 60 сек → 3 балла (слишком короткий)
      - 60-180 сек → 7 баллов
      - 180-300 сек (3-5 мин — идеально по ТЗ) → 10 баллов
      - 300-600 сек → 7 баллов
      - > 600 сек → 5 баллов
   
   c) Проверка качества:
      - resolution >= 1080p → +1
      - resolution >= 720p → +0.5
      - Есть аудиодорожка → +1
   
   d) Транскрипция (если есть аудио):
      - Извлечь аудио: ffmpeg -i video.mp4 -vn -acodec pcm_s16le audio.wav
      - Транскрипция через whisper (модель "base" для скорости):
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe("audio.wav", language="ru")
      - Генерация саммари: первые 500 символов транскрипции как preview
        + общее количество слов
   
   e) Если скринкаст — это URL (YouTube/etc):
      - Просто сохранить URL, пометить "external_link"
      - Базовая оценка 5/10 (не можем проверить автоматически)
   
   f) Итоговая оценка 0-10
   
   Report: {duration_sec: N, resolution: "1920x1080", codec: "h264", 
            has_audio: bool, transcript_preview: "...", word_count: N, 
            summary: "..."}
```

---

### ШАГ 9: Система оценки + панель жюри (backend)

**Промпт:**
```
Реализуй систему оценки:

1. app/api/scoring.py — роутер /api/scoring:

   Для жюри:
   - GET /hackathons/{id}/submissions — все submissions с результатами автопроверок
   - GET /submissions/{id}/review — детальная страница для оценки (артефакты + авто-отчёты)
   - POST /submissions/{id}/scores — выставить оценки по критериям [{criterion_id, score, comment}]
   - PUT /scores/{score_id} — обновить оценку
   
   Для организатора:
   - GET /hackathons/{id}/leaderboard — итоговая таблица:
     Для каждой команды:
     - auto_scores: {code: X, doc: Y, presentation: Z, screencast: W} (из check_results)
     - expert_scores: [{criterion: "...", avg_score: X, jury_count: N}] (среднее по всем жюри)
     - total_score: weighted sum по критериям
     Сортировка по total_score DESC

2. app/services/scoring_service.py:
   - calculate_team_score(team_id, hackathon_id):
     - Получить все критерии с весами
     - Для auto-критериев: взять score из check_results
     - Для expert-критериев: среднее по всем jury scores
     - Итого = Σ(criterion_score × weight)
   - get_leaderboard(hackathon_id): список команд с итоговыми баллами

3. GET /hackathons/{id}/leaderboard/export — экспорт в CSV
```

---

### ШАГ 10: Алгоритмический модуль (backend)

**Промпт:**
```
Реализуй модуль алгоритмических проверок:

1. app/api/algo.py — роутер /api/algo:

   Организатор:
   - POST /tasks — создать задачу (title, description MD, time_limit_ms, memory_limit_mb)
   - POST /tasks/{id}/tests — добавить тесты [{input, expected_output, is_sample}]
   - GET /tasks — список задач хакатона
   - GET /tasks/{id} — условие задачи + sample тесты
   
   Участник:
   - POST /tasks/{id}/submit — отправить решение (language, source_code)
   - GET /tasks/{id}/submissions — мои попытки
   - GET /submissions/{id} — детали попытки (вердикт, время, память)

2. app/workers/sandbox_runner.py — Celery задача run_algo_solution:
   
   a) Записать source_code во временный файл
   b) Подготовить Docker-команду:
      - Python: python3 solution.py
      - C++: g++ -O2 -o solution solution.cpp && ./solution
      - Java: javac Solution.java && java Solution
   c) Для каждого теста:
      - Запустить через subprocess с timeout (time_limit_ms) и memory tracking
      - Подать input на stdin
      - Сравнить stdout с expected_output (strip trailing whitespace)
      - Определить вердикт:
        - Компиляция провалилась → CE
        - Timeout → TL  
        - Memory exceeded → ML
        - Runtime error (exit code != 0) → RE
        - Output не совпадает → WA
        - Всё ок → OK (для этого теста)
      - Остановиться на первом не-OK вердикте
   d) Итоговый вердикт: OK если все тесты пройдены, иначе — вердикт первого failed теста
   e) Сохранить AlgoSubmission с вердиктом, test_passed, test_total, execution_time, memory_used

   ВАЖНО: Запуск БЕЗ Docker-in-Docker для простоты MVP.
   Использовать subprocess с resource limits (ulimit) для безопасности:
   - timeout для ограничения времени
   - ulimit -v для ограничения памяти
   - Запуск от непривилегированного пользователя
```

---

### ШАГ 11: Seed-данные (демо)

**Промпт:**
```
Создай скрипт backend/app/seed.py для заполнения БД демо-данными:

1. Пользователи:
   - admin@hackscore.ru / admin123 (organizer)
   - jury1@hackscore.ru / jury123 (jury)
   - jury2@hackscore.ru / jury123 (jury)
   - team1@hackscore.ru / team123 (participant)
   - team2@hackscore.ru / team123 (participant)
   - team3@hackscore.ru / team123 (participant)

2. Хакатон "Чемпионат по продуктовому программированию 2026" со статусом in_progress

3. Критерии оценки (из ТЗ):
   - Полнота MVP (20%, auto)
   - Качество автопроверок (15%, expert)
   - Алгоритмический модуль (10%, expert)
   - Архитектура и качество кода (10%, auto)
   - UX/UI (10%, expert)
   - Работоспособность стенда (10%, expert)
   - Документация (7%, auto)
   - Презентация и скринкаст (6%, auto)
   - Инновационность (6%, expert)
   - Очная защита (6%, expert)

4. 3 команды с участниками

5. 2 алгоритмические задачи:
   - "Сумма двух чисел" (time_limit=1000, memory=256) с 5 тестами
   - "Палиндром" (time_limit=1000, memory=256) с 5 тестами

Добавить эндпоинт POST /api/seed (только в dev-режиме) или management-команду.
```

---

### ШАГ 12: Frontend — Layout + Auth

**Промпт:**
```
Реализуй фронтенд HackScore. Макет дизайна приложен (ссылка на figma/скриншоты).

1. src/api/client.ts:
   - axios instance с baseURL /api
   - Interceptor: добавлять Authorization: Bearer token
   - Interceptor: при 401 → редирект на /login

2. src/store/authStore.ts (Zustand):
   - user, token, isAuthenticated
   - login(email, password), register(email, password, name, role), logout()
   - Сохранение token в localStorage

3. src/components/layout/:
   - AppLayout.tsx — sidebar + header + main content
   - Sidebar.tsx — навигация по ролям:
     * Participant: Мои хакатоны, Моя команда, Загрузка решения, Алго-задачи, Результаты
     * Jury: Хакатоны, Оценка решений, Лидерборд
     * Organizer: Управление хакатонами, Критерии, Команды, Лидерборд, Алго-задачи
   - Header.tsx — имя пользователя, роль, logout

4. src/pages/auth/:
   - LoginPage.tsx — форма входа
   - RegisterPage.tsx — форма регистрации с выбором роли

5. src/App.tsx:
   - React Router с protected routes по ролям
   - Редирект неавторизованных на /login

Следуй приложенному дизайн-макету для стилизации.
```

---

### ШАГ 13: Frontend — Участник (загрузка решений)

**Промпт:**
```
Реализуй страницы участника:

1. src/pages/participant/HackathonListPage.tsx:
   - Список доступных хакатонов
   - Кнопка "Создать команду" / "Присоединиться"

2. src/pages/participant/TeamPage.tsx:
   - Информация о команде
   - Список участников
   - Приглашение участника (по email)

3. src/pages/participant/SubmissionPage.tsx — ГЛАВНАЯ СТРАНИЦА УЧАСТНИКА:
   - Прогресс-бар: Репозиторий → Документация → Презентация → Скринкаст → Отправка
   - Секция "Репозиторий":
     - Поле для URL (GitHub/GitLab)
     - ИЛИ drag-n-drop для архива
   - Секция "Документация":
     - Drag-n-drop для PDF/DOCX/MD
     - Показывать имя файла после загрузки
   - Секция "Презентация":
     - Drag-n-drop для PPTX/PDF
   - Секция "Скринкаст":
     - Drag-n-drop для видео
     - ИЛИ поле для URL (YouTube)
   - Кнопка "Отправить на проверку"
   - После отправки: статусы проверок в реальном времени (polling каждые 5 сек)
   - Карточки результатов: для каждого артефакта — статус, балл, развернуть отчёт

4. src/pages/participant/AlgoTasksPage.tsx:
   - Список задач
   - Страница задачи: условие (Markdown render), примеры тестов
   - Редактор кода (textarea с monospace font + выбор языка)
   - Кнопка "Отправить" 
   - Таблица моих попыток: вердикт, время, память

5. src/pages/participant/ResultsPage.tsx:
   - Мои результаты: автопроверки + экспертные оценки
   - Итоговый балл
```

---

### ШАГ 14: Frontend — Жюри

**Промпт:**
```
Реализуй страницы жюри:

1. src/pages/jury/ReviewListPage.tsx:
   - Таблица всех submissions хакатона
   - Колонки: Команда, Статус проверки, Авто-балл, Мой балл, Действия
   - Фильтры: по статусу, по наличию моей оценки
   - Цветовая индикация: зелёный (оценено), жёлтый (частично), серый (не оценено)

2. src/pages/jury/ReviewDetailPage.tsx — ГЛАВНАЯ СТРАНИЦА ЖЮРИ:
   - Информация о команде
   - Табы: Код | Документация | Презентация | Скринкаст | Алгоритмы
   - Каждый таб показывает:
     - Статус автопроверки (pending/running/completed/failed)
     - Автоматический балл с шкалой
     - Развёрнутый отчёт автопроверки (JSON → красивый UI)
     - Ссылка на скачивание/просмотр артефакта
   - Таб "Скринкаст" дополнительно: транскрипция, саммари
   - Правая панель: форма оценки
     - Список критериев с полями 0-10 (slider или number input)
     - Комментарий к каждому критерию (textarea)
     - Кнопка "Сохранить оценки"
   - Навигация: "← Предыдущая команда" / "Следующая команда →"

3. src/pages/jury/LeaderboardPage.tsx:
   - Таблица с итоговыми баллами
   - Колонки: Место, Команда, по одной колонке на критерий, Итого
   - Сортировка по итогу DESC
```

---

### ШАГ 15: Frontend — Организатор

**Промпт:**
```
Реализуй страницы организатора:

1. src/pages/organizer/HackathonManagePage.tsx:
   - Создание/редактирование хакатона
   - Поля: название, описание, даты, статус
   - Кнопки смены фазы: Регистрация → Разработка → Оценка → Завершён

2. src/pages/organizer/CriteriaPage.tsx:
   - Таблица критериев: название, описание, тип (auto/expert), вес
   - Добавление/редактирование/удаление критериев
   - Визуальный индикатор суммы весов (прогресс-бар до 100%)
   - Drag-n-drop для изменения порядка
   - Предустановленные шаблоны критериев (кнопка "Загрузить стандартные")

3. src/pages/organizer/TeamsOverviewPage.tsx:
   - Список всех команд
   - Для каждой: участники, статус submission, прогресс проверок
   - Индикатор прогресса: сколько артефактов загружено

4. src/pages/organizer/AlgoManagePage.tsx:
   - CRUD задач: название, условие (Markdown editor), лимиты
   - Добавление тестов: input/output пары
   - Пометка sample тестов
   - Таблица submissions по задаче: кто, когда, вердикт

5. src/pages/organizer/LeaderboardPage.tsx:
   - Полная итоговая таблица (как у жюри, но с возможностью экспорта)
   - Кнопка "Экспорт в CSV"
   - Кнопка "Опубликовать результаты" (делает лидерборд видимым для участников)
```

---

### ШАГ 16: Финальная интеграция + полировка

**Промпт:**
```
Финализируй проект HackScore:

1. Проверь что docker compose up --build работает с нуля:
   - postgres + redis + backend + celery + frontend
   - Автоматический запуск миграций при старте backend
   - Seed-данные загружаются автоматически при первом запуске (если БД пустая)

2. Error handling:
   - Backend: единый exception handler с правильными HTTP-кодами
   - Frontend: toast-уведомления об ошибках (react-hot-toast)
   - Loading states на всех страницах (скелетоны)

3. Responsive design:
   - Sidebar складывается в бургер на мобильных
   - Таблицы горизонтально скроллятся

4. README.md:
   - Описание проекта
   - Архитектура (текстом + упоминание диаграммы)
   - Стек технологий
   - Инструкция запуска: git clone + docker compose up
   - Демо-аккаунты
   - API документация: ссылка на /api/docs (Swagger)
   - Скриншоты интерфейса

5. Проверь все flows:
   - Регистрация → Создание команды → Загрузка артефактов → Отправка → Просмотр результатов
   - Жюри видит submissions → Оценивает → Лидерборд обновляется
   - Организатор создаёт хакатон → Настраивает критерии → Видит лидерборд
   - Участник отправляет алго-задачу → Получает вердикт
```

---

## Порядок работы с Claude Code

1. Отправляй шаги **СТРОГО ПО ПОРЯДКУ** — каждый следующий зависит от предыдущего
2. После каждого шага **проверяй** что всё компилируется/запускается
3. Если Claude Code допускает ошибку — фикси в том же шаге, не переходи к следующему
4. Шаги 5-8 (Celery workers) можно делать параллельно, но лучше последовательно
5. Шаги 12-15 (frontend) — строго после того как backend API полностью работает

## Инновационные фичи (бонус к оценке «Инновационность»)

- Realtime-обновления через WebSocket (статус проверок)
- Сравнение submissions разных команд side-by-side
- Автогенерация PDF-отчёта с результатами для каждой команды
- Тепловая карта оценок жюри (кто кому сколько поставил)
- Markdown-превью условий алго-задач с подсветкой синтаксиса
- Экспорт лидерборда в красивый PDF
