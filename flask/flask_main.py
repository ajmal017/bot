from flask import Flask, request, render_template


accountsList = []


app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/add/', methods=['post', 'get'])
def login():
    message = ''
    value = []

    with open('accs.txt', 'r') as root:
        value = root.readline().split(',')
    
    if request.method == 'POST':
        data = request.get_data()
        data = str(data)[2:]
        data = data[:-1]
        data = data.split("&")

        data_d = dict()
        for line in data:
            arr = line.split('=')
            data_d[arr[0]] = arr[1]
        print(data_d)

        with open('record.txt', 'w') as root:
            root.write(data_d['accounts'])
            root.write('\n' + data_d['value'])
            root.write('\n' + data_d['risk'])
            root.write('\n' + data_d['data'])
            root.write('\n' + data_d['suc_fee'])

    return render_template('login.html', message='All OK', accs=value)

app.run()
