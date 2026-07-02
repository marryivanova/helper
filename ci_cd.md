# CI/CD в GitLab

Оф дока: https://docs.gitlab.com/ci/yaml/
Пример по шагам: https://habr.com/ru/articles/498436/

Как назвать файл: .gitlab-ci.yml file

- пайплайн — набор задач, организованных в этапы, в котором можно собрать, протестировать, упаковать код, развернуть готовую сборку в облачный сервис, и пр.,
- этап (stage) — единица организации пайплайна, содержит 1+ задачу,
- задача (job) — единица работы в пайплайне. Состоит из скрипта (обязательно), условий запуска, настроек публикации/кеширования артефактов и много другого.

Примеры:

```yaml
image: python:3.12

stages:
  - lint
  - scan
  - quality-gate

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"
  POETRY_CACHE_DIR: "$CI_PROJECT_DIR/.cache/poetry"
  POETRY_VIRTUALENVS_IN_PROJECT: "true"

cache:
  paths:
    - .cache/pip
    - .cache/poetry
    - .venv

.before_script_template: &before_script_template
  before_script:
    - pip install --upgrade pip
    - pip install poetry
    - poetry install --no-interaction

.common-rules: &common-rules
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
    - if: $CI_COMMIT_TAG
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

.lint-job:
  stage: lint
  <<: *before_script_template
  cache:
    policy: pull
    paths:
      - .cache/pip
      - .cache/poetry
      - .venv
  <<: *common-rules

black:
  extends: .lint-job
  script:
    - |
      TARGET_BRANCH="${CI_MERGE_REQUEST_TARGET_BRANCH_NAME:-$CI_DEFAULT_BRANCH}"
      
      git fetch origin "$TARGET_BRANCH"
      
      CHANGED_FILES=$(git diff --name-only --diff-filter=d "origin/$TARGET_BRANCH"...HEAD | grep '\.py$' || true)
      
      if [ -n "$CHANGED_FILES" ]; then
        echo "🔍 Checking changed Python files with Black:"
        echo "$CHANGED_FILES"
        poetry run black --check --diff $CHANGED_FILES
      else
        echo "✅ No Python files to check"
      fi

isort:
  extends: .lint-job
  script:
    - poetry run isort . --check-only --diff --verbose

.security-job:
  stage: scan
  <<: *before_script_template
  cache:
    policy: pull
    paths:
      - .cache/pip
      - .cache/poetry
      - .venv
  <<: *common-rules

bandit:
  extends: .security-job
  script:
    - |
      TARGET_BRANCH="${CI_MERGE_REQUEST_TARGET_BRANCH_NAME:-$CI_DEFAULT_BRANCH}"
      
      echo "🎯 Target branch: $TARGET_BRANCH"
      
      git fetch origin "$TARGET_BRANCH"
      
      CHANGED_PYTHON_FILES=$(git diff --name-only --diff-filter=AM "origin/$TARGET_BRANCH"...HEAD | grep '\.py$' || true)
      
      if [ -z "$CHANGED_PYTHON_FILES" ]; then
        echo "📝 No Python files changed"
        echo '{"errors": [], "generated_at": "", "metrics": {"_totals": {}}, "results": []}' > bandit-report.json
        exit 0
      fi
      
      echo "🔍 Checking security in changed Python files:"
      echo "$CHANGED_PYTHON_FILES"
      
      # Check if .bandit.yml exists, use default config otherwise
      if [ -f ".bandit.yml" ]; then
        CONFIG_FLAG="-c .bandit.yml"
      else
        CONFIG_FLAG=""
      fi
      
      poetry run bandit $CONFIG_FLAG -f json -o bandit-report.json $CHANGED_PYTHON_FILES
      
      echo "✅ Bandit security scan completed"
  artifacts:
    when: always
    reports:
      sast: bandit-report.json
    expire_in: 1 week

penetration-test:
  image: owasp/zap2docker-stable:latest
  stage: scan
  variables:
    ZAP_TARGET: "http://sender.hwschool.tech:8000"
  before_script:
    - echo "🚀 Starting OWASP ZAP scan for $ZAP_TARGET"
  script:
    - |
      zap-baseline.py -t "$ZAP_TARGET" \
        ${ZAP_CONFIG:+-c $ZAP_CONFIG} \
        -x penetration-report.xml \
        -I
  artifacts:
    when: always
    reports:
      sast: penetration-report.xml
    expire_in: 1 week
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
    - if: $CI_PIPELINE_SOURCE == "schedule"
  allow_failure: true

code-metrics:
  stage: quality-gate
  <<: *before_script_template
  before_script:
    - !reference [.before_script_template, before_script]
    - pip install radon
  script:
    - |
      echo "=== 📊 CODE METRICS FOR CHANGED FILES ==="
      
      TARGET_BRANCH="${CI_MERGE_REQUEST_TARGET_BRANCH_NAME:-$CI_DEFAULT_BRANCH}"
      
      git fetch origin "$TARGET_BRANCH"
      CHANGED_PYTHON_FILES=$(git diff --name-only --diff-filter=AM "origin/$TARGET_BRANCH"...HEAD | grep '\.py$' || true)
      
      if [ -z "$CHANGED_PYTHON_FILES" ]; then
        echo "📝 No Python files changed"
        exit 0
      fi
      
      echo "📁 Changed Python files:"
      echo "$CHANGED_PYTHON_FILES" | sed 's/^/  - /'
      echo ""
      
      echo "$CHANGED_PYTHON_FILES" > changed_files.txt
      
      echo "📈 Cyclomatic Complexity:"
      if ! poetry run radon cc --min B --show-complexity --average --total-average $CHANGED_PYTHON_FILES 2>/dev/null; then
        echo "  No functions with complexity > B found"
      fi
      
      echo ""
      echo "📉 Maintainability Index:"
      if ! poetry run radon mi --show $CHANGED_PYTHON_FILES 2>/dev/null; then
        echo "  All files have good maintainability"
      fi
      
      # Generate JSON report
      poetry run radon cc --json $CHANGED_PYTHON_FILES > gl-code-quality-report.json 2>/dev/null || echo "{}" > gl-code-quality-report.json
      
      echo ""
      echo "📊 АНАЛИЗ СЛОЖНОСТИ ИЗМЕНЕННОГО КОДА:"
      echo "======================================"
      
      # Check for high complexity (C and above)
      HIGH_COMPLEXITY=$(poetry run radon cc --min C $CHANGED_PYTHON_FILES 2>/dev/null | grep -v "Nothing to analyse" || true)
      
      # Check for low maintainability (C and below)
      LOW_MAINTAINABILITY=$(poetry run radon mi $CHANGED_PYTHON_FILES 2>/dev/null | grep -E " [C-F] " || true)
      
      if [ -n "$HIGH_COMPLEXITY" ] || [ -n "$LOW_MAINTAINABILITY" ]; then
        echo "⚠️  ВНИМАНИЕ: В измененных файлах найдены участки кода с повышенной сложностью"
        echo ""
        echo "💡 Рекомендации:"
        echo "  - Разбейте сложные функции на более мелкие"
        echo "  - Упростите логику в методах с оценкой C и ниже"
        echo "  - Добавьте комментарии к сложным алгоритмам"
        echo ""
        
        if [ -n "$HIGH_COMPLEXITY" ]; then
          echo "📋 Функции с высокой цикломатической сложностью:"
          echo "$HIGH_COMPLEXITY" | sed 's/^/  /'
        fi
        
        if [ -n "$LOW_MAINTAINABILITY" ]; then
          echo "📋 Файлы с низкой поддерживаемостью:"
          echo "$LOW_MAINTAINABILITY" | sed 's/^/  /'
        fi
      else
        echo "✅ Измененный код соответствует стандартам качества!"
      fi
  artifacts:
    reports:
      codequality: gl-code-quality-report.json
    paths:
      - gl-code-quality-report.json
    expire_in: 1 week
  allow_failure: true
  <<: *common-rules

quality-gate:
  stage: quality-gate
  script:
    - |
      echo "=========================================="
      echo "🚀 QUALITY GATE - MERGE READINESS CHECK"
      echo "=========================================="
      echo "📋 Pipeline ID: $CI_PIPELINE_ID"
      echo "🔀 Branch: ${CI_MERGE_REQUEST_SOURCE_BRANCH_NAME:-$CI_COMMIT_BRANCH} → ${CI_MERGE_REQUEST_TARGET_BRANCH_NAME:-$CI_DEFAULT_BRANCH}"
      echo "👤 Author: $GITLAB_USER_NAME"
      echo ""
      
      # Check if all required jobs passed
      echo "✅ Code Formatting (black): PASSED"
      echo "✅ Import Sorting (isort): PASSED"
      echo "✅ Security Scan (bandit): PASSED"
      
      # Only show code metrics status if it was executed
      if [ -n "$CI_MERGE_REQUEST_IID" ]; then
        echo "📊 Code Quality (radon): CHECKED"
      fi
      
      echo ""
      echo "📊 SUMMARY:"
      echo "==========="
      echo "🎯 All critical checks passed"
      echo "💚 Code is ready for review"
      echo ""
      echo "👉 Ready to merge!"
      echo "=========================================="
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  needs:
    - job: black
      optional: false
    - job: isort
      optional: false
    - job: bandit
      optional: false
    - job: code-metrics
      optional: true
  cache:
    policy: pull
  allow_failure: false
```

