"""
Version 4 - Mining, work on data and report are now deeper and splitted
into three method: mine_data takes data from CMC and create a list db;
filtered_data cleans the data and prepare the output strings;
create_report check the internet connection for data mining and
creates teh .json and .txt reports, otherwis creates a log error
.txt file. Chkdir now check the existence of two separete folders
to save the two reports.
Implemented functions to check user's input (currency, delta, date/time).
There's now a function that creates an updated CMC data set.
Defined 3 function that creates filtered and sorted data set from
wich take precise data on the cryptos.
- - - - -
This module allows the creation of instances for background
management -on parallel thread- of recursive scheduling for the
creation of two kind of reports: one is an updated db mined from
CMC and saved in a .json format; the other is a report as required
by the project, saved as .txt file.
User must pass first's execution date (sched_dt, in datetime obj
format), the delta between execution (delta, in timedelta obj format),
a selected currency to express crypto values (currency, string) and,
as optional a path where to save reports and a default folder's name.
A createdir() function is used to chek the accessibility of user
selected folder, as well to create it. Various functions ar provided
for useful analysis on clean data set.
"""

import threading, time, datetime, sched, os, json, requests, sys


class CMCSchedThread(threading.Thread):
    def __init__(self, sched_dt, delta, currency, key, path=None, default_fold='Report'):
        """
The constructor create an instance to perform a scheduled task on a
parallel thread than the main one.
  -sched_dt is the datetime object indicating the first's execution
      date

  -delta is the timedelta object indicating the rythm with wich
      perform the action

  -path is an optional argument indicating the directory where reports
      will be created or a folder name to create in the current path.
      If None a "Report" folder will be created in the same path where
      the script is
"""
        threading.Thread.__init__(self)
        # user defined instance attribute
        self.sched_dt = sched_dt
        self.first_dt = sched_dt
        self.delta = delta
        self.currency = currency
        self.path = path
        self.default_fold = default_fold
        self.key = key
        # default instance attribute
        self.n = 0
        self.n_err = 0
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        self.params = {
            'start': '1',
            'limit': '200',
            'convert': self.currency
        }
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.key
        }
        self.last_CMC_data = []

    def chkdir(self):
        """
Check if the given directory exists. If not create it
"""
        if not os.path.exists(self.path):
            self.path = createdir(self.path, self.default_fold)
        if not os.path.exists(os.path.join(self.path, 'Raw Data')):
            os.makedirs(os.path.join(self.path, 'Raw Data'))
        if not os.path.exists(os.path.join(self.path, 'Reports')):
            os.makedirs(os.path.join(self.path, 'Reports'))

    def mine_data(self):
        """
Mine data from CMC and create a list with the last updated crypto values
"""
        last = requests.get(url=self.url, headers=self.headers, params=self.params).json()
        self.last_CMC_data.clear()
        self.last_CMC_data = last['data']

    def filtered_data(self):
        """
This method calculate the 5 points of the required output e prepare the string to write
in the .txt report file.
"""
        # name of the best volume crypto
        name_b_vol_24 = list(dict(sorted({crypto['name']: crypto['quote'][self.currency]['volume_24h']
                                          for crypto in self.last_CMC_data}.items(), reverse=True,
                                         key=lambda item: item[1])).keys())[0]
        # volume of the best volume crypto
        b_vol_24 = list(dict(sorted({crypto['name']: crypto['quote'][self.currency]['volume_24h']
                                     for crypto in self.last_CMC_data}.items(), reverse=True,
                                    key=lambda item: item[1])).values())[0]
        # it-output for the best volume crypto
        self.str_b_vol = f'\n1. La criptovaluta con il volume maggiore (in {self.currency}) delle ultime 24 ore è "{name_b_vol_24}" con un volume di \
{round(b_vol_24, 2)} {self.currency}.\n'
        # best 10 for % change  24h
        best10_var_24h = dict(list(dict(sorted({crypto['name']: crypto['quote'][self.currency]['percent_change_24h']
                                                for crypto in self.last_CMC_data}.items(), reverse=True,
                                               key=lambda item: item[1])).items())[i] for i in range(10))
        # it-output best 10 for % change iu 24h
        self.best = ['\n2a. Le migliori 10 criptovalute per rendimento nelle ultime 24 ore sono:\n', ]
        for i in range(len(best10_var_24h)):
            self.best.append('     ')
            self.best.append(list(best10_var_24h.keys())[i])
            self.best.append(' : ')
            self.best.append(str(round(list(best10_var_24h.values())[i], 2)))
            self.best.append('%\n')
        # worst 10 for % change in 24h
        worst10_var_24h = dict(list(dict(sorted({crypto['name']: crypto['quote'][self.currency]['percent_change_24h']
                                                 for crypto in self.last_CMC_data}.items(), reverse=False,
                                                key=lambda item: item[1])).items())[i] for i in range(10))
        # it-output worst 10 for % change iu 24h
        self.worst = ['\n2b. Le Peggiori 10 criptovalute per rendimento nelle ultime 24 ore sono:\n', ]
        for i in range(len(worst10_var_24h)):
            self.worst.append('     ')
            self.worst.append(list(worst10_var_24h.keys())[i])
            self.worst.append(' : ')
            self.worst.append(str(round(list(worst10_var_24h.values())[i], 2)))
            self.worst.append('%\n')
        # best 20 by market cap and their prices
        best20_mktcap_and_price = dict(
            list(dict(sorted({crypto['quote'][self.currency]['market_cap']: crypto['quote'][self.currency]['price']
                              for crypto in self.last_CMC_data}.items(), reverse=True,
                             key=lambda item: item[0])).items())[i] for i in range(20))
        # investiment required to buy one coin each
        money_for_best20_mktcap = 0
        for prices in best20_mktcap_and_price.values():
            money_for_best20_mktcap += prices
        # it-output investiment to buy one each of the 20s best by market cap
        self.str_b20_mktcap = f'\n3. La quantità di denaro necessaria per acquistare una unità di ciascuna delle prime 20 criptovalute per capitalizzazione \
è {round(money_for_best20_mktcap, 2)} {self.currency}.\n'
        # volume above 76000000 and their prices
        vol_and_price = {crypto['quote'][self.currency]['volume_24h']: crypto['quote'][self.currency]['price']
                         for crypto in self.last_CMC_data if crypto['quote'][self.currency]['volume_24h'] > 76000000}
        # investiment required to buy one coin each
        money_for_more_76k = 0
        for prices in vol_and_price.values():
            money_for_more_76k += prices
        # it-output investiment to buy one each of the cryptos with a volume above 76000000
        self.str_money_for_more_76k = f'\n4. Per acquistare una unità di tutte le criptovalute con volume superiore a 76000000 {self.currency} nelle ultime 24 \
ore occorrono {round(money_for_more_76k, 2)} {self.currency}.\n'

        # best 20 by market cap with their 24h % change, today's prices and yesterday's prices

        def p_yes(pr, v):  # function to get yesterday's price
            return pr / (1 + (v / 100))
        # alternative
        # p_yes = lambda pr, v: pr / (1 + (v / 100))

        best20_mkt_var24h_price_t_y = dict(list(dict(sorted({crypto['quote'][self.currency]['market_cap']:
                                                                 {'var_24h': crypto['quote'][self.currency][
                                                                     'percent_change_24h'],
                                                                  'price_today': crypto['quote'][self.currency][
                                                                      'price'],
                                                                  'price_yesterday': p_yes(
                                                                      crypto['quote'][self.currency]['price'],
                                                                      crypto['quote'][self.currency][
                                                                          'percent_change_24h'])}
                                                             for crypto in self.last_CMC_data}.items(), reverse=True,
                                                            key=lambda item: item[0])).items())[i] for i in range(20))
       
        # sum of yesterday's prices
        sum_p_y = 0
        for i in range(len(best20_mkt_var24h_price_t_y)):
            sum_p_y += list(best20_mkt_var24h_price_t_y.values())[0]['price_yesterday']
        # sum of today's prices
        sum_p_t = 0
        for i in range(len(best20_mkt_var24h_price_t_y)):
            sum_p_t += list(best20_mkt_var24h_price_t_y.values())[0]['price_today']
        # it-output 24h % change on '20s best by market cap' portfolio
        gain_24h = ((sum_p_t - sum_p_y) / sum_p_y)
        self.str_gain_24h = f'\n5. La variazione percentuale realizzata se avessimo comprato ieri le 20 cripto a maggior capitalizzazione di oggi sarebbe \
stata {round(gain_24h * 100, 2)}%.'

    def create_report(self):
        """
Thi method begin updating data from CMC, than agregate it for the required report and
create a .json file to store the db and a .txt data to report the analysis.
Finally it updates the datetime object for the next event to schedule and update the
number of report created till now.
"""
        try:
            self.mine_data()  # mine updated data from CMC
            self.filtered_data()  # aggregate data for report
            dt = datetime.datetime.now().strftime('%d-%m-%Y_%H.%M')  # current time
            self.chkdir()  # check directory

            # create a json updated offline db
            db_name = str(f'CMC_data ({dt}).json')  # db's name
            db_path = os.path.join(self.path, 'Raw Data', db_name)  # db's path
            with open(db_path, 'w') as new_db:
                json.dump(self.last_CMC_data, new_db, indent=2)

            # create a txt updated report as required
            r_name = str(f'Crypto_report ({dt}).txt')  # report's name
            r_path = os.path.join(self.path, 'Reports', r_name)  # report's path
            with open(r_path, 'w') as new_r:
                new_r.write(
                    f'\n* * * REPORT DEL GIORNO {datetime.datetime.now().strftime("%d/%m/%Y")} ORE {datetime.datetime.now().strftime("%H:%M")} * * *\n')
                new_r.write(self.str_b_vol)
                new_r.writelines(self.best)
                new_r.writelines(self.worst)
                new_r.write(self.str_b20_mktcap)
                new_r.write(self.str_money_for_more_76k)
                new_r.write(self.str_gain_24h)

            self.sched_dt += self.delta  # next scheduled date/time
            self.n += 1  # number of scheduled event completed

        except requests.exceptions.RequestException:
            delta_err = datetime.timedelta(minutes=15)
            self.sched_dt += min(delta_err, self.delta)
            self.chkdir()
            dt = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
            err_name = str('Log_error.txt')
            err_path = os.path.join(self.path, err_name)
            with open(err_path, 'a') as err_f:
                err_f.write(f'Errore di connessione in data {dt}. Nuovo tentativo in data {self.sched_dt.strftime("%d-%m-%Y %H:%M:%S")}.\n')
            self.n_err += 1

    def run(self):
        """
The override run method starts the scheduler, following the rules
given with the argumets
"""
        self.path = createdir(self.path, self.default_fold)  # create folder on 1st run
        while True:
            _ = self.scheduler.enterabs(self.sched_dt.timestamp(), 0, self.create_report)
            self.scheduler.run()

    def __repr__(self):
        return f'<Class \'CMCSchedThread\' delta={self.delta} next_schedule={self.sched_dt}>'

    @staticmethod
    def info_it():
        """
Informazioni sulla classe in ITALIANO
"""
        info = 'Questo è un modulo di prova che permette la creazione di istanze \
per la gestione in background (su un thread parallelo) di pianificazioni ricorsive \
per la creazione di report (in questa versione un report .txt vuoto). Definita una \
data per la prima pianificazione (sched_dt, oggetto datetime.datetime) verrà \
creato un report ogni delta (secondi, minuti, ore, giorni, ecc..) a partire dalla \
prima data indicata. I report vengono salvati nella cartella richiesta o in una di\
default, creata all\'indirizzo dello script.'
        return print(info)


