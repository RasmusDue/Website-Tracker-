import matplotlib.pyplot as plt
import io
from flask import send_file



# @app.route('/fig/')
def fig():
    plt.title("figure_key")
    # x_list = []
    # y_list = []
    # for i in data.graf_list:
    #     x_list.append(i['timestamp'])
    #     y_list.append(i['value'])
    # print("_____")
    # print(x_list)
    # print(y_list)
    plt.plot([5,10,15,20], [1,2,3,4])
    img = io.BytesIO()
    plt.savefig(img)
    img.seek(0)
    print("_____opretter fig______")
    return send_file(img, mimetype='image/png')
