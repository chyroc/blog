# anko源代码阅读之lex/goyacc（一）

- time 2018-03-20

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