def check_key():
    """
Check user CMC key
"""
    key = str(input('Inserisci la tua chiave CMC per avviare il programma.\n>'))
    try:
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        params = {
                'start': '1',
                'limit': '1',
                'convert': 'USD'
                 }
        headers = {
                'Accepts': 'application/json',
                'X-CMC_PRO_API_KEY': key
                }
        resp = requests.get(url=url, headers=headers, params=params)
        if resp.status_code != 200:
            input('Chiave non valida,\npremere un tasto qualsiasi per terminare il programma. . .')
            sys.exit()
        else: pass
    except requests.exceptions.RequestException:
        input('Errore di comunicazione con il server,\npremere un tasto qualsiasi per terminare il programma. . .')
        sys.exit()
    return key
    

def createdir(directory, default='Report'):
    """
Check if a directory exists. If doesn't it try to create it.
If the directory is inaccessible or ungiven, create a folder
in the current path named default (Report by default)
"""
    while True:
        if directory is None or not directory:  # if a directory is not given, then
            directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), default)
            if not os.path.exists(directory):  # if it doesn't exist
                os.makedirs(directory)  # create the default one
            return directory
        elif not os.path.exists(directory):  # if dir doesn't exist, then
            try:  # try to create it
                directory = os.path.normpath(directory)
                os.makedirs(directory)
                with open(os.path.join(directory, 'try.txt'), 'w'):
                    pass
                os.remove(os.path.join(directory, 'try.txt'))
                return directory
            except Exception:  # if dir impossible to create try with the default one
                directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), default)
                if not os.path.exists(directory):  # if it doesn't exist create it
                    os.makedirs(directory)
                return directory
        elif os.path.exists(directory):  # if dir does exist, then
            try:  # verify its accessibility
                with open(os.path.join(directory, 'try.txt'), 'w'):
                    pass
                os.remove(os.path.join(directory, 'try.txt'))
                return directory
            except Exception:  # if dir impossible to create try with the default one
                directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), default)
                if not os.path.exists(directory):  # if it doesn't exist create it
                    os.makedirs(directory)
                return directory


