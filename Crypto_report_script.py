import BCpython, datetime, requests, sys

# Scheduling script
print('''
       - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
- - - | Benvenuti nel programma di Reportistica e Analisi Criptovalute  | - - -
       - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n
|  Compito di questo script è di creare una reportistica standard ricorsiva   |
|  pianificata dall'utente e gestita in background dal programma stesso; nel  |
|    mentre è data la possibilità di analizzare diverse informazioni sulle    |
|  criptovalute presenti sul portale CoinMarketCap. Una volta iniziallizato   |
|  il programma verrà chiesto in quale valuta scaricare i dati (le prime 200  |
|    criptovalute per capitalizzazione presenti su CMC), di indicare dove     |
|      salvare i report (un database in formato .json e un cruscotto in       |
|   formato .txt) e definire la frequenza e la data di inizio degli stessi.   |\n|                                                                             |
|    Pianificate queste operazioni si potranno ricavare altri dati sulle      |
|   criptovalute, di volta in volta relativi all'ultimo aggiornamento CMC o   |
|                         all'ultimo database salvato.                        |\n                      
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
''')

key = BCpython.check_key()

while True:
    # CURRENCY input    
    allowed_curr = ('USD', 'EUR', 'GBP', 'BTC', 'ETH', 'RUB', 'CNY', 'JPY', 'CUP', 'BRL')
    currency = BCpython.chkcur(allowed_curr)
    # PATH input
    directory = input('Dove vuoi salvare i report? Premi invio per selezionare la \
cartella di \ndefault, che verrà creata nel percorso corrente.\n>')
    if not directory:
        _directory = 'di default'
    else:
        _directory = str('"' + directory + '"')

    # DELTA input
    delta = BCpython.chkdelta()

    # first date scheduling input
    date_fs = BCpython.chkdate()

    # first time scheduling input        
    time_fs = BCpython.chktime()

    # FIRST SCHEDULING datetime obj
    dt_fs = datetime.datetime.strptime(str(date_fs + ' ' + time_fs), '%d/%m/%Y %H:%M')

    play = input(f'\n* * *\n* Hai deciso di realizzare dei report in {currency} ogni \
{BCpython.strdelta(delta)} a partire\n* dalle {dt_fs.strftime("%H:%M")} del \
{dt_fs.strftime("%d/%m/%Y")} e di salvarli nella cartella\n* {_directory}.\n* * *\n\
\nPremi invio per avviare la pianificazione o un tasto qualsiasi\
\nper modificare le tue scelte.\n>')

    if play != '':  # modify user choices
        continue
    else:  # check if datetime is plannable
        if dt_fs > datetime.datetime.now():
            reporting = BCpython.CMCSchedThread(sched_dt=dt_fs, delta=delta,
                                                currency=currency, path=directory, key=key)
            reporting.start()       
            input('\n* * *\n* Il programma di reportistica è stato pianificato, d\'ora in \
avanti\n* proseguirà in background, permettendoti di effettuare ulteriori analisi\n* sui \
dati scaricati o, se prefirisci, aggiornandoli.\n* * *\n\nPremi invio per proseguire al programma di analisi.\n>')
            break
        else:
            while True:
                dt_err = input('\nLa data inserita non è valida in quanto precedente all\'ora attuale.\
\nPremi invio per avviare la pianificazione alla prima data utile\
\no un tasto qualsiasi per modificare la tua scelta.\n>')
                if dt_err == '':
                    reporting = BCpython.CMCSchedThread(sched_dt=datetime.datetime.now(), delta=delta,
                                                        currency=currency, path=directory)
                    reporting.start()
                    input('\n* * *\n* Il programma di reportistica è stato pianificato, d\'ora in \
avanti\n* proseguirà in background, permettendoti di effettuare ulteriori\n* analisi sui \
dati scaricati o, se prefirisci, aggiornandoli.\n* * *\n\nPremi invio per proseguire al programma di analisi.\n>')
                    break
                else:
                    date_fs = BCpython.chkdate()
                    time_fs = BCpython.chktime()
                    dt_fs = datetime.datetime.strptime(str(date_fs + ' ' + time_fs), '%d/%m/%Y %H:%M')
                    if dt_fs > datetime.datetime.now():
                        reporting = BCpython.CMCSchedThread(sched_dt=dt_fs, delta=delta,
                                                            currency=currency, path=directory)
                        reporting.start()
                        input('\n* * *\n* Il programma di reportistica è stato pianificato, d\'ora in \
avanti\n* proseguirà in background, permettendoti di effettuare ulteriori analisi\n* sui \
dati scaricati o, se prefirisci, aggiornandoli.\n* * *\n\nPremi un tasto qualsiasi per proseguire al programma di analisi.\n>')
                        break
                    else:
                        continue
            break

