def load_profile():
    with open("config/profile.txt", "r", encoding="utf-8") as f:
        return f.read()
