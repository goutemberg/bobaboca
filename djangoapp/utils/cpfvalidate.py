def validar_cpf(cpf: str) -> bool:
    """
    Valida um CPF.
    :param cpf: CPF no formato "123.456.789-09" ou "12345678909"
    :return: True se for válido, False caso contrário.
    """
    # Remover caracteres não numéricos
    cpf = ''.join(filter(str.isdigit, cpf))

    # Verificar se o CPF tem 11 dígitos
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    # Cálculo do primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    primeiro_digito = (soma * 10 % 11) % 10

    # Cálculo do segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    segundo_digito = (soma * 10 % 11) % 10

    # Verificar os dígitos
    return cpf[-2:] == f"{primeiro_digito}{segundo_digito}"


# Exemplo de uso
cpf_teste = "123.456.789-09"
if validar_cpf(cpf_teste):
    print(f"O CPF {cpf_teste} é válido.")
else:
    print(f"O CPF {cpf_teste} é inválido.")
