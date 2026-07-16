# ⚡ Git Cheatsheet - коротко и по делу

### Настройка

- git config --global user.name "Name" — задать имя  
- git config --global user.email "email" — задать почту  
- git config --list — показать настройки  

### Старт

git init — создать репозиторий  
git clone url — клонировать репо  

### Стейджинг и коммиты

git status — статус  
git add . — добавить все изменения  
git reset file — убрать из стейджа  
git commit -m "msg" — коммит  
git commit --amend — исправить последний коммит  

### Ветки

git branch — список  
git branch name — создать  
git checkout -b name — создать и перейти  
git branch -d name — удалить  

### Merge и Rebase

git merge branch — слить ветку  
git merge --abort — отменить  
git rebase branch — перебазирование  

### История

git log --oneline — компактная история  
git log --graph --all — граф  
git diff — показать изменения  

### Откат

git restore file — вернуть файл  
git reset --soft HEAD~1 — откатить коммит, сохранить изменения  
git reset --hard HEAD~1 — откатить и удалить изменения  
git clean -f — удалить лишние файлы  

### Удалённые репозитории

git remote -v — список  
git push origin branch — запушить  
git pull — получить изменения  
git fetch — только забрать  

### Теги

git tag — список  
git tag name — создать  
git push origin --tags — отправить теги  

### Stash

git stash — сохранить изменения  
git stash list — список  
git stash apply — применить  

### Поиск и анализ

git blame file — кто менял строки  
git grep "text" — поиск  
git bisect — бинарный поиск бага  

### Продвинутое

git cherry-pick commit — взять коммит  
git revert commit — отменить коммит через новый  
git submodule add url — добавить сабмодуль  