+ тут для бандита надо добавть .bandit.yaml

```yaml
skips:
  - B101  # assert used in tests
  - B311  # random in test files
  - B112  # try/except pass

exclude_dirs:
  - tests
  - test_*
  - .venv
  - venv
  - env
  - .env

targets:
  - server
  - updater
```

#### Полезные переменные окружения GitLab

| Переменная | Описание |
|------------|----------|
| `CI_COMMIT_SHA` | Хэш коммита |
| `CI_COMMIT_BRANCH` | Имя ветки |
| `CI_COMMIT_TAG` | Имя тега (если есть) |
| `CI_MERGE_REQUEST_IID` | ID MR |
| `CI_PIPELINE_SOURCE` | Триггер (push, web, schedule, etc.) |
| `CI_JOB_STAGE` | Текущий этап |
| `CI_PROJECT_DIR` | Путь к проекту |
| `CI_REGISTRY_IMAGE` | URL образа в GitLab Registry |

---

#### Где хранить секреты

В интерфейсе GitLab: **Settings → CI/CD → Variables**

- `DB_PASSWORD` → защищённая (Protected) переменная  
- `AWS_ACCESS_KEY_ID` → маскированная (Masked)  
- `DEPLOY_TOKEN` → для развёртывания

### Использование в `.gitlab-ci.yml`:

