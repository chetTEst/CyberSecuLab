from pyseto import Key
from icecream import ic

ic.enable()

# Загружаем raw-PEM
with open("C:\\Users\\1\\PycharmProjects\\CyberSecuLab\\universal_app\\flask_app\\private.pem", "rb") as f:
    raw_priv = f.read()
    sk = ic(Key.new(version=4, purpose="public", key=raw_priv).to_paserk()) # импорт raw PEM
    ic(sk)

# Загружаем raw-PEM
with open("C:\\Users\\1\\PycharmProjects\\CyberSecuLab\\universal_app\\flask_app\\public.pem", "rb") as f:
    raw_priv = f.read()
    pk = ic(Key.new(version=4, purpose="public", key=raw_priv).to_paserk()) # импорт raw PEM
    ic(pk)