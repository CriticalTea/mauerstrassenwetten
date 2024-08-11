from datetime import date, timedelta

def read_csv(path,delimiter=','):
    with open(path, 'r') as f:
        lines = f.readlines()
    keys = [key.strip() for key in lines[0].split(delimiter)]
    content = {}
    for line in lines[1:]:
        parts = line.split(delimiter)
        values = {}
        if parts[1] == 'null':
            continue
        for i in range(1,len(keys)):
            try:
                values[keys[i]] = float(parts[i])
            except Exception:
                print("Unable to parse %s" % parts[i])
                raise Exception("asdf")

        date_key = date(int(parts[0][0:4]), int(parts[0][5:7]), int(parts[0][8:10]))
        content[date_key] = values
    return content
    

def tmp():
    for days in range(0, (end_date-start_date).days+1):
        current_date = start_date+timedelta(days=days)
        if current_date in vta_price.keys():
            current_price = vta_price[current_date]['Close']
        if current_date in vta_dividends.keys():
            dividend = vta_dividends[current_date]['Dividends']
            share += dividend/current_price
        shares.append(share)
        performance.append(share*current_price)
        price.append(current_price)
        dates.append(current_date)