#!/bin/bash -xEe

echo "Shutting down MySQL..."
kill `cat /tmp/testramdisk/mysqld.pid` && sleep 6
echo "Unmounting ramdisk..."
umount /tmp/testramdisk

rm -rf /tmp/testramdisk
echo "Completed!"
