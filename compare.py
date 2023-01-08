import sys
import ast


def levenshtein_distance(code1, code2):
    text1 = code1
    text2 = code2
    n = len(text1) + 1
    m = len(text2) + 1
    dp = [0] * n
    for i in range(len(dp)):
        dp[i] = [0] * (m)
    for i in range(m):
        dp[0][i] = i
    for i in range(n):
        dp[i][0] = i
    for i in range(1, n):
        for j in range(1, m):
            if text1[i - 1] == text2[j - 1]:
                q = 0
            else:
                q = 1
            dp[i][j] = min(dp[i][j - 1] + 1, dp[i - 1][j] + 1, dp[i - 1][j - 1] + q)
    return dp[n - 1][m - 1]


def read_file(file_path):
    with open(file_path, "r", encoding='utf-8') as file:
        code = ""
        for string in file:
            code += string + '\n'
        return code


def cut_replace_variables(text1, text2):
    variable_names1 = {var.id for var in ast.walk(ast.parse(text1))
                       if isinstance(var, ast.Name) and not isinstance(var.ctx, ast.Load)}
    variable_names2 = {var.id for var in ast.walk(ast.parse(text2))
                       if isinstance(var, ast.Name) and not isinstance(var.ctx, ast.Load)}
    s = "a"
    for i in variable_names1.union(variable_names2):
        text1 = text1.replace(f"{i} ", f"{s} ")
        text2 = text2.replace(f"{i} ", f"{s} ")
        s = s[:-1] + chr(ord(s[-1]) + 1)
        if s[len(s) - 1] == chr(ord('z') + 1):
            s = s[:-1] + "a"
            s += "a"
    return text1, text2


def delete_docstrings(tree, text):
    text = text.replace(" ", "")
    text = text.replace("\n", "")
    text = text.expandtabs(0)
    for i in ast.walk(tree):
        try:
            docstring = ast.get_docstring(i, clean=True)
            if docstring is not None:
                docstring = str(docstring)
                docstring = docstring.expandtabs(0)
                docstring = docstring.replace(" ", "")
                docstring = docstring.replace('\n', "")
                text = text.replace(f"\"\"\"{docstring}\"\"\"", "")
                text = text.replace(f"\'\'\'{docstring}\'\'\'", "")
        except:
            continue
    return text


with open(sys.argv[1], "r") as input_file, open(sys.argv[2], "w") as output_file:
    for paths in input_file.readlines():
        paths = paths.split()
        file1 = paths[0]
        file2 = paths[1]
        text1 = read_file(file1)
        text2 = read_file(file2)
        tree1 = ast.parse(text1)
        tree2 = ast.parse(text2)
        text1, text2 = cut_replace_variables(text1, text2)
        text1 = delete_docstrings(tree1, text1)
        text2 = delete_docstrings(tree2, text2)
        similarity = levenshtein_distance(text1, text2)
        output_file.write(str(1 - similarity / max(len(text1), len(text2))) + '\n')
