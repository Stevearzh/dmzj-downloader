# dmzj-downloader
downloader for https://manhua.dmzj.com/, based on [requests](http://docs.python-requests.org/en/master/) and [pyppeteer](https://miyakogi.github.io/pyppeteer/)

## how to use

First, clone the project and install the dependencies:

```bash
git clone https://github.com/Stevearzh/dmzj-downloader

cd dmzj-downloader

python3 -m venv ./venv

source ./venv/bin/activate

pip install -r requirements.txt
```

Then, edit `downloader.py`, copy the comic's url you want to download to `comic_url`

Finally, run script:
```bash
python downloader.py
```

Enjoy!
