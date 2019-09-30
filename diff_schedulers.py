
import os	
import pandas.io.data as web
import datetime as dt
from apscheduler.schedulers.blocking import BlockingScheduler

def download_SPX():
    s_dir = os.getcwd() + '/' + date.strftime('%Y-%m-%d')
    start = dt.datetime(1990,1,1)
    f = web.DataReader("^GSPC", 'yahoo', start, dt.date.today()).fillna('NaN')
    f.to_csv(s_dir+'/SPX.csv', date_format='%Y%m%d')	
	
def main():
    sched = BlockingScheduler()
    @sched.scheduled_job('cron', day_of_week='mon,tue,wed,thu,fri,sat', hour=23)
    def scheduled_job():
    	print('[INFO] Job started.')
        download_SPX()
        print('[INFO] Job ended.')

    sched.start()    

if __name__ == '__main__':
	main()
