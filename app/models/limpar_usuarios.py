from user import apagar_usuarios_nao_confirmados

if __name__ == "__main__":
    apagar_usuarios_nao_confirmados(expiracao_horas=24)
    print("Usuários não confirmados apagados (24h).")
