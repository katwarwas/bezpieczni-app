import pandas as pd
import numpy as np 
import base64
from io import BytesIO
from datetime import datetime
import matplotlib.pyplot as plt

def string_to_date(date_str):
        return datetime.strptime(date_str, "%Y-%m-%d").date()

def image_base64():

    df = pd.read_csv('cyberattacks.csv')

    date_str= np.array(df['event_date'])

    vectorized_string_to_date = np.vectorize(string_to_date)
    dates = vectorized_string_to_date(date_str)

    year_event = dates.astype('datetime64[Y]')
    year_event_str = year_event.astype('str')
    year_events = year_event_str[year_event_str.astype('int')>2000]
    year_events_name = np.unique(year_events)
    xlabel = year_events_name
    year_events_count = pd.DataFrame(pd.DataFrame(year_events).value_counts()).sort_index().values
    fig, ax = plt.subplots()
    fig.patch.set_facecolor('#232323')
    ax.plot(xlabel, year_events_count, marker = 'o', color='#92B6FC')
    ax.set_frame_on(False)
    ax.set_xlabel('Rok', color='white')
    ax.set_ylabel('Liczba ataków', color='white')
    ax.tick_params(axis='both', colors='white')
    ax.set_ylim(0, 4000)
    plt.title('Liczba ataków w danym roku', fontsize=20, color='white')


    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()


    return base64.b64encode(image_png).decode('utf-8')
