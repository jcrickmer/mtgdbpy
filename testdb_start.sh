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

source /home/jason/venvs/mtgdb/bin/activate
alias fasttest='./manage.py test --settings=mtgdb.settings_test'
echo "alias 'fasttest' created."
echo "Completed!"
