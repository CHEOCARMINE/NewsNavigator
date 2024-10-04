from celery import Celery

# Configurar la aplicación Celery
app = Celery('news_scraper', broker='redis://localhost:6379/0')

app.conf.beat_schedule = {
    'scrape-every-30-minutes': {
        'task': 'manage.run_scraper',
        'schedule': 1800.0,  
    },
}

app.conf.timezone = 'UTC'
