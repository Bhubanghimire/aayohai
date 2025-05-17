rm -r system/migrations
rm -r accounts/migrations
rm -r room/migrations
rm -r events/migrations
rm -r grocery/migrations
rm -r book/migrations
rm -r payment/migrations


rm db.sqlite3

pip install -r requirements.txt

python manage.py makemigrations system accounts room events grocery book payment
python manage.py migrate
python manage.py loaddata system/initial_fixtures/initial_fixtures.json
#python manage.py loaddata accounts/initial_fixtures/initial_fixtures.json