def chkcur(allowed_curr):
    currency = str(input('\nIn quale valuta vuoi espressi i valori delle criptovalute? \
\nPremi invio per impostare la valuta di default(USD).\n>')).upper()
    while True:
        if not currency:
            currency = 'USD'
        if currency in allowed_curr:
            break
        else:
            currency = str(input(f'{currency} non è una valuta disponibile. Scegline \
un\'altra o premi invio per\nimpostare la valuta di default (USD).\n>')).upper()
            continue
    return currency


def chkdelta():
    delta = input('Ogni quante ore vuoi scaricare i dati? Premi invio per selezionare \
\nl\'intervallo di default (24 ore).\n>')
    while True:
        if not delta:
            delta = datetime.timedelta(hours=24)
            break
        try:
            if ',' in str(delta):
                delta = str(delta).replace(',', '.')
            delta = datetime.timedelta(hours=float(delta))
            break
        except ValueError:
            delta = input('L\'intervallo deve essere espresso in valore numerico. \
Riprova o premi\ninvio per impostare l\'intervallo di default (24 ore).\n>')
            continue
    return delta


def strdelta(delta):
    if delta.days == 0:
        if delta.seconds / 3600 == 1:
            _delta = '1 ora'
        else:
            _delta = f'{int(delta.seconds / 3600)} ore'
    elif delta.days == 1:
        if delta.seconds / 3600 == 0:
            _delta = '1 giorno'
        elif delta.seconds / 3600 == 1:
            _delta = '1 giorno e 1 ora'
        else:
            _delta = f'1 giorno e {int(delta.seconds / 3600)} ore'
    else:
        if delta.seconds / 3600 == 0:
            _delta = f'{delta.days} giorni'
        elif delta.seconds / 3600 == 1:
            _delta = f'{delta.days} giorni e 1 ora'
        else:
            _delta = f'{delta.days} giorni e {int(delta.seconds / 3600)} ore'
    return _delta


