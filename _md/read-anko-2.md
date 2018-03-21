# anko源代码阅读之lex/goyacc（一）

- time 2018-03-21

> 这篇文章是在阅读[GitHub - mattn/anko: Scriptable interpreter written in golang](https://github.com/mattn/anko)时候的笔记

## yacc的语法

### 语法文件
* 结构，由`%%`分割的三部分组成
```
声明
%%
规则
%%
程序
```
* yacc 命令忽略语法文件中的空格、制表符和换行符
* 注释：`/* This is a comment on a line by itself. */`
* 使用''（单引号）表示字符串
* 对标记名称使用大写字母，对非终止符号名称使用小写字母。
* 将语法规则和操作放在单独的行上，允许在更改一个时无需更改另一个。
* 将所有的规则一起放在相同的左侧。进入左侧一次，并将竖线作为该左侧其余规则的起始位置。
* 对于相同左侧的每一个规则集，请在该左侧的最后一条规则后输入一个分号，并独立成行。您可在以后方便地添加新的规则。
* 使用两个制表符停止位缩进规则主体，使用三个制表符停止位缩进操作体。

### yacc规则
* 语法文件的规则部分包含一条或者多条语法规则。
* 语法规则具有下述格式：`A : BODY;`
* 其中 A 为非终止名称，BODY 为 0 个或者多个名称、文字和语义操作的序列，语义操作后面可有优先顺序规则（可选）。只有名称和文字是构成语法所必需的。语义操作和优先顺序规则为可选的。冒号和分号是必需的 yacc 标点。
* 优先顺序规则由 %prec 关键字定义，并更改与特定的语法规则关联的优先顺序级别。保留符号 %prec 可紧跟在语法规则的主体后面，且其后可有标记名称或者文字。构造使得语法规则的优先顺序成为标记名称或者文字的优先顺序。

## anko的yacc文件注释阅读

```diff
+ /* %{}%之间的代码会直接输出到go代码中 */
%{
package parser

import (
	"github.com/mattn/anko/ast"
)

%}
+ /* %type <x> y 规定y的类型是x*/
%type<compstmt> compstmt
%type<stmts> stmts
%type<stmt> stmt
%type<stmt_if> stmt_if
%type<stmt_default> stmt_default
%type<stmt_case> stmt_case
%type<stmt_cases> stmt_cases
%type<expr> expr
%type<exprs> exprs
%type<expr_many> expr_many
%type<expr_lets> expr_lets
%type<expr_pair> expr_pair
%type<expr_pairs> expr_pairs
%type<expr_idents> expr_idents
%type<expr_type> expr_type
%type<array_count> array_count

+ /* 会生成一个struct的type，字段是这些*/
%union{
	compstmt               []ast.Stmt
	stmt_if                ast.Stmt
	stmt_default           ast.Stmt
	stmt_case              ast.Stmt
	stmt_cases             []ast.Stmt
	stmts                  []ast.Stmt
	stmt                   ast.Stmt
	expr                   ast.Expr
	exprs                  []ast.Expr
	expr_many              []ast.Expr
	expr_lets              ast.Expr
	expr_pair              ast.Expr
	expr_pairs             []ast.Expr
	expr_idents            []string
	expr_type              string
	tok                    ast.Token
	term                   ast.Token
	terms                  ast.Token
	opt_terms              ast.Token
	array_count            ast.ArrayCount
}

+ /*
+ IDENT           结构体成员变量？
+ NUMBER          数字
+ STRING          字符串，"" 、 \'\' 、 ``之间的部分
+ ARRAY           数组
+ VARARG          ...
+ FUNC            func
+ RETURN          return
+ VAR             var
+ THROW           throw
+ IF              if
+ ELSE            else
+ FOR             for
+ IN              in
+ EQEQ            ==
+ NEQ             !=
+ GE              >=
+ LE              <=
+ OROR            ||
+ ANDAND          &&
+ NEW             new
+ TRUE            true
+ FALSE           false
+ NIL             nil
+ MODULE          module
+ TRY             try
+ CATCH           catch
+ FINALLY         finally
+ PLUSEQ          +=
+ MINUSEQ         -=
+ MULEQ           *=
+ DIVEQ           /=
+ ANDEQ           &=
+ OREQ            |=
+ BREAK           break
+ CONTINUE        continue
+ PLUSPLUS        ++
+ MINUSMINUS      --
+ POW             **
+ SHIFTLEFT       <<
+ SHIFTRIGHT      >>
+ SWITCH          switch
+ CASE            case
+ DEFAULT         default
+ GO              go
+ CHAN            chan
+ MAKE            make
+ OPCHAN          <-
+ TYPE            type
+ LEN             len
+ */
%token<tok> IDENT NUMBER STRING ARRAY VARARG FUNC RETURN VAR THROW IF ELSE FOR IN EQEQ NEQ GE LE OROR ANDAND NEW TRUE FALSE NIL MODULE TRY CATCH FINALLY PLUSEQ MINUSEQ MULEQ DIVEQ ANDEQ OREQ BREAK CONTINUE PLUSPLUS MINUSMINUS POW SHIFTLEFT SHIFTRIGHT SWITCH CASE DEFAULT GO CHAN MAKE OPCHAN TYPE LEN

+ /* 定义优先级 */
+ /* 同一行优先级一致 */
+ /* 越后面，优先级越高 */
+ /* left是左结合，rifht是右结合 */
%right '='
%right '?' ':'
%left OROR
%left ANDAND
%left IDENT
%nonassoc EQEQ NEQ ','
%left '>' GE '<' LE SHIFTLEFT SHIFTRIGHT

%left '+' '-' PLUSPLUS MINUSMINUS
%left '*' '/' '%'
%right UNARY

+ /* 第一个%%之前是定义 */
%%

+ /* 代码块 */
compstmt :
+   /* 空格，分号，换行 */
	opt_terms
	{
		$$ = nil
	}
	| stmts opt_terms
	{
		$$ = $1
	}

+ /*
+   l.stmts 就是解析后需要的东西 */
+   yylex 是 lex.go 里面实现了yyLexer接口的Lexer
+   为了改 stmts ,先做一个 type assert
+ */
stmts :
	{
		$$ = nil
		if l, ok := yylex.(*Lexer); ok {
			l.stmts = $$
		}
	}
	| opt_terms stmt
	{
		$$ = []ast.Stmt{$2}
		if l, ok := yylex.(*Lexer); ok {
			l.stmts = $$
		}
	}
	| stmts terms stmt
	{
		if $3 != nil {
			$$ = append($1, $3)
			if l, ok := yylex.(*Lexer); ok {
				l.stmts = $$
			}
		}
	}

+ /*
+   一个代码块，递归的
+   yylex 是 lex.go 里面实现了yyLexer接口的Lexer
+   为了改 stmts ,先做一个 type assert
+ */
stmt :
+   /* a = 1,2,3 */
	VAR expr_idents '=' expr_many
	{
		$$ = &ast.VarStmt{Names: $2, Exprs: $4}
		$$.SetPosition($1.Position())
	}
+   /* a = b */
	| expr '=' expr
	{
		$$ = &ast.LetsStmt{Lhss: []ast.Expr{$1}, Operator: "=", Rhss: []ast.Expr{$3}}
	}
+   /* a,b = a,b */
	| expr_many '=' expr_many
	{
		$$ = &ast.LetsStmt{Lhss: $1, Operator: "=", Rhss: $3}
	}
+   /* break */
	| BREAK
	{
		$$ = &ast.BreakStmt{}
		$$.SetPosition($1.Position())
	}
+   /* continue */
	| CONTINUE
	{
		$$ = &ast.ContinueStmt{}
		$$.SetPosition($1.Position())
	}
+   /* return */
	| RETURN exprs
	{
		$$ = &ast.ReturnStmt{Exprs: $2}
		$$.SetPosition($1.Position())
	}
+   /* throw 表达式*/
	| THROW expr
	{
		$$ = &ast.ThrowStmt{Expr: $2}
		$$.SetPosition($1.Position())
	}
+   /* module IDENT { 代码块 } */
	| MODULE IDENT '{' compstmt '}'
	{
		$$ = &ast.ModuleStmt{Name: $2.Lit, Stmts: $4}
		$$.SetPosition($1.Position())
	}
+   /* if */
+   /* stmt_if 代码块 */
	| stmt_if
	{
		$$ = $1
		$$.SetPosition($1.Position())
	}
+   /* for { 代码块 } */
	| FOR '{' compstmt '}'
	{
		$$ = &ast.LoopStmt{Stmts: $3}
		$$.SetPosition($1.Position())
	}
+   /* for ？ in 表达式 { 代码块 } */
	| FOR expr_idents IN expr '{' compstmt '}'
	{
		$$ = &ast.ForStmt{Vars: $2, Value: $4, Stmts: $6}
		$$.SetPosition($1.Position())
	}
+   /* for 赋值表达式;表达式;表达式 { 代码块 } */
	| FOR expr_lets ';' expr ';' expr '{' compstmt '}'
	{
		$$ = &ast.CForStmt{Expr1: $2, Expr2: $4, Expr3: $6, Stmts: $8}
		$$.SetPosition($1.Position())
	}
+   /* for 表达式 { 代码块 } */
	| FOR expr '{' compstmt '}'
	{
		$$ = &ast.LoopStmt{Expr: $2, Stmts: $4}
		$$.SetPosition($1.Position())
	}
+   /* try { 代码块 } catch IDENT { 代码块 } finally { 代码块 } */
	| TRY '{' compstmt '}' CATCH IDENT '{' compstmt '}' FINALLY '{' compstmt '}'
	{
		$$ = &ast.TryStmt{Try: $3, Var: $6.Lit, Catch: $8, Finally: $12}
		$$.SetPosition($1.Position())
	}
+   /* try { 代码块 } catch { 代码块 } finally { 代码块 } */
	| TRY '{' compstmt '}' CATCH '{' compstmt '}' FINALLY '{' compstmt '}'
	{
		$$ = &ast.TryStmt{Try: $3, Catch: $7, Finally: $11}
		$$.SetPosition($1.Position())
	}
+   /* try { 代码块 } catch IDENT { 代码块 } */
	| TRY '{' compstmt '}' CATCH IDENT '{' compstmt '}'
	{
		$$ = &ast.TryStmt{Try: $3, Var: $6.Lit, Catch: $8}
		$$.SetPosition($1.Position())
	}
+   /* try { 代码块 } catch { 代码块 } */
	| TRY '{' compstmt '}' CATCH '{' compstmt '}'
	{
		$$ = &ast.TryStmt{Try: $3, Catch: $7}
		$$.SetPosition($1.Position())
	}
+   /* switch expr { switch代码块 } */
	| SWITCH expr '{' stmt_cases '}'
	{
		$$ = &ast.SwitchStmt{Expr: $2, Cases: $4}
		$$.SetPosition($1.Position())
	}
+   /* 表达式 */
	| expr
	{
		$$ = &ast.ExprStmt{Expr: $1}
		$$.SetPosition($1.Position())
	}

+ /*
+   if代码块
+ */
stmt_if :
+   /* stmt_if 加 else if { 代码块 } */
	stmt_if ELSE IF expr '{' compstmt '}'
	{
		$1.(*ast.IfStmt).ElseIf = append($1.(*ast.IfStmt).ElseIf, &ast.IfStmt{If: $4, Then: $6})
		$$.SetPosition($1.Position())
	}
+   /* stmt_if 加 else { 代码块 } */
	| stmt_if ELSE '{' compstmt '}'
	{
		if $$.(*ast.IfStmt).Else != nil {
			yylex.Error("multiple else statement")
		} else {
			$$.(*ast.IfStmt).Else = append($$.(*ast.IfStmt).Else, $4...)
		}
		$$.SetPosition($1.Position())
	}
+   /* if xxx { 代码块 } */
+   /* 最简单的 stmt_if 就是上面这个形式 */
	| IF expr '{' compstmt '}'
	{
		$$ = &ast.IfStmt{If: $2, Then: $4, Else: nil}
		$$.SetPosition($1.Position())
	}

+ /*
+   switch...case...代码块
+   注意：这里面的代码都是switch里面的
+ */
stmt_cases :
+   /* 空 */
	{
		$$ = []ast.Stmt{}
	}
+   /* 一个case */
	| opt_terms stmt_case
	{
		$$ = []ast.Stmt{$2}
	}
+   /* 一个default */
	| opt_terms stmt_default
	{
		$$ = []ast.Stmt{$2}
	}
+   /* 多个stmt_case */
	| stmt_cases stmt_case
	{
		$$ = append($1, $2)
	}
+   /* 多个stmt_default，然后就会报错 */
	| stmt_cases stmt_default
	{
		for _, stmt := range $1 {
			if _, ok := stmt.(*ast.DefaultStmt); ok {
				yylex.Error("multiple default statement")
			}
		}
		$$ = append($1, $2)
	}

+ /*
+   switch...case...代码块
+   注意：这里面的代码都是case里面的
+ */
stmt_case :
+   /* case expr : 代码块 */
	CASE expr ':' opt_terms compstmt
	{
		$$ = &ast.CaseStmt{Expr: $2, Stmts: $5}
	}

+ /*
+   switch...case...代码块
+   注意：这里面的代码都是default里面的
+ */
stmt_default :
+   /* default : 代码块 */
	DEFAULT ':' opt_terms compstmt
	{
		$$ = &ast.DefaultStmt{Stmts: $4}
	}

array_count :
	{
		$$ = ast.ArrayCount{Count: 0}
	}
	| '[' ']'
	{
		$$ = ast.ArrayCount{Count: 1}
	}
	| array_count '[' ']'
	{
		$$.Count = $$.Count + 1
	}

expr_pair :
	STRING ':' expr
	{
		$$ = &ast.PairExpr{Key: $1.Lit, Value: $3}
	}

expr_pairs :
	{
		$$ = []ast.Expr{}
	}
	| expr_pair
	{
		$$ = []ast.Expr{$1}
	}
	| expr_pairs ',' opt_terms expr_pair
	{
		$$ = append($1, $4)
	}

+   /* name数组 */
expr_idents :
+   /* 空 */
	{
		$$ = []string{}
	}
+   /* name */
	| IDENT
	{
		$$ = []string{$1.Lit}
	}
+   /* name, ? */
	| expr_idents ',' opt_terms IDENT
	{
		$$ = append($1, $4.Lit)
	}

expr_type :
+   /* name */
	IDENT
	{
		$$ = $1.Lit
	}
+   /* some.name */
	| expr_type '.' IDENT
	{
		$$ = $$ + "." + $3.Lit
	}

+   /* a,b=b,a */
expr_lets : expr_many '=' expr_many
	{
		$$ = &ast.LetsExpr{Lhss: $1, Operator: "=", Rhss: $3}
	}

expr_many :
	expr
	{
		$$ = []ast.Expr{$1}
	}
	| exprs ',' opt_terms expr
	{
		$$ = append($1, $4)
	}
	| exprs ',' opt_terms IDENT
	{
		$$ = append($1, &ast.IdentExpr{Lit: $4.Lit})
	}

+  /* exprs 多个表达式 */
exprs :
+   /* 空 */
	{
		$$ = nil
	}
+   /* 一个式子 expr  */
	| expr
	{
		$$ = []ast.Expr{$1}
	}
+   /* 逗号分隔的多个 expr */
	| exprs ',' opt_terms expr
	{
		$$ = append($1, $4)
	}
+   /* 逗号分隔的多个 IDENT */
	| exprs ',' opt_terms IDENT
	{
		$$ = append($1, &ast.IdentExpr{Lit: $4.Lit})
	}

+   /* 一个式子 expr  */
expr :
+   /* IDENT 由字母组成的单词 */
	IDENT
	{
		$$ = &ast.IdentExpr{Lit: $1.Lit}
		$$.SetPosition($1.Position())
	}
+   /* 数字 */
	| NUMBER
	{
		$$ = &ast.NumberExpr{Lit: $1.Lit}
		$$.SetPosition($1.Position())
	}
+   /* -expr */
	| '-' expr %prec UNARY
	{
		$$ = &ast.UnaryExpr{Operator: "-", Expr: $2}
		$$.SetPosition($2.Position())
	}
+   /* !expr */
	| '!' expr %prec UNARY
	{
		$$ = &ast.UnaryExpr{Operator: "!", Expr: $2}
		$$.SetPosition($2.Position())
	}
+   /* ^expr */
	| '^' expr %prec UNARY
	{
		$$ = &ast.UnaryExpr{Operator: "^", Expr: $2}
		$$.SetPosition($2.Position())
	}
+   /* &IDENT */
	| '&' IDENT %prec UNARY
	{
		$$ = &ast.AddrExpr{Expr: &ast.IdentExpr{Lit: $2.Lit}}
		$$.SetPosition($2.Position())
	}
	| '&' expr '.' IDENT %prec UNARY
	{
		$$ = &ast.AddrExpr{Expr: &ast.MemberExpr{Expr: $2, Name: $4.Lit}}
		$$.SetPosition($2.Position())
	}
+   /* *IDENT */
	| '*' IDENT %prec UNARY
	{
		$$ = &ast.DerefExpr{Expr: &ast.IdentExpr{Lit: $2.Lit}}
		$$.SetPosition($2.Position())
	}
	| '*' expr '.' IDENT %prec UNARY
	{
		$$ = &ast.DerefExpr{Expr: &ast.MemberExpr{Expr: $2, Name: $4.Lit}}
		$$.SetPosition($2.Position())
	}
+   /* 字符串，"" 、 \'\' 、 ``之间的部分 */
	| STRING
	{
		$$ = &ast.StringExpr{Lit: $1.Lit}
		$$.SetPosition($1.Position())
	}
+   /* true */
	| TRUE
	{
		$$ = &ast.ConstExpr{Value: $1.Lit}
		$$.SetPosition($1.Position())
	}
+   /* false */
	| FALSE
	{
		$$ = &ast.ConstExpr{Value: $1.Lit}
		$$.SetPosition($1.Position())
	}
+   /* nil */
	| NIL
	{
		$$ = &ast.ConstExpr{Value: $1.Lit}
		$$.SetPosition($1.Position())
	}
+   /* expr ? expr : expr */
	| expr '?' expr ':' expr
	{
		$$ = &ast.TernaryOpExpr{Expr: $1, Lhs: $3, Rhs: $5}
		$$.SetPosition($1.Position())
	}
+   /* expr.IDENT */
	| expr '.' IDENT
	{
		$$ = &ast.MemberExpr{Expr: $1, Name: $3.Lit}
		$$.SetPosition($1.Position())
	}
	| FUNC '(' expr_idents ')' '{' compstmt '}'
	{
		$$ = &ast.FuncExpr{Params: $3, Stmts: $6}
		$$.SetPosition($1.Position())
	}
	| FUNC '(' expr_idents VARARG ')' '{' compstmt '}'
	{
		$$ = &ast.FuncExpr{Params: $3, Stmts: $7, VarArg: true}
		$$.SetPosition($1.Position())
	}
	| FUNC IDENT '(' expr_idents ')' '{' compstmt '}'
	{
		$$ = &ast.FuncExpr{Name: $2.Lit, Params: $4, Stmts: $7}
		$$.SetPosition($1.Position())
	}
	| FUNC IDENT '(' expr_idents VARARG ')' '{' compstmt '}'
	{
		$$ = &ast.FuncExpr{Name: $2.Lit, Params: $4, Stmts: $8, VarArg: true}
		$$.SetPosition($1.Position())
	}
	| '[' opt_terms exprs opt_terms ']'
	{
		$$ = &ast.ArrayExpr{Exprs: $3}
		if l, ok := yylex.(*Lexer); ok { $$.SetPosition(l.pos) }
	}
	| '[' opt_terms exprs ',' opt_terms ']'
	{
		$$ = &ast.ArrayExpr{Exprs: $3}
		if l, ok := yylex.(*Lexer); ok { $$.SetPosition(l.pos) }
	}
+   /* ? */
	| '{' opt_terms expr_pairs opt_terms '}'
	{
		mapExpr := make(map[string]ast.Expr)
		for _, v := range $3 {
			mapExpr[v.(*ast.PairExpr).Key] = v.(*ast.PairExpr).Value
		}
		$$ = &ast.MapExpr{MapExpr: mapExpr}
		if l, ok := yylex.(*Lexer); ok { $$.SetPosition(l.pos) }
	}
+   /* ? */
	| '{' opt_terms expr_pairs ',' opt_terms '}'
	{
		mapExpr := make(map[string]ast.Expr)
		for _, v := range $3 {
			mapExpr[v.(*ast.PairExpr).Key] = v.(*ast.PairExpr).Value
		}
		$$ = &ast.MapExpr{MapExpr: mapExpr}
		if l, ok := yylex.(*Lexer); ok { $$.SetPosition(l.pos) }
	}
+   /* (expr) */
	| '(' expr ')'
	{
		$$ = &ast.ParenExpr{SubExpr: $2}
		if l, ok := yylex.(*Lexer); ok { $$.SetPosition(l.pos) }
	}
+   /* expr + expr */
	| expr '+' expr
	{
		$$ = &ast.BinOpExpr{Lhs: $1, Operator: "+", Rhs: $3}
		$$.SetPosition($1.Position())
	}
+   /* expr - expr */
	| expr '-' expr
	{
		$$ = &ast.BinOpExpr{Lhs: $1, Operator: "-", Rhs: $3}
		$$.SetPosition($1.Position())
	}
+   /* expr * expr */
	| expr '*' expr
	{
		$$ = &ast.BinOpExpr{Lhs: $1, Operator: "*", Rhs: $3}
		$$.SetPosition($1.Position())
	}
+   /* expr / expr */
	| expr '/' expr
	{
		$$ = &ast.BinOpExpr{Lhs: $1, Operator: "/", Rhs: $3}
		$$.SetPosition($1.Position())
	}
+   /* expr % expr */
	| expr '%' expr
	{
		$$ = &ast.BinOpExpr{Lhs: $1, Operator: "%", Rhs: $3}
		$$.SetPosition($1.Position())
	}
+   /* expr ** expr */
	| expr POW expr
	{
		$$ = &ast.BinOpExpr{Lhs: $1, Operator: "**", Rhs: $3}
		$$.SetPosition($1.Position())
	}
+   /* expr << expr */
	| expr SHIFTLEFT expr
	{
		$$ = &ast.BinOpExpr{Lhs: $1, Operator: "<<", Rhs: $3}
		$$.SetPosition($1.Position())
	}
+   /* expr >> expr */
	| expr SHIFTRIGHT expr
	{
		$$ = &ast.BinOpExpr{Lhs: $1, Operator: ">>", Rhs: $3}
		$$.SetPosition($1.Position())
	}
+   /* expr == expr */
	| expr EQEQ expr
	{
		$$ = &ast.BinOpExpr{Lhs: $1, Operator: "==", Rhs: $3}
		$$.SetPosition($1.Position())
	}
+   /* expr != expr */
	| expr NEQ expr
	{
		$$ = &ast.BinOpExpr{Lhs: $1, Operator: "!=", Rhs: $3}
		$$.SetPosition($1.Position())
	}
+   /* expr > expr */
	| expr '>' expr
	{
		$$ = &ast.BinOpExpr{Lhs: $1, Operator: ">", Rhs: $3}
		$$.SetPosition($1.Position())
	}
+   /* expr >= expr */
	| expr GE expr
	{
		$$ = &ast.BinOpExpr{Lhs: $1, Operator: ">=", Rhs: $3}
		$$.SetPosition($1.Position())
	}
+   /* expr < expr */
	| expr '<' expr
	{
		$$ = &ast.BinOpExpr{Lhs: $1, Operator: "<", Rhs: $3}
		$$.SetPosition($1.Position())
	}
+   /* expr <= expr */
	| expr LE expr
	{
		$$ = &ast.BinOpExpr{Lhs: $1, Operator: "<=", Rhs: $3}
		$$.SetPosition($1.Position())
	}
+   /* expr += expr */
	| expr PLUSEQ expr
	{
		$$ = &ast.AssocExpr{Lhs: $1, Operator: "+=", Rhs: $3}
		$$.SetPosition($1.Position())
	}
+   /* expr -= expr */
	| expr MINUSEQ expr
	{
		$$ = &ast.AssocExpr{Lhs: $1, Operator: "-=", Rhs: $3}
		$$.SetPosition($1.Position())
	}
+   /* expr *= expr */
	| expr MULEQ expr
	{
		$$ = &ast.AssocExpr{Lhs: $1, Operator: "*=", Rhs: $3}
		$$.SetPosition($1.Position())
	}
+   /* expr /= expr */
	| expr DIVEQ expr
	{
		$$ = &ast.AssocExpr{Lhs: $1, Operator: "/=", Rhs: $3}
		$$.SetPosition($1.Position())
	}
+   /* expr &= expr */
	| expr ANDEQ expr
	{
		$$ = &ast.AssocExpr{Lhs: $1, Operator: "&=", Rhs: $3}
		$$.SetPosition($1.Position())
	}
+   /* expr |= expr */
	| expr OREQ expr
	{
		$$ = &ast.AssocExpr{Lhs: $1, Operator: "|=", Rhs: $3}
		$$.SetPosition($1.Position())
	}
+   /* expr ++ */
	| expr PLUSPLUS
	{
		$$ = &ast.AssocExpr{Lhs: $1, Operator: "++"}
		$$.SetPosition($1.Position())
	}
+   /* expr -- */
	| expr MINUSMINUS
	{
		$$ = &ast.AssocExpr{Lhs: $1, Operator: "--"}
		$$.SetPosition($1.Position())
	}
+   /* expr | expr */
	| expr '|' expr
	{
		$$ = &ast.BinOpExpr{Lhs: $1, Operator: "|", Rhs: $3}
		$$.SetPosition($1.Position())
	}
+   /* expr || expr */
	| expr OROR expr
	{
		$$ = &ast.BinOpExpr{Lhs: $1, Operator: "||", Rhs: $3}
		$$.SetPosition($1.Position())
	}
+   /* expr & expr */
	| expr '&' expr
	{
		$$ = &ast.BinOpExpr{Lhs: $1, Operator: "&", Rhs: $3}
		$$.SetPosition($1.Position())
	}
+   /* expr && expr */
	| expr ANDAND expr
	{
		$$ = &ast.BinOpExpr{Lhs: $1, Operator: "&&", Rhs: $3}
		$$.SetPosition($1.Position())
	}
+   /* IDENT(agrs ...) */
	| IDENT '(' exprs VARARG ')'
	{
		$$ = &ast.CallExpr{Name: $1.Lit, SubExprs: $3, VarArg: true}
		$$.SetPosition($1.Position())
	}
+   /* func_name(args) */
	| IDENT '(' exprs ')'
	{
		$$ = &ast.CallExpr{Name: $1.Lit, SubExprs: $3}
		$$.SetPosition($1.Position())
	}
+   /* go func_name(args...) */
	| GO IDENT '(' exprs VARARG ')'
	{
		$$ = &ast.CallExpr{Name: $2.Lit, SubExprs: $4, VarArg: true, Go: true}
		$$.SetPosition($2.Position())
	}
+   /* go func_name(args) */
	| GO IDENT '(' exprs ')'
	{
		$$ = &ast.CallExpr{Name: $2.Lit, SubExprs: $4, Go: true}
		$$.SetPosition($2.Position())
	}
+   /* func(args...) */
	| expr '(' exprs VARARG ')'
	{
		$$ = &ast.AnonCallExpr{Expr: $1, SubExprs: $3, VarArg: true}
		$$.SetPosition($1.Position())
	}
+   /* func(args) */	
	| expr '(' exprs ')'
	{
		$$ = &ast.AnonCallExpr{Expr: $1, SubExprs: $3}
		$$.SetPosition($1.Position())
	}
+   /* go ...(...) */	
	| GO expr '(' exprs VARARG ')'
	{
		$$ = &ast.AnonCallExpr{Expr: $2, SubExprs: $4, VarArg: true, Go: true}
		$$.SetPosition($2.Position())
	}
+   /* go ...(...) */	
	| GO expr '(' exprs ')'
	{
		$$ = &ast.AnonCallExpr{Expr: $2, SubExprs: $4, Go: true}
		$$.SetPosition($1.Position())
	}
+   /* a[...] */	
	| IDENT '[' expr ']'
	{
		$$ = &ast.ItemExpr{Value: &ast.IdentExpr{Lit: $1.Lit}, Index: $3}
		$$.SetPosition($1.Position())
	}
+   /* ...[...] */	
	| expr '[' expr ']'
	{
		$$ = &ast.ItemExpr{Value: $1, Index: $3}
		$$.SetPosition($1.Position())
	}
+   /* a[10:20] */	
	| IDENT '[' expr ':' expr ']'
	{
		$$ = &ast.SliceExpr{Value: &ast.IdentExpr{Lit: $1.Lit}, Begin: $3, End: $5}
		$$.SetPosition($1.Position())
	}
+   /* a[10:] */	
	| IDENT '[' expr ':' ']'
	{
		$$ = &ast.SliceExpr{Value: &ast.IdentExpr{Lit: $1.Lit}, Begin: $3, End: nil}
		$$.SetPosition($1.Position())
	}
+   /* a[10:20] */	
	| IDENT '[' ':' expr ']'
	{
		$$ = &ast.SliceExpr{Value: &ast.IdentExpr{Lit: $1.Lit}, Begin: nil, End: $4}
		$$.SetPosition($1.Position())
	}
+   /* ...[10:20] */	
	| expr '[' expr ':' expr ']'
	{
		$$ = &ast.SliceExpr{Value: $1, Begin: $3, End: $5}
		$$.SetPosition($1.Position())
	}
+   /* ...[10:] */	
	| expr '[' expr ':' ']'
	{
		$$ = &ast.SliceExpr{Value: $1, Begin: $3, End: nil}
		$$.SetPosition($1.Position())
	}
+   /* ...[:10] */	
	| expr '[' ':' expr ']'
	{
		$$ = &ast.SliceExpr{Value: $1, Begin: nil, End: $4}
		$$.SetPosition($1.Position())
	}
+   /* len(...) */	
	| LEN '(' expr ')'
	{
		$$ = &ast.LenExpr{Expr: $3}
		$$.SetPosition($1.Position())
	}
+   /* new(Type) */
	| NEW '(' expr_type ')'
	{
		$$ = &ast.NewExpr{Type: $3}
		$$.SetPosition($1.Position())
	}
+   /* make(chan string) */
	| MAKE '(' CHAN expr_type ')'
	{
		$$ = &ast.MakeChanExpr{Type: $4, SizeExpr: nil}
		$$.SetPosition($1.Position())
	}
+   /* make(chan string, 10) */
	| MAKE '(' CHAN expr_type ',' expr ')'
	{
		$$ = &ast.MakeChanExpr{Type: $4, SizeExpr: $6}
		$$.SetPosition($1.Position())
	}
+   /* ? */
	| MAKE '(' array_count expr_type ')'
	{
		$$ = &ast.MakeExpr{Dimensions: $3.Count, Type: $4}
		$$.SetPosition($1.Position())
	}
+   /* make([]string, 10) */
	| MAKE '(' array_count expr_type ',' expr ')'
	{
		$$ = &ast.MakeExpr{Dimensions: $3.Count,Type: $4, LenExpr: $6}
		$$.SetPosition($1.Position())
	}
+   /* make([]string, 10, 10) */
	| MAKE '(' array_count expr_type ',' expr ',' expr ')'
	{
		$$ = &ast.MakeExpr{Dimensions: $3.Count,Type: $4, LenExpr: $6, CapExpr: $8}
		$$.SetPosition($1.Position())
	}
+   /* ? todo */
	| MAKE '(' TYPE IDENT ',' expr ')'
	{
		$$ = &ast.MakeTypeExpr{Name: $4.Lit, Type: $6}
		$$.SetPosition($1.Position())
	}
+   /* a<-b */
	| expr OPCHAN expr
	{
		$$ = &ast.ChanExpr{Lhs: $1, Rhs: $3}
		$$.SetPosition($1.Position())
	}
+   /* <-b */
	| OPCHAN expr
	{
		$$ = &ast.ChanExpr{Rhs: $2}
		$$.SetPosition($2.Position())
	}

+ /* 空字符串或者terms（term（分号或者换行）或者多个 term） */
opt_terms : /* none */
	| terms
	;

+ /* term（分号或者换行）或者多个 term*/
terms : term
	{
	}
	| terms term
	{
	}
	;

+ /* 分号或者换行 */
term : ';'
	{
	}
	| '\n'
	{
	}
	;

+ /* 第二个%%之前是规则 */

%%

```

参考：
* https://blog.golang.org/generate
* https://github.com/cdstelly/goyacc-sample
* https://www.ibm.com/support/knowledgecenter/zh/ssw_aix_71/com.ibm.aix.genprogc/chapter13.htm
* https://www.ibm.com/support/knowledgecenter/zh/ssw_aix_71/com.ibm.aix.genprogc/using_yacc_file.htm
* https://www.ibm.com/support/knowledgecenter/zh/ssw_aix_71/com.ibm.aix.genprogc/yaac_file_declarations.htm
* https://www.ibm.com/support/knowledgecenter/zh/ssw_aix_71/com.ibm.aix.genprogc/yacc_rules.htm
* https://www.ibm.com/support/knowledgecenter/zh/ssw_aix_71/com.ibm.aix.genprogc/yacc_actions.htm
* http://jiayaowei.blogspot.com/2007/12/lexyaccyacc_03.html
* http://shahuwang.com/%E7%BC%96%E8%AF%91%E5%8E%9F%E7%90%86/%E5%AE%9E%E7%8E%B0%E8%87%AA%E5%B7%B1%E7%9A%84%E8%84%9A%E6%9C%AC%E8%AF%AD%E8%A8%80(%E4%BA%8C).html
* https://github.com/shahuwang/yaccalc
* https://github.com/cdstelly/goyacc-sample