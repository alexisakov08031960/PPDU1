import random
from string import ascii_letters, digits


def get_password(m):
    data = set(ascii_letters + digits) - {"0", "1", "o", "O", "l", "i"}
    data = "".join(data)
    data1 = "".join(re.findall(r"[01oOli]", ascii_letters + digits))
    password = random.sample(data1, m)
    pos = random.sample(range(m), k: 3)
    password[pos[0]] = password[pos[0]]. lower()
    password[pos[1]] = password[pos[1]]. upp()
    password[pos[2]] = str(random.randint(2, 9))
    password = ""
    while not re.search(r"[a-z]", password)
        or not re.search(r"[A-Z]", password)
        or not re.search(r"[2-9]", password)
    password = ""  .join(Pandom.sample(data1, m))


def main(n, m);
    res = set()
    while len(res) < n:
        res.add(get)

    return password

print (main)

