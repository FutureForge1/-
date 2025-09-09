"""
公共数据结构和常量定义
"""

from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional

# ======================== Token类型定义 ========================

class TokenType(Enum):
    """Token类型枚举"""
    # 关键字
    SELECT = "SELECT"
    FROM = "FROM"
    WHERE = "WHERE"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    
    # 复杂查询关键字
    JOIN = "JOIN"
    INNER = "INNER"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    OUTER = "OUTER"
    FULL = "FULL"
    ON = "ON"
    
    # 聚合函数关键字
    GROUP = "GROUP"
    BY = "BY"
    HAVING = "HAVING"
    COUNT = "COUNT"
    SUM = "SUM"
    AVG = "AVG"
    MAX = "MAX"
    MIN = "MIN"
    
    # 排序关键字
    ORDER = "ORDER"
    ASC = "ASC"
    DESC = "DESC"
    
    # 子查询关键字
    IN = "IN"
    EXISTS = "EXISTS"
    ALL = "ALL"
    ANY = "ANY"
    SOME = "SOME"
    
    # DDL关键字
    CREATE = "CREATE"
    TABLE = "TABLE"
    DROP = "DROP"
    ALTER = "ALTER"
    INDEX = "INDEX"
    
    # DML关键字
    INSERT = "INSERT"
    INTO = "INTO"
    VALUES = "VALUES"
    UPDATE = "UPDATE"
    SET = "SET"
    DELETE = "DELETE"
    
    # 数据类型关键字
    INT = "INT"
    INTEGER = "INTEGER"
    VARCHAR = "VARCHAR"
    CHAR = "CHAR"
    DECIMAL = "DECIMAL"
    FLOAT = "FLOAT"
    DOUBLE = "DOUBLE"
    TEXT = "TEXT"
    DATE = "DATE"
    TIME = "TIME"
    DATETIME = "DATETIME"
    TIMESTAMP = "TIMESTAMP"
    
    # 约束关键字
    PRIMARY = "PRIMARY"
    KEY = "KEY"
    FOREIGN = "FOREIGN"
    REFERENCES = "REFERENCES"
    UNIQUE = "UNIQUE"
    CHECK = "CHECK"
    DEFAULT = "DEFAULT"
    NULL = "NULL"
    
    # 其他关键字
    DISTINCT = "DISTINCT"
    AS = "AS"
    UNION = "UNION"
    INTERSECT = "INTERSECT"
    EXCEPT = "EXCEPT"
    
    # 标识符和字面值
    IDENTIFIER = "IDENTIFIER"  # 表名、列名等
    NUMBER = "NUMBER"          # 数字
    STRING = "STRING"          # 字符串
    
    # 运算符
    EQUALS = "="              # 等于
    NOT_EQUALS = "<>"         # 不等于
    LESS_THAN = "<"           # 小于
    LESS_EQUAL = "<="         # 小于等于
    GREATER_THAN = ">"        # 大于
    GREATER_EQUAL = ">="      # 大于等于
    
    # 分隔符
    COMMA = ","               # 逗号
    SEMICOLON = ";"           # 分号
    LEFT_PAREN = "("          # 左括号
    RIGHT_PAREN = ")"         # 右括号
    ASTERISK = "*"            # 星号
    DOT = "."                 # 点号
    
    # 特殊标记
    EOF = "EOF"               # 文件结束
    UNKNOWN = "UNKNOWN"       # 未知字符

@dataclass
class Token:
    """Token数据结构"""
    type: TokenType
    value: str
    line: int
    column: int
    
    def __str__(self):
        return f"Token({self.type.value}, '{self.value}', {self.line}:{self.column})"

# ======================== 中间代码定义 ========================

@dataclass
class Quadruple:
    """四元式中间代码 [op, arg1, arg2, result]"""
    op: str              # 操作符
    arg1: Optional[str]  # 第一个操作数
    arg2: Optional[str]  # 第二个操作数
    result: str          # 结果
    
    def __str__(self):
        return f"({self.op}, {self.arg1 or '-'}, {self.arg2 or '-'}, {self.result})"

# ======================== 目标代码指令定义 ========================

class InstructionType(Enum):
    """目标代码指令类型"""
    OPEN = "OPEN"         # 打开表
    SCAN = "SCAN"         # 扫描记录
    FILTER = "FILTER"     # 按条件过滤
    PROJECT = "PROJECT"   # 投影列
    OUTPUT = "OUTPUT"     # 输出结果
    CLOSE = "CLOSE"       # 关闭表

@dataclass
class Instruction:
    """目标代码指令"""
    type: InstructionType
    operands: list[str]
    
    def __str__(self):
        operands_str = ", ".join(self.operands)
        return f"{self.type.value} {operands_str}"

# ======================== SQL语法树节点定义 ========================

