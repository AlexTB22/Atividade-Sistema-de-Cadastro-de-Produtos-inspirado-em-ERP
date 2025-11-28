import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime
from tabulate import tabulate
conn = sqlite3.connect("a2.db")
cursor = conn.cursor()
nome = "NULL"
cursor.execute(f"""
CREATE TABLE IF NOT EXISTS produto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    produto_nome TEXT NOT NULL,
    categoria TEXT NOT NULL,
    preco REAL NOT NULL,
    quantidade REAL NOT NULL,
    custo REAl NOT NULL,
    FOREIGN KEY (produto_id) REFERENCES produto(id)
);
""")

cursor.execute(f"""
CREATE TABLE IF NOT EXIST movimentacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    tipo TEXT NOT NULL,
    quantidade INTEGER,
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (produto_id) REFERENCES produto(id)
);
""")

prod_selecionado="NULL"

def mostrar_produtos():
    cursor.execute("SELECT * FROM produto")
    dados = cursor.fetchall()
    cursor.execute("PRAGMA table_info(produto)")
    colunas = [c[1] for c in cursor.fetchall()]
    linhas_formatadas = []

    for linha in dados:
        quantidade = linha[5] 

        if quantidade < 5:
            cor_inicio = "\033[91m"
            cor_fim = "\033[0m"
            linha_colorida = [f"{cor_inicio}{valor}{cor_fim}" for valor in linha]
            linhas_formatadas.append(linha_colorida)
        else:
            linhas_formatadas.append(linha)

    print(tabulate(linhas_formatadas, headers=colunas, tablefmt="grid"))


def cadastrar_prod():
    while True:
        nomep=input("digite o nome do produto(digite 'sair' ou '0' para desistir)")
        cursor.execute("SELECT 1 FROM produto WHERE produto_nome = ? LIMIT 1", (nomep,))
        existe = cursor.fetchone()

        if existe:
            print("Produto já existente!")
        
        if nomep== "sair" or "0":
            return
        else:
            break
        
    categoria=input("digite a categoria do produto")
    
    while True:
            try:
                cost=input("digite o custo do produto")
                if cost > 0:
                    break
                else:
                    print("digite um custo maior que 0")
            except ValueError:
                print("digite um número válido")
    
    
    while True:
            try:
                b=input("digite o valor do produto")
                if b > 0:
                    break
                else:
                    print("digite um valor maior que 0")
            except ValueError:
                print("digite um número válido")
    
    while True:
        c=(float(input("quantidade do produto")))
        if c <= 0:
            print("digite uma quantidade válida")
        elif c == "":
            print("digite uma quantidade válida")
        elif c > 0:
            break
        else:
            print("digite uma quantidade válida")
            
    while True:
        codep=input("digite o código do produto")
        cursor.execute("SELECT 1 FROM produto WHERE produto_id = ? LIMIT 1", (codep,))
        existe = cursor.fetchone()

        if existe:
            print("Produto já existente!")
        else:
            break
            
    cursor.execute(f"""
        INSERT INTO produto (produto_id, produto, categoria, custo, preco, quantidade)
        VALUES (?, ?, ?, ?, ?);
        """, (codep, nomep, categoria, cost, b, c))
    conn.commit()    
    
    cursor.execute("SELECT id, nome FROM produtos WHERE nome = ?", (nomep,))
    produto = cursor.fetchone()
    cursor.execute(f"""
        INSERT INTO movimentacoes (produto_id, tipo, quantidade)
        VALUES (?, ?, ?,);
        """, (produto[0], "entrada", c))
    conn.commit()        

def selecionar_produto():
    mostrar_produtos()
    cursor.execute("SELECT produto_nome FROM produto")
    tabelas = cursor.fetchall()
    for tabela in tabelas:
        print(tabela)
    try:
        choice=input("selecione o produto")
        cursor.execute("SELECT id FROM produto WHERE nome = ?", (choice,))
        prod_selecionado = cursor.fetchone()
        return prod_selecionado
    
    except ValueError:
        print("produto não encontrado")
        
        

def atualizar():
    selecionar_produto()
    
    while True:
        atualizando=input("digite 1 para atualizar o valor - 2 para registrar movimentação - 3 para atualizar o custo = 4 para realizar pedido - 0 para sair")
        if atualizando == "2":
            while True:
                try: 
                    c=(float(input("movimentação do produto")))
                    break
                except ValueError:
                    print("digite uma quantidade válida")
            if c > 0:
                ent="entrada"
            else:
                ent="saida"
            
            cursor.execute("""
            UPDATE produto
            SET preco = ?
            WHERE id = ?;
            """, ((prod_selecionado[5] + c), prod_selecionado[0]))
            conn.commit()
            cursor.execute(f"""
                INSERT INTO movimentacoes (produto_id, tipo, quantidade)
                VALUES (?, ?, ?,);
                """, (prod_selecionado[0], ent, c))
            conn.commit()        
        elif atualizando == "1":
            while True:
                try:
                    b=input("novo valor do produto")
                    if b > 0:
                        break
                    else:
                        print("digite um valor maior que 0")
                except ValueError:
                    print("digite um número válido")
            cursor.execute("""
            UPDATE produto
            SET preco = ?
            WHERE id = ?;
            """, (b, prod_selecionado[0]))
            conn.commit()
            
        elif atualizando == "3":
            while True:
                try:
                    b=input("novo custo do produto")
                    if b > 0:
                        break
                    else:
                        print("digite um valor maior que 0")
                except ValueError:
                    print("digite um número válido")
            cursor.execute("""
            UPDATE produto
            SET custo = ?
            WHERE id = ?;
            """, (b, prod_selecionado[0]))
            conn.commit()
            
        elif atualizando == "4":
            prods=input("quantos produtos deseja que sejam entregues?")
            cursor.execute(f"""
                INSERT INTO movimentacoes (produto_id, tipo, quantidade)
                VALUES (?, ?, ?,);
                """, (prod_selecionado[0], "pedido", prods))
            conn.commit()     
            
        elif atualizando == "0":
            return

        else:
            print("inválido")
            
def indicadores():
    while True:
        opcaum = input("digite 1 para ver o giro de estoque dos últimos 6 meses - 2 para nível de serviço - 3 tempo de reposição - 4 custo de manutenção - 0 para sair")
        if opcaum == "1":
            selecionar_produto
            cursor.execute("SELECT * FROM movimentacoes WHERE produto_id AND data_hora >= DATE('now', '-6 months') = ? ", (prod_selecionado[0]))
            movis=cursor.fetchall()
            quantidade = len(movis)
            print(f"a frequência de giro é de {quantidade} nos útimos 6 meses")

        if opcaum == "0":
            break
            
def apagar():
    selecionar_produto()
    cursor.execute("DELETE FROM items WHERE id = ?;", (prod_selecionado[0],))
    conn.commit()
    print("produto deletado com sucesso")
    


def menu():
    while True:
        opcaoo = input("Digite o respectivo número da opção para executa-la - 1. Cadastrar produto - 2. Excluir produto - 3. atualizar - 4. Mostrar produtos - 5. indicadores de desempenho - - 0. Sair do programa").strip
        if opcaoo == "1":
            cadastrar_prod()
        elif opcaoo == "2":
            apagar()
        elif opcaoo == "3":
            atualizar()
        elif opcaoo == "4":
            mostrar_produtos()
        elif opcaoo == "5":
            indicadores()
        elif opcaoo == "0":
            return
        else:
            print("valor inválido")
if __name__ == "__main__":
    menu()