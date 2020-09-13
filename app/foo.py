
def coin_change(S, N):
    c = 0
    amount = N
    i = 0
    while (amount > 0):
        if S[i] <= amount:
            amount -= S[i]
            c += 1
        else:
            i += 1
    return amount, c