def chkdate():
    date_fs = str(input('In che data vuoi creare il primo ciclo di report?\
\nPremi invio per scegliere la data di oggi.\n>')).replace('\\', '/')
    if len(date_fs.rsplit('/')[-1]) == 2:
        date_fs = date_fs.rsplit('/')[0] + '/' + date_fs.rsplit('/')[1] + '/20' + date_fs.rsplit('/')[2]
    while True:
        if not date_fs:
            date_fs = datetime.datetime.now().strftime('%d/%m/%Y')
        try:
            type(datetime.datetime.strptime(date_fs, '%d/%m/%Y')) is datetime.datetime
            break
        except ValueError:
            date_fs = str(input('Il formato data inserito è errato. Utilizza il formato \
gg/mm/aaaa o\npremi invio per scegliere la data di oggi.\n>')).replace('\\', '/')
            if len(date_fs.rsplit('/')[-1]) == 2:
                date_fs = date_fs.rsplit('/')[0] + '/' + date_fs.rsplit('/')[1] + '/20' + date_fs.rsplit('/')[2]
            continue
    return date_fs


def chktime():
    time_fs = str(input('A che ora vuoi creare il primo ciclo di report?\
\nPremi invio per scegliere l\'ora corrente.\n>')).replace('.', ':')
    while True:
        if not time_fs:
            time_fs = (datetime.datetime.now() + datetime.timedelta(minutes=1)).strftime('%H:%M')
        try:
            type(datetime.datetime.strptime(time_fs, '%H:%M')) is datetime.datetime
            break
        except ValueError:
            time_fs = str(input('Il formato ora inserito è errato. Utilizza il formato \
ore:minuti o\npremi invio per scegliere l\'ora corrente.\n>')).replace('.', ':')
            continue
    return time_fs