class ASTNodeType(Enum):
    """抽象语法树节点类型"""
    SELECT_STMT = "SELECT_STATEMENT"
    COLUMN_LIST = "COLUMN_LIST"
    TABLE_NAME = "TABLE_NAME"
    WHERE_CLAUSE = "WHERE_CLAUSE"
    CONDITION = "CONDITION"
    IDENTIFIER = "IDENTIFIER"
    LITERAL = "LITERAL"
    
    # 复杂查询节点类型
    JOIN_CLAUSE = "JOIN_CLAUSE"
    JOIN_TYPE = "JOIN_TYPE"
    ON_CLAUSE = "ON_CLAUSE"
    
    # 聚合函数节点类型
    GROUP_BY_CLAUSE = "GROUP_BY_CLAUSE"
    HAVING_CLAUSE = "HAVING_CLAUSE"
    AGGREGATE_FUNCTION = "AGGREGATE_FUNCTION"
    
    # 排序节点类型
    ORDER_BY_CLAUSE = "ORDER_BY_CLAUSE"
    ORDER_SPEC = "ORDER_SPEC"
    
    # 子查询节点类型
    SUBQUERY = "SUBQUERY"
    
    # 表连接节点类型
    TABLE_REF = "TABLE_REF"
    TABLE_ALIAS = "TABLE_ALIAS"

@dataclass
class ASTNode:
    """抽象语法树节点"""
    type: ASTNodeType
    value: Optional[str] = None
    children: list['ASTNode'] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
    
    def add_child(self, child: 'ASTNode'):
        """添加子节点"""
        self.children.append(child)
    
    def __str__(self, level=0):
        indent = "  " * level
        result = f"{indent}{self.type.value}"
        if self.value:
            result += f": {self.value}"
        result += "\n"
        for child in self.children:
            result += child.__str__(level + 1)
        return result

# ======================== 符号表定义 ========================

@dataclass
class Symbol:
    """符号表条目"""
    name: str
    type: str
    scope: str
    line: int
    column: int

class SymbolTable:
    """符号表"""
    def __init__(self):
        self.symbols: dict[str, Symbol] = {}
    
    def add_symbol(self, symbol: Symbol):
        """添加符号"""
        self.symbols[symbol.name] = symbol
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """查找符号"""
        return self.symbols.get(name)
    
    def __str__(self):
        result = "Symbol Table:\n"
        for name, symbol in self.symbols.items():
            result += f"  {name}: {symbol.type} (line {symbol.line})\n"
        return result

# ======================== 错误处理 ========================

class CompilerError(Exception):
    """编译器错误基类"""
    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self.format_message())
    
    def format_message(self):
        if self.line > 0:
            return f"Error at line {self.line}, column {self.column}: {self.message}"
        return f"Error: {self.message}"

class LexicalError(CompilerError):
    """词法分析错误"""
    pass

class SyntaxError(CompilerError):
    """语法分析错误"""
    pass

class SemanticError(CompilerError):
    """语义分析错误"""
    pass

# ======================== 常量定义 ========================

# SQL关键字列表
SQL_KEYWORDS = {
    'SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'NOT',
    # 复杂查询关键字
    'JOIN', 'INNER', 'LEFT', 'RIGHT', 'OUTER', 'FULL', 'ON',
    # 聚合函数关键字
    'GROUP', 'BY', 'HAVING', 'COUNT', 'SUM', 'AVG', 'MAX', 'MIN',
    # 排序关键字
    'ORDER', 'ASC', 'DESC',
    # 子查询关键字
    'IN', 'EXISTS', 'ALL', 'ANY', 'SOME',
    # DDL关键字
    'CREATE', 'TABLE', 'DROP', 'ALTER', 'INDEX',
    # DML关键字
    'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET', 'DELETE',
    # 数据类型关键字
    'INT', 'INTEGER', 'VARCHAR', 'CHAR', 'DECIMAL', 'FLOAT', 'DOUBLE',
    'TEXT', 'DATE', 'TIME', 'DATETIME', 'TIMESTAMP',
    # 约束关键字
    'PRIMARY', 'KEY', 'FOREIGN', 'REFERENCES', 'UNIQUE', 'CHECK', 'DEFAULT', 'NULL',
    # 其他关键字
    'DISTINCT', 'AS', 'UNION', 'INTERSECT', 'EXCEPT'
}

# 运算符映射
OPERATORS = {
    '=': TokenType.EQUALS,
    '<>': TokenType.NOT_EQUALS,
    '<': TokenType.LESS_THAN,
    '<=': TokenType.LESS_EQUAL,
    '>': TokenType.GREATER_THAN,
    '>=': TokenType.GREATER_EQUAL,
}

# 分隔符映射
DELIMITERS = {
    ',': TokenType.COMMA,
    ';': TokenType.SEMICOLON,
    '(': TokenType.LEFT_PAREN,
    ')': TokenType.RIGHT_PAREN,
    '*': TokenType.ASTERISK,
    '.': TokenType.DOT,
}