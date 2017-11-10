#!/bin/bash -xEe

rm -rf /tmp/testramdisk
mkdir /tmp/testramdisk

echo "Creating ramdisk..."
mount -t tmpfs -o size=512m tmpfs /tmp/testramdisk

echo "[mysqld]" > /tmp/testramdisk/my.cnf
echo "datadir=/tmp/testramdisk/data" >> /tmp/testramdisk/my.cnf
mkdir /tmp/testramdisk/data
echo "port=13006" >> /tmp/testramdisk/my.cnf
echo "socket=/tmp/testramdisk/mysql.sock" >> /tmp/testramdisk/my.cnf
echo "user=mysql" >> /tmp/testramdisk/my.cnf
echo "default_storage_engine = InnoDB" >> /tmp/testramdisk/my.cnf
echo "character-set-server = utf8" >> /tmp/testramdisk/my.cnf
echo "character-set-filesystem = utf8" >> /tmp/testramdisk/my.cnf
echo "[mysqld_safe]" >> /tmp/testramdisk/my.cnf
echo "log-error=/tmp/testramdisk/mysqld.log" >> /tmp/testramdisk/my.cnf
echo "pid-file=/tmp/testramdisk/mysqld.pid" >> /tmp/testramdisk/my.cnf
chown -R mysql.mysql /tmp/testramdisk

echo "Initializing MySQL..."
mysql_install_db --user=mysql --datadir="/tmp/testramdisk/data"

mysqld_safe --defaults-file=/tmp/testramdisk/my.cnf &
sleep 3
mysqladmin -S /tmp/testramdisk/mysql.sock -u root password tester

echo "Running tests..."
source /home/jason/mtgdb/bin/activate

./manage.py test --settings=mtgdb.settings_test cards.tests.helpertests && ./manage.py test --settings=mtgdb.settings_test cards.tests.tests && ./manage.py test --settings=mtgdb.settings_test cards.tests.filingstringtests && ./manage.py test --settings=mtgdb.settings_test cards.tests.loadertests && ./manage.py test --settings=mtgdb.settings_test cards.tests.searchtests && ./manage.py test --settings=mtgdb.settings_test cards.tests.nametests && ./manage.py test --settings=mtgdb.settings_test decks.tests.tests && ./manage.py test --settings=mtgdb.settings_test decks.tests.parsertests && ./manage.py test --settings=mtgdb.settings_test decks.tests.stattests

echo "Tests completed!"
echo "Shutting down MySQL..."
kill `cat /tmp/testramdisk/mysqld.pid` && sleep 6
echo "Unmounting ramdisk..."
umount /tmp/testramdisk

rm -rf /tmp/testramdisk
echo "Completed!"