def update_cmc(currency, key):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    params = {
        'start': '1',
        'limit': '200',
        'convert': currency
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': key
    }
    upd = requests.get(url=url, headers=headers, params=params).json()
    return upd['data']


def crypto_data(cmc_data, currency):
    """
creates a clean db with unfiltered data
"""
    return {f'{crypto["name"]} ({crypto["symbol"]})': {'price': crypto['quote'][currency]['price'],
                                                       'volume_24h': crypto['quote'][currency]['volume_24h'],
                                                       'market_cap': crypto['quote'][currency]['market_cap'],
                                                       'market_cap_dominance': crypto['quote'][currency]['market_cap_dominance'],
                                                       'percent_change_1h': crypto['quote'][currency]['percent_change_1h'],
                                                       'percent_change_24h': crypto['quote'][currency]['percent_change_24h'],
                                                       'percent_change_7d': crypto['quote'][currency]['percent_change_7d'],
                                                       'percent_change_30d': crypto['quote'][currency]['percent_change_30d'],
                                                       'percent_change_60d': crypto['quote'][currency]['percent_change_60d'],
                                                       'percent_change_90d': crypto['quote'][currency]['percent_change_90d']
                                                       } for crypto in cmc_data}


def filtered_major_data(cmc_data, currency, thr_data, threshold, asc_desc=None):
    """
creates a clean db with filtered (greater than a threshold) and ordered data.
-thr_data is the type of data you need to order (price, vol_24h, mkt_cap, ect..
-threshold is a float
-asc_desc is a boolean for the reverse argument
"""
    return dict(sorted({f'{crypto["name"]} ({crypto["symbol"]})': {'price': crypto['quote'][currency]['price'],
                                                                   'volume_24h': crypto['quote'][currency]['volume_24h'],
                                                                   'market_cap': crypto['quote'][currency]['market_cap'],
                                                                   'market_cap_dominance': crypto['quote'][currency]['market_cap_dominance'],
                                                                   'percent_change_1h': crypto['quote'][currency]['percent_change_1h'],
                                                                   'percent_change_24h': crypto['quote'][currency]['percent_change_24h'],
                                                                   'percent_change_7d': crypto['quote'][currency]['percent_change_7d'],
                                                                   'percent_change_30d': crypto['quote'][currency]['percent_change_30d'],
                                                                   'percent_change_60d': crypto['quote'][currency]['percent_change_60d'],
                                                                   'percent_change_90d': crypto['quote'][currency]['percent_change_90d']
                                                                   } for crypto in cmc_data if
                        crypto['quote'][currency][thr_data] > threshold}.items(),
                       key=lambda item: item[1][thr_data], reverse=asc_desc))


def filtered_minor_data(cmc_data, currency, thr_data, threshold, asc_desc=None):
    """
creates a clean db with filtered (lesser than a threshold) and ordered data.
-thr_data is the type of data you need to order (price, vol_24h, mkt_cap, ect..
-threshold is a float
-asc_desc is a boolean for the reverse argument
"""
    return dict(sorted({f'{crypto["name"]} ({crypto["symbol"]})': {'price': crypto['quote'][currency]['price'],
                                                                   'volume_24h': crypto['quote'][currency]['volume_24h'],
                                                                   'market_cap': crypto['quote'][currency]['market_cap'],
                                                                   'market_cap_dominance': crypto['quote'][currency]['market_cap_dominance'],
                                                                   'percent_change_1h': crypto['quote'][currency]['percent_change_1h'],
                                                                   'percent_change_24h': crypto['quote'][currency]['percent_change_24h'],
                                                                   'percent_change_7d': crypto['quote'][currency]['percent_change_7d'],
                                                                   'percent_change_30d': crypto['quote'][currency]['percent_change_30d'],
                                                                   'percent_change_60d': crypto['quote'][currency]['percent_change_60d'],
                                                                   'percent_change_90d': crypto['quote'][currency]['percent_change_90d']
                                                                   } for crypto in cmc_data if
                        crypto['quote'][currency][thr_data] < threshold}.items(),
                       key=lambda item: item[1][thr_data], reverse=asc_desc))