# Analysis script
print('''
 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
|    Questa parte del programma permette la visualizzazione di dati filtrati   |
| sulle prime 200 criptovalute per capitalizzazione presenti su CoinMarketCap. |
|    Potrai visualizzare dati sui prezzi delle monete, i volumi movimentati    |
|   durante le 24 ore precedenti, la loro capitalizzazione (nonchè dominanza   |
|  sul mercato) e le performance durante la precedente o le precedenti 24 ore, |
|   oltre che sugli ultimi 7, 30, 60 o 90 giorni. Potrai filtrare i dati con   |
|      valori al di sopra o al di sotto di determinate soglie e ordinarli      |
|                       in senso crescente o decrescente.                      |
 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ''')

choices = '''
 - - -
|Scegli su quali valori vuoi ricavare informazioni:\n|
| - PREZZI, digita                                     > p
| - VOLUME scambiato nelle ultime 24 ore, digita       > v
| - CAPITALIZZAZIONE di mercato, digita                > c
| - DOMINANZA sul mercato, digita                      > d
| - VARIAZIONE % durante l'ultima ora, digita          > 1
| - VARIAZIONE % durante le ultime 24 ore, digita      > 24
| - VARIAZIONE % durante gli ultimi 7 giorni, digita   > 7
| - VARIAZIONE % durante gli ultimi 30 giorni, digita  > 30
| - VARIAZIONE % durante gli ultimi 60 giorni, digita  > 60
| - VARIAZIONE % durante gli ultimi 90 giorni, digita  > 90\n|
| - per informazioni sullo stato dei report, digita    > i\n|
| - per uscire dal programma, digita                   > exit
 - - -\n>'''
valid_choices = ['p', 'v', 'c', 'd', '1', '24', '7', '30', '60', '90', 'i', 'exit']
choices_d = {'p': 'price', 'v': 'volume_24h', 'c': 'market_cap', 'd': 'market_cap_dominance', '1': 'percent_change_1h',
             '7': 'percent_change_7d', '30': 'percent_change_30d', '60': 'percent_change_60d',
             '24': 'percent_change_24h', '90': 'percent_change_90d'}
choices_out = {'p': 'PREZZO', 'v': 'VOLUME', 'c': 'MARKET CAP', 'd': 'DOMINANZA', '1': 'VAR % 1 ORA ',
               '7': 'VAR % 7 GG', '30': 'VAR % 30 GG', '60': 'VAR % 60 GG',
               '24': 'VAR % 24 ORE', '90': 'VAR % 90 GG'}
fiat_sym = {'USD': '$', 'EUR': '€', 'GBP': '£', 'BTC': '₿', 'ETH': 'ETH', 'CNY': '¥', 'JPY': '¥',
            'CUP': 'MN', 'BRL': 'R$', 'RUB': '₽'}
info = ''

