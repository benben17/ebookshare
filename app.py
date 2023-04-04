from book import app




if __name__ == '__main__':
    print(app.url_map)
    app.run(debug=True,threaded=True)
