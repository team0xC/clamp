# Useful commands for File System and User Investigations

## File System Investigation
>__find / -type d -name ".*"__        (List all hidden directories)

>__lsattr / -R 2> /dev/null | grep "\----i"__    (Immutable files and directories)

>__find / -type f \( -perm -04000 -o -perm -02000 \) -exec ls -lg {} \;__    (Find SUID/SGID files)

>__find / \( -nouser -o -nogroup \) -exec ls -lg  {} \;__     (Files/Dirs with no user/group name)

>__file * -p__     (List all file types in current dir)

>__find / -type f -exec file -p '{}' \; |  grep ELF__      (Find executables anywhere)

>__find /tmp -type f -exec file -p '{}' \; |  grep ELF__     (Find executables in /tmp)

>__find / -mtime -1__        (Find files modified/created within last day)

__Persistence areas__
/etc/rc.local, /etc/initd, /etc/rc*.d, /etc/modules, /etc/cron*, /var/spool/cron/*    

>__rpm -Va | grep ^..5.__     (Package command to find changed files)

>__debsums -c__         (Package command to find changed files)

>__grep [[:cntrl:]] /var/log/*.log__       (Find logs with binary in them)

>__ls -al /var/log/*__            (Check for zero size logs)

## Procfs  
Proc file system (procfs) is virtual file system created on fly when system boots and is dissolved at time of system shut down. It contains useful information about the processes that are currently running, it is regarded as control and information center for kernel. The proc file system also provides communication medium between kernel space and user space.

>ls -l /proc | grep '^d'  __(List of directories with PIDs)__

>ls -ltr /proc/7494    __(Entries for a specific PIDs)__

>find /proc -name comm -exec cat "{}" \; 2>/dev/null |sort -u    __(Sorted list of running processes)__

>ls -alR /proc/*/exe 2> /dev/null |  grep deleted       __(Deleted binaries still running)__

>ls -al /proc/<PID>/exe      __(Real process path)__

strings /proc/<PID>/environ    __(Process environment)__

>ls -alR /proc/*/cwd      __(Process working directory)__

>ls -alR /proc/*/cwd 2> /dev/null | grep tmp   __(Process running from tmp folder)__

>ls -alR /proc/*/cwd 2> /dev/null | grep dev   __(Process running from dev folder)__

# Users Investigation

>find / -name authorized_keys      (Find all ssh authorized_keys files)

>find / -name .*history       __(History files for users)__

>ls -alR / 2> /dev/null | grep .*history |  grep null     __(History files linked to /dev/null)__

>grep ":0:" /etc/passwd      __(Look for UID/ 0/ GID 0)__

>cat /etc/sudoers and /etc/group      __(check sudoers file)__

crontab -l        __(Check scheduled tasks)__

>atq             __(Check scheduled tasks)__

>systemctl list-timers  --all     __(Check scheduled tasks)__