while True:
    if info == 'exit':
        print('\nLa pianificazione dei report continuerà fino a che la finestra resterà aperta.\
\n\n- - - - - -\n\nUscita dal programma di analisi in corso. . . . . . . .')
        break
    
    info = str(input(choices))

    # invalid user choice
    while info not in valid_choices:         
        info = input('\nHai effettuato una scelta non valida. Riprova o digita \'exit\'\nper uscire dal programma.\n>')

    # show info on reporting activity
    if info == 'i':
        if reporting.n == 0 and reporting.n_err == 0:       # no report yet
            print(f'\n* * *\n\
* I report sono pianificati ogni {BCpython.strdelta(delta)}.\n\
* La prima copia verrà prodotta alle {reporting.sched_dt.strftime("%H:%M")} del \
{reporting.sched_dt.strftime("%d/%m/%Y")} e salvata\n* in "{reporting.path}".\n* * *\n')
            info = input('- - - - - -\nPremi un tasto qualsiasi se vuoi tornare al menù principale per effettuare\naltre analisi, \
digita \'exit\' per uscire dal programma di analisi.\n>')
        elif reporting.n == 0 and reporting.n_err != 0:     # tryed but just errors
            print(f'\n* * *\n\
* I report sono pianificati ogni {BCpython.strdelta(delta)}.\n\
* Primo tentativo effettuato con esito negativo alle {reporting.first_dt.strftime("%H:%M")} del \
{reporting.first_dt.strftime("%d/%m/%Y")}.\n\
* Il prossimo tentativo verrà effettuato alle {reporting.sched_dt.strftime("%H:%M")} del \
{reporting.sched_dt.strftime("%d/%m/%Y")}.\n\
* Sono stati effettuati {reporting.n_err} tentativi, tutti falliti.\n\
* I report vengono salvati in "{reporting.path}".\n* * *\n')
            info = input('- - - - - -\nPremi un tasto qualsiasi se vuoi tornare al menù principale per effettuare\naltre analisi, \
digita \'exit\' per uscire dal programma di analisi.\n>')
            
        else:                                               # reports already produced
            print(f'\n* * *\n\
* I report sono pianificati ogni {BCpython.strdelta(delta)}.\n\
* La prima copia è stata prodotta alle {reporting.first_dt.strftime("%H:%M")} del \
{reporting.first_dt.strftime("%d/%m/%Y")}.\n\
* La prossima copia verrà prodotta alle {reporting.sched_dt.strftime("%H:%M")} del \
{reporting.sched_dt.strftime("%d/%m/%Y")}.\n\
* Sono stati prodotti {reporting.n} report, con {reporting.n_err} errori di connessione.\n\
* I report vengono salvati in "{reporting.path}".\n* * *\n')
            info = input('- - - - - -\nPremi un tasto qualsiasi se vuoi tornare al menù principale per effettuare\naltre analisi, \
digita \'exit\' per uscire dal programma di analisi.\n>')

    # show some kind of data
    elif info in valid_choices[:-2]:
        if info in ('p', 'v', 'c'):                                 # symbol for currency output
            sym = fiat_sym[currency]
        elif info in ('d', '1', '24', '7', '30', '60', '90'):       # symbol for percentage output
            sym = '%'
        _filter = input('\nSe vuoi applicare un filtro ai dati digita \'s\', premi un altro tasto\n\
per visualizzare tutti i dati scelti.\n>')
        if _filter != 's':                      # DON'T apply filters on data
            update_data = input('Se vuoi aggiornare i dati da CMC prima di inizare le analisi digita \'s\',\
\npremi invio se vuoi analizzare i dati salvati nell\'ultimo report.\n>')
        elif _filter == 's':                    # apply filters on data
            m_l = input('Se vuoi selezionare i valori superiori a una data soglia digita \'>\',\
\naltrimenti digita \'<\'.\n>')
            while m_l not in ('>', '<'):
                m_l = input('Selezione errata. Digita \'>\' per visulizzare i valori superiori a una\
soglia, \'<\' altrimenti.\n>')
            threshold = str(input('Seleziona la soglia desiderata, inserendo un valore numerico.\n>')).replace(',', '.')
            # alternative
            # if isinstance(float(threshold), float): threshold = float(threshold)          
            # else: threshold = str(input('Inserisci un valore numerico.\n>')).replace(',', '.')
            while True:
                try:
                    threshold = float(threshold)
                    break
                except ValueError:
                    threshold = str(input('Inserisci un valore numerico.\n>')).replace(',', '.')
                    continue
            asc_desc = input('Digita \'c\' per ordinare i dati in ordine crescente, \'d\' per ordinarli\
in ordine decrescente.\n>')
            while asc_desc not in ('c', 'd'):
                asc_desc = input('Selezione errata. Digita \'c\' per la visualizzazione in ordine\
\ncrescente, \'d\' altrimenti.\n>')
            if asc_desc == 'c':
                asc_desc = False
                ad_out = 'crescente'
            else:
                asc_desc = True
                ad_out = 'decrescente'
            update_data = input('Se vuoi aggiornare i dati da CMC prima di inizare le analisi digita \'s\',\
\npremi invio se vuoi analizzare i dati salvati nell\'ultimo report.\n>')
     
        # create dictonary with selected data
        while True:
            # check offline db
            while reporting.n == 0 and update_data != 's':
                update_data = input(f'\nLa pianificazione non ha ancora creato alcun db.\n\n\
Attendere le {reporting.sched_dt.strftime("%H:%M")} del {reporting.sched_dt.strftime("%d/%m/%Y")} per lavorare su un db offline.\n\
Premi \'s\' per lavorare sui dati online, un tasto qualsiasi per riprovare.\n>')
                if update_data == 's':
                    break
                else:
                    continue            
            try:
                if _filter != 's':                  # unfiltered selection
                    if update_data != 's':          # unfiltered offline data
                        data = BCpython.crypto_data(cmc_data=reporting.last_CMC_data, currency=currency)
                    elif update_data == 's':        # unfiltered online data
                        print('\nRichiesta dati in corso . . . . .\n')
                        data = BCpython.crypto_data(cmc_data=BCpython.update_cmc(currency, key), currency=currency)
                    print(f'\n* * *\nHai richiesto dati su: {str(choices_out[info]).lower()}. Criptovalute sono ordinate per capitalizzazione.\n')
                else:                               # filtered selection
                    if update_data != 's':          # filtered offline data
                        if m_l == '>':              # filtered offline data > of
                            data = BCpython.filtered_major_data(cmc_data=reporting.last_CMC_data, currency=currency,
                                                                thr_data=choices_d[info], threshold=threshold,
                                                                asc_desc=asc_desc)
                        else:                       # filtered offline data < of
                            data = BCpython.filtered_minor_data(cmc_data=reporting.last_CMC_data, currency=currency,
                                                                thr_data=choices_d[info], threshold=threshold,
                                                                asc_desc=asc_desc)
                    else:                           # filtered online data
                        print('\nRichiesta dati in corso . . . . .\n')
                        if m_l == '>':              # filtered online data > of
                            data = BCpython.filtered_major_data(cmc_data=BCpython.update_cmc(currency, key), currency=currency,
                                                                thr_data=choices_d[info], threshold=threshold,
                                                                asc_desc=asc_desc)
                        else:                       # filtered online data < of
                            data = BCpython.filtered_minor_data(cmc_data=BCpython.update_cmc(currency, key), currency=currency,
                                                                thr_data=choices_d[info], threshold=threshold,
                                                                asc_desc=asc_desc)                    
                    print(f'\n* * *\nHai richiesto dati su: {str(choices_out[info]).lower()} {m_l} {threshold}{sym}, in ordine \
{ad_out}.\n{len(data.keys())} criptovalute soddisfano i requisiti.\n')
                break
            except requests.exceptions.ConnectionError:
                update_data = input('Errore di connessione. Connettiti ad internet e premi \'s\' per riprovare a scaricare i dati online, un tasto qualunque per utilizzare i dati offline.\n>')
                continue

        # print analysis result
        try:
            sp = ''
            for i in range((max(len(x) for x in data.keys()) + 5) - len('-CRIPTOVALUTA-')):     # spaces between headers
                sp += ' '
            print(f'-CRIPTOVALUTA-{sp}-{choices_out[info]}-\n')
            for crypto in data.keys():
                sp = ''
                for i in range((max(len(x) for x in data.keys()) + 3) - len(crypto)):           # spaces between values
                    sp += ' '
                print(crypto, sp, round(data[crypto][choices_d[info]], 4), sym)                 # values lines
        except ValueError:
            pass
        
        info = input('* * *\n\nPremi un tasto qualsiasi se vuoi tornare al menù principale per effettuare\
\naltre analisi, digita \'exit\' per uscire dal programma di analisi.\n>')

    elif info == 'exit':
        print('\nLa pianificazione dei report continuerà fino a che la finestra resterà aperta.\
\n\n- - - - - -\n\nUscita dal programma di analisi in corso. . . . . . . .')
        break
