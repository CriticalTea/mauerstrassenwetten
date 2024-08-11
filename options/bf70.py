from datetime import date, datetime
data = {}
print(datetime.now().strftime('%Y-%m-%d'))
with open('RUT.csv', mode='r') as f:
    lines = f.readlines()
    for line in lines[1:]:
        parts = line.split(',')
        line_date = datetime.strptime(parts[0].strip(), '%Y-%m-%d').date()
        print(line_date, (float(parts[2])+ float(parts[3]))/2)
        data[line_date] = (float(parts[2])+ float(parts[3]))/2

