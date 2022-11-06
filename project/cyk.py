from pyformlang.cfg import CFG

__all__ = [
    "cyk",
]


def cyk(word: str, cfg: CFG) -> bool:
    """
    Cocke-Younger-Kasami algorithm implementation.
    Check whether CFG accepts given word

    Parameters
    ----------
    word : str
        Word to be checked
    cfg : CFG
        Grammar

    Returns
    -------
    result: bool
        Does a word belong to a given grammar
    """

    if not word:
        return cfg.generate_epsilon()

    n = len(word)
    cnf = cfg.to_normal_form()
    dp = [[set() for _ in range(n)] for _ in range(n)]

    prods_terminal = [p for p in cnf.productions if len(p.body) == 1]
    prods_non_terminals = [p for p in cnf.productions if len(p.body) == 2]

    for i, term in enumerate(word):
        dp[i][i].update(
            production.head.value
            for production in prods_terminal
            if word[i] == production.body[0].value
        )

    for step in range(1, n):
        for i in range(n - step):
            j = i + step
            for k in range(i, j):
                dp[i][j].update(
                    p.head
                    for p in prods_non_terminals
                    if p.body[0] in dp[i][k] and p.body[1] in dp[k + 1][j]
                )

    return cfg.start_symbol in dp[0][n - 1]
