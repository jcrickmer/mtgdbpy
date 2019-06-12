#!/bin/bash -xEe

USE_RAMDISK=0

rm -rf /tmp/testramdisk
mkdir /tmp/testramdisk

if [ $USER_RAMDISK -ne 0 ]; then
    echo "Creating ramdisk..."
    mount -t tmpfs -o size=512m tmpfs /tmp/testramdisk
fi

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
MYSQL_USER_PARAM=
#chown -R mysql.mysql /tmp/testramdisk

echo "Initializing MySQL..."
mysql_install_db $MYSQL_USER_PARAM --datadir="/tmp/testramdisk/data"

mysqld_safe --defaults-file=/tmp/testramdisk/my.cnf &
sleep 3
mysqladmin -S /tmp/testramdisk/mysql.sock -u root password tester

echo "Running tests..."
source /home/jason/venvs/mtgdb2/bin/activate

TESTS=()
TESTS+=('cards.tests.helpertests')
TESTS+=('cards.tests.tests')
TESTS+=('cards.tests.cardmanagertests')
TESTS+=('cards.tests.filingstringtests')
TESTS+=('cards.tests.loadertests')
TESTS+=('cards.tests.searchtests')
TESTS+=('cards.tests.nametests')
TESTS+=('decks.tests.tests')
TESTS+=('decks.tests.parsertests')
TESTS+=('decks.tests.stattests')
TESTS+=('cards.tests.formattests')

for test_name in "${TESTS[@]}"
do
    ./manage.py test --settings=mtgdb.settings_test $test_name || break
#    if [ $? -ne 0 ]; then
#        break
#    fi
done

echo "Tests completed!"
echo "Shutting down MySQL..."
kill `cat /tmp/testramdisk/mysqld.pid` && sleep 6

if [ $USER_RAMDISK -ne 0 ]; then
    echo "Unmounting ramdisk..."
    umount /tmp/testramdisk
fi

rm -rf /tmp/testramdisk
echo "Completed!"
