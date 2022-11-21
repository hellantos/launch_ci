from asyncio.subprocess import PIPE, STDOUT
from subprocess import Popen
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

def get_commit_count_since_before(since: date, before: date) -> int:
    since_arg = "--since={}-{}-{}".format(since.year, since.month, since.day)
    until_arg = "--before={}-{}-{}".format(before.year, before.month, before.day)
    cmd = ["/usr/bin/git", "rev-list", "--count", since_arg, until_arg, "HEAD"]
    obj = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT, cwd="/home/christoph/ws_ros2/src/launch_ros", start_new_session=True)
    stdout, stderr = obj.communicate()
    return int(stdout)

def get_first_commit_date() -> date:
    cmd = ["/usr/bin/git", "log", "--reverse", "--format=%cd", "--date=short"]
    obj = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT, cwd="/home/christoph/ws_ros2/src/launch_ros", start_new_session=True)
    stdout, stderr = obj.communicate()
    lines = stdout.splitlines()
    f = lines[0].decode('utf-8').split("-")
    first_commit_date = date(int(f[0]), int(f[1]), int(f[2]))
    return first_commit_date

def get_monthly_commits():
    first_commit = get_first_commit_date()
    commits_per_month = []
    month_start = date(first_commit.year, first_commit.month, 1)
    month_end = month_start + relativedelta(months=1)
    while(month_end < date.today()):
        commits_per_month.append(get_commit_count_since_before(since=month_start, before=month_end))
        month_start = month_end
        month_end = month_start + relativedelta(months=1)
    return commits_per_month



a = get_monthly_commits()


for item in a:
    print(item)