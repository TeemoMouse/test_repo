CD "projects\%1\public"
git add .
git commit -a --allow-empty-message -m ''
git branch -M %2
git remote add origin %3
git pull origin %2 --allow-unrelated-histories
git push -u origin %2 -f