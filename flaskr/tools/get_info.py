import requests

def info(url):
    try:
        r = requests.get(url)
        return r.headers
    except Exception as e:
        return e

if __name__ == "__main__":
    print(info("http://192.168.1.254"))
