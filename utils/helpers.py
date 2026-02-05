def load_profile():
    with open("config/profile.txt", "r", encoding="utf-8") as f:
        return f.read()
def ask_for_feedback():
    print("\n🗣️ FEEDBACK")
    print("O que você achou do conteúdo apresentado?")
    print("Responda com algo como:")
    print("- gostei / não gostei")
    print("- muito longo / muito curto")
    print("- técnico demais / superficial")
    print("- comentário livre\n")

    feedback = input("👉 Seu feedback: ").strip()
    return feedback
