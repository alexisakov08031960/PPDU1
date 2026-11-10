# распаковка для самопроверки
with pyzipper.AESZipFile('crypto_rates_src.zip') as zf:
    zf.setpassword(password_bytes)
    print(zf.namelist())
    zf.extractall('verify')