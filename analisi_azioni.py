from yahoo_fin.stock_info import get_data, tickers_sp500, tickers_nasdaq, tickers_other, get_quote_table, get_live_price

import azioni

last_best = dict()
last_detected = dict()


def get_info(azione_id, bought=False):
    """ pull historical data for Netflix (NFLX) """
    # nflx = get_data("MB.MI")

    """ pull data for Apple (AAPL) """
    """case sensitivity does not matter"""
    # aapl = get_data("aapl")

    """ get list of all stocks currently traded
        on NASDAQ exchange """
    # nasdaq_ticker_list = tickers_nasdaq()

    """ get list of all stocks currently in the S&P 500 """
    # sp500_ticker_list = tickers_sp500()

    """ get other tickers not in NASDAQ (based off nasdaq.com)"""
    # other_tickers = tickers_other()

    """ get information on stock from quote page """

    global last_best
    to_send = False
    pretty_result = "<b>Titolo " + azioni.azioni_id[azione_id] + "</b>\n\n"
    try:
        agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15'
        headers = {'User-Agent': agent}
        info = get_quote_table(azione_id, headers=headers)
        for key in info:
            value_str = str(info[key])
            if value_str != "nan" and "N/A" not in value_str:
                if key == "Quote Price":
                    value = float(info[key])
                    round_value = round(value, 3)
                    value_str = "<b><u>" + str(round_value) + "</u></b>"

                    if azione_id not in last_best:
                        to_send = True
                        # last_best[azione_id] = value
                        azioni.add_azioni_best(azione_id, value)
                    else:
                        round_lb = round(last_best[azione_id], 3)
                        if (not bought and round_lb > round_value) or (bought and round_lb < round_value):
                            condition1 = azione_id not in last_detected
                            condition2 = azione_id in azioni.azioni_soglia
                            condition3 = not condition2 and round_value != round(last_detected[azione_id], 3)
                            condition4 = condition2 and not bought and azioni.azioni_soglia[azione_id] >= round_value
                            condition5 = condition2 and bought and azioni.azioni_soglia[azione_id] <= round_value
                            if condition1 or condition3 or condition4 or condition5:
                                to_send = True
                            # last_best[azione_id] = value
                            azioni.add_azioni_best(azione_id, value)
                    # pretty_result = "<b>NUOVO MIGLIORE</b>\n\n" + pretty_result
                    # last_detected[azione_id] = value
                    azioni.add_azioni_detected(azione_id, value)
                pretty_result += "<i><b>" + key + "</b></i>:  " + value_str + "\n"
    except Exception as ex:
        pretty_result += "Titolo non trovato"
        pretty_result += "\n\n" + str(ex)

    # print(info)
    # print(get_live_price("MB.MI"))
    return pretty_result, to_send


def get_last_bests():
    info = "<i>Valori migliori dall'ultima accensione:</i>\n"
    for key in last_best:
        info += "<b>" + key + ":</b> " + str(last_best[key]) + "\n"
    return info


def get_last_detected(azione_id):
    return last_detected[azione_id]
