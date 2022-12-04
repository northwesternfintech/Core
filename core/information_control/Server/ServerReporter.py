import psutil
import SlackBot


def reportServerInfo():
    """Called hourly to report server information to Slack"""
    cpuUtil = str(psutil.cpu_percent(interval=1))
    ramUtil = str(psutil.virtual_memory().percent)
    SlackBot.slack_bot(cpuUtil, ramUtil)


if __name__ == "__main__":
    reportServerInfo()
