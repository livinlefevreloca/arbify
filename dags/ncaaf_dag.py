from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator

from tasks import *


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2018, 4, 1),
    'email': ['adamtlefevre@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
}


ncaaf_dag = DAG('ncaaf_dag',
                  default_args=default_args,
                  schedule_interval=timedelta(mins=2),
                  catchup=False
                  )


scrape_bovada_task = PythonOperator(
                   task_id='scrape_bovada',
                   provide_context=True,
                   python_callable=get_bovada_ncaaf,
                   params={"sport": "ncaaf"},
                   dag=ncaaf_dag
                   )

scrape_betonline_task = PythonOperator(
                   task_id='scrape_betonline',
                   provide_context=True,
                   python_callable=get_betonline_ncaaf,
                   params={"sport": "ncaaf"},
                   dag=ncaaf_dag
                   )

scrape_interops_task = PythonOperator(
                   task_id='scrape_interops',
                   provide_context=True,
                   python_callable=get_interops_ncaaf,
                   params={"sport": "ncaaf"},
                   dag=ncaaf_dag
                   )


scrape_youwager_task = PythonOperator(
                   task_id='scrape_youwager',
                   provide_context=True,
                   python_callable=get_youwager_ncaaf,
                   params={"sport": "ncaaf"},
                   dag=ncaaf_dag
                   )
scrape_sportsbetting_task =  PythonOperator(
                   task_id='scrape_sportsbetting',
                   provide_context=True,
                   python_callable=get_sportsbetting_ncaaf,
                   params={"sport": "ncaaf"},
                   dag=ncaaf_dag
                   )


# Clean data frames coming out of the scrapers

clean_betonline_task = PythonOperator(
                    task_id='clean_betonline',
                    provide_context=True,
                    python_callable=clean_ncaaf,
                    params={"task_id": "scrape_betonline"},
                    dag=ncaaf_dag
                    )

clean_bovadad_task = PythonOperator(
                    task_id='clean_bovada',
                    provide_context=True,
                    python_callable=clean_ncaaf,
                    params={"task_id": "scrape_bovada"},
                    dag=ncaaf_dag
                    )

clean_interops_task = PythonOperator(
                    task_id='clean_interops',
                    provide_context=True,
                    python_callable=clean_ncaaf,
                    params={"task_id": "scrape_interops"},
                    dag=ncaaf_dag
                    )

clean_youwager_task = PythonOperator(
                    task_id='clean_youwager',
                    provide_context=True,
                    python_callable=clean_ncaaf,
                    params={"task_id": "scrape_youwager"},
                    dag=ncaaf_dag
                    )

clean_sportsbetting_task = PythonOperator(
                    task_id='clean_sportsbetting',
                    provide_context=True,
                    python_callable=clean_ncaaf,
                    params={"task_id": "scrape_sportsbetting"},
                    dag=ncaaf_dag
                    )