```yaml
deploy:
  script:
    - echo "Deploying with token $DEPLOY_TOKEN"  # В логах будет скрыто
```

Полезные Python-библиотеки для CI/CD
```bash
# requirements-ci.txt
pytest
pytest-cov
pytest-xdist
pytest-benchmark
pytest-html
pytest-instafail
coverage
flake8
black
isort
mypy
ruff
bandit
safety
pip-audit
pre-commit
tox
nox
twine
build
cibuildwheel
```
#### Советы для Python-проектов:

- Используйте .python-version для указания версии
- Кэшируйте poetry.lock для детерминированных сборок
- Настройте coverage с порогом в fail-under
- Добавьте tox.ini для локального тестирования
- Используйте pre-commit для проверок перед коммитом
- Настройте Dependabot для обновления зависимостей
- Включите pyproject.toml вместо setup.py для современных проектов

### Готовые штуки:

#### Если нужны уведы в тг

```yaml
image: python:3.11-slim

stages:
  - notify

.notify-template: &notify
  stage: notify
  script:
    - |
      python -c "
      import requests
      message = '$1'
      url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
      data = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
      requests.post(url, data=data)
      "
  only:
    - main
    - develop
  when: always

notify-start:
  <<: *notify
  script:
    - |
      export MSG="🚀 <b>Pipeline started</b>%0AProject: $CI_PROJECT_NAME%0ABranch: $CI_COMMIT_BRANCH%0ACommit: $CI_COMMIT_SHORT_SHA%0AUser: $GITLAB_USER_NAME"
      python -c "import requests; requests.post('https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage', data={'chat_id': '$TELEGRAM_CHAT_ID', 'text': '$MSG', 'parse_mode': 'HTML'})"
  before_script: []
  only:
    - main

notify-success:
  <<: *notify
  script:
    - |
      export MSG="✅ <b>Pipeline succeeded</b>%0AProject: $CI_PROJECT_NAME%0ABranch: $CI_COMMIT_BRANCH%0ACommit: $CI_COMMIT_SHORT_SHA%0AUser: $GITLAB_USER_NAME%0AURL: $CI_PIPELINE_URL"
      python -c "import requests; requests.post('https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage', data={'chat_id': '$TELEGRAM_CHAT_ID', 'text': '$MSG', 'parse_mode': 'HTML'})"
  before_script: []
  when: on_success

notify-failure:
  <<: *notify
  script:
    - |
      export MSG="❌ <b>Pipeline failed</b>%0AProject: $CI_PROJECT_NAME%0ABranch: $CI_COMMIT_BRANCH%0ACommit: $CI_COMMIT_SHORT_SHA%0AUser: $GITLAB_USER_NAME%0AStage: $CI_JOB_STAGE%0AURL: $CI_PIPELINE_URL"
      python -c "import requests; requests.post('https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage', data={'chat_id': '$TELEGRAM_CHAT_ID', 'text': '$MSG', 'parse_mode': 'HTML'})"
  before_script: []
  when: on_failure
```

#### Мультиверсионное тестирование (Python 3.9-3.12)

