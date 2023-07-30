# import pandas
# import sqlite3

# DBFILE = "trading_data.db"

# day = day_of_signal

# params = {
#     'start_time': f'{day} 09:30:00',
#     'end_time': f'{day} 16:00:00'
# }

# query = """
#     SELECT Close, Volume, Timestamp
#     FROM trading_data
#     WHERE timestamp >= %(start_time)s
#     AND timestamp <= %(end_time)s;
#     """



m1 = [
    [1,2,3],
    [4,4,4],
    [5,5,5]
]

m2 = [
    [1,2,3],
    [4,4,4],
    [5,5,5]
]

rma = [
    [0,0,0],
    [0,0,0],
    [0,0,0]
]

rmm = [
    [0,0,0],
    [0,0,0],
    [0,0,0]
]

for i in range(len(m1)):
    for j in range(len(m1[0])):
        rma[i][j] = m1[i][j] + m2[i][j]


for i in range(len(m1)):
    for j in range(len(m2[i])):
        rmm[i][j] = m1
print(rm)