```yaml
image: python:3.11

stages:
  - test

.python-test-template: &python-test
  stage: test
  before_script:
    - python -V
    - pip install poetry
    - poetry install
  script:
    - poetry run pytest -v --cov=src
  parallel:
    matrix:
      - PYTHON_IMAGE: 
          - "python:3.9-slim"
          - "python:3.10-slim"
          - "python:3.11-slim"
          - "python:3.12-slim"
        DB:
          - "sqlite"
          - "postgresql"

test-py39-sqlite:
  image: python:3.9-slim
  <<: *python-test
  variables:
    DB_TYPE: "sqlite"
  script:
    - poetry run pytest -v --cov=src --db=sqlite

test-py39-postgres:
  image: python:3.9-slim
  <<: *python-test
  variables:
    DB_TYPE: "postgresql"
  services:
    - postgres:15-alpine
  script:
    - poetry run pytest -v --cov=src --db=postgresql
```

#### Умные правила с изменениями файлов

```yaml
# Запускать тесты только если изменился код
test-backend:
  script: 
    - poetry run pytest
  rules:
    - if: $CI_MERGE_REQUEST_ID
      changes:
        - src/**/*.py
        - tests/**/*.py
        - pyproject.toml
        - poetry.lock
    - if: $CI_COMMIT_BRANCH == "main"
      when: always

# Запускать только если изменились зависимости
update-dependencies:
  script:
    - poetry update
    - poetry run pytest
  rules:
    - changes:
        - poetry.lock
        - pyproject.toml
    - if: $CI_COMMIT_BRANCH == "main"
      when: never

# Пропустить тяжелые тесты для небольших изменений
heavy-tests:
  script:
    - poetry run pytest tests/heavy/
  rules:
    - changes:
        - src/core/**/*.py
        - tests/heavy/**/*.py
      when: on_success
    - if: $CI_COMMIT_BRANCH == "main"
      when: always
    - if: $CI_MERGE_REQUEST_LABELS =~ /full-tests/
      when: always
    - when: never
```

## Плюшки:

**ruff** — супер-линтер (замена flake8 + isort + многие другие)
```bash
ruff check src/                # Проверка
ruff check --fix src/          # Автоисправление
ruff format src/               # Форматирование (как black)
ruff check --select ALL        # Все правила
ruff check --statistics        # Статистика
ruff check --diff src/         # Показать изменения
```

*Для toml file*

```bash
[tool.ruff]
line-length = 120
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # Pyflakes
    "I",   # isort
    "C",   # flake8-comprehensions
    "N",   # pep8-naming
    "B",   # flake8-bugbear
    "UP",  # pyupgrade
    "RUF", # Ruff-specific rules
]
ignore = [
    "E501",  # Line too long (handled by formatter)
    "B008",  # Do not perform function calls in argument defaults
]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]  # Allow unused imports in __init__
"tests/**/*.py" = ["S101"]  # Allow assert in tests

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
```

#### CI-пайплайн со всеми инструментами

```yaml
image: python:3.11-slim

stages:
  - pre-commit
  - lint
  - security
  - test
  - test-matrix
  - build
  - publish

cache:
  paths:
    - .venv/
    - .cache/

before_script:
  - pip install poetry
  - poetry install --no-interaction

pre-commit:
  stage: pre-commit
  script:
    - pip install pre-commit
    - pre-commit run --all-files
  only:
    - merge_requests
    - main

lint:
  stage: lint
  script:
    - ruff check src/ tests/
    - ruff format --check src/ tests/
    - mypy src/
  only:
    - merge_requests
    - main

security:
  stage: security
  script:
    - bandit -r src/ -ll -f json -o bandit.json || true
    - safety check -r requirements.txt --json > safety.json || true
    - pip-audit -r requirements.txt --desc --format json > pip-audit.json || true
  artifacts:
    paths:
      - bandit.json
      - safety.json
      - pip-audit.json
  allow_failure: true

test:
  stage: test
  script:
    - pytest -v --cov=src --cov-report=xml --cov-report=html --junitxml=report.xml
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    paths:
      - htmlcov/
    reports:
      junit: report.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

test-matrix:
  stage: test-matrix
  parallel:
    matrix:
      - PYTHON: ["3.9", "3.10", "3.11", "3.12"]
  image: python:${PYTHON}-slim
  script:
    - pip install poetry
    - poetry install
    - pytest -v --cov=src
  only:
    - main
    - tags

build:
  stage: build
  script:
    - python -m build
    - twine check dist/*
  artifacts:
    paths:
      - dist/
    expire_in: 1 week
  only:
    - tags

publish-testpypi:
  stage: publish
  script:
    - twine upload --repository testpypi --username __token__ --password $TESTPYPI_TOKEN dist/*
  only:
    - develop
  when: manual

publish-pypi:
  stage: publish
  script:
    - twine upload --username __token__ --password $PYPI_TOKEN dist/*
  only:
    - tags
  when: manual
```