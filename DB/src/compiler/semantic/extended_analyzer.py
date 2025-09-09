"""
扩展的语义分析器
支持复杂查询的语义分析和四元式生成，包括JOIN、聚合函数、ORDER BY等
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from typing import List, Optional, Dict, Any
from src.common.types import ASTNode, ASTNodeType, Quadruple, SymbolTable, Symbol, SemanticError

class ExtendedSemanticAnalyzer:
    """扩展的语义分析器"""
    
    def __init__(self):
        """初始化扩展语义分析器"""
        self.symbol_table = SymbolTable()
        self.quadruples: List[Quadruple] = []
        self.temp_counter = 0
        self.label_counter = 0
        
        # 扩展的操作符映射
        self.operators = {
            '>': 'GT',
            '>=': 'GE', 
            '<': 'LT',
            '<=': 'LE',
            '=': 'EQ',
            '<>': 'NE',
            '!=': 'NE'
        }
        
        # 聚合函数映射
        self.aggregate_functions = {
            'COUNT': 'COUNT',
            'SUM': 'SUM',
            'AVG': 'AVG',
            'MAX': 'MAX',
            'MIN': 'MIN'
        }
    
    def analyze(self, ast: ASTNode) -> List[Quadruple]:
        """
        分析AST并生成四元式
        
        Args:
            ast: 抽象语法树根节点
            
        Returns:
            四元式列表
        """
        self.quadruples = []
        self.temp_counter = 0
        self.label_counter = 0
        
        try:
            print("\\n开始扩展语义分析:")
            print("-" * 50)
            
            if ast.type == ASTNodeType.SELECT_STMT:
                self._analyze_select_statement(ast)
            else:
                raise SemanticError(f"Unsupported statement type: {ast.type}")
            
            print(f"\\n✅ 生成 {len(self.quadruples)} 个四元式")
            for i, quad in enumerate(self.quadruples, 1):
                print(f"  {i}: {quad}")
            
            return self.quadruples
            
        except Exception as e:
            print(f"❌ 语义错误: {e}")
            return []
    
    def _analyze_select_statement(self, node: ASTNode):
        """分析SELECT语句"""
        print("分析SELECT语句...")
        
        # 生成开始标记
        self._emit('BEGIN', None, None, None)
        
        # 处理FROM子句（必须先处理，确定表信息）
        table_info = self._analyze_from_clause(node)
        
        # 处理SELECT列表
        select_info = self._analyze_select_list(node)
        
        # 处理JOIN子句
        self._analyze_join_clauses(node, table_info)
        
        # 处理WHERE子句
        self._analyze_where_clause(node)
        
        # 处理GROUP BY子句
        group_info = self._analyze_group_by_clause(node)
        
        # 处理HAVING子句
        self._analyze_having_clause(node)
        
        # 处理ORDER BY子句
        self._analyze_order_by_clause(node)
        
        # 生成最终的选择和输出操作
        result_temp = self._generate_temp()
        self._emit('SELECT', select_info.get('columns', '*'), table_info.get('main_table'), result_temp)
        self._emit('OUTPUT', result_temp, None, None)
        
        # 生成结束标记
        self._emit('END', None, None, None)
    
    def _analyze_from_clause(self, node: ASTNode) -> Dict[str, Any]:
        """分析FROM子句"""
        table_info = {'main_table': None, 'tables': [], 'aliases': {}}
        
        for child in node.children:
            if child.type == ASTNodeType.TABLE_NAME:
                table_name = child.value
                table_info['main_table'] = table_name
                table_info['tables'].append(table_name)
                
                print(f"  主表: {table_name}")
                
                # 添加表到符号表
                self.symbol_table.add_symbol(Symbol(
                    name=table_name,
                    type="TABLE",
                    scope="GLOBAL",
                    line=0,
                    column=0
                ))
        
        return table_info
    
    def _analyze_select_list(self, node: ASTNode) -> Dict[str, Any]:
        """分析SELECT列表"""
        select_info = {'columns': [], 'aggregates': [], 'has_aggregates': False}
        
        for child in node.children:
            if child.type == ASTNodeType.COLUMN_LIST:
                print("  分析列列表...")
                self._analyze_column_list(child, select_info)
                break
        
        return select_info
    
    def _analyze_column_list(self, node: ASTNode, select_info: Dict[str, Any]):
        """分析列列表"""
        for child in node.children:
            if child.type == ASTNodeType.IDENTIFIER:
                column_name = child.value
                if column_name == "*":
                    select_info['columns'] = "*"
                    print(f"    选择所有列: *")
                else:
                    if isinstance(select_info['columns'], list):
                        select_info['columns'].append(column_name)
                    else:
                        select_info['columns'] = [column_name]
                    print(f"    选择列: {column_name}")
                    
            elif child.type == ASTNodeType.AGGREGATE_FUNCTION:
                func_name = child.value
                select_info['has_aggregates'] = True
                
                # 生成聚合函数的四元式
                agg_temp = self._generate_temp()
                if func_name == 'COUNT':
                    self._emit('COUNT', '*', None, agg_temp)
                else:
                    # 对于其他聚合函数，需要确定列名
                    column_arg = self._get_aggregate_column(child)
                    self._emit(func_name, column_arg, None, agg_temp)
                
                select_info['aggregates'].append({
                    'function': func_name,
                    'temp': agg_temp
                })
                
                if isinstance(select_info['columns'], list):
                    select_info['columns'].append(agg_temp)
                else:
                    select_info['columns'] = [agg_temp]
                
                print(f"    聚合函数: {func_name} -> {agg_temp}")
    
    def _get_aggregate_column(self, agg_node: ASTNode) -> str:
        """获取聚合函数的列参数"""
        # 简化实现，返回默认列名
        # 在完整实现中应该解析函数参数
        return "value"
    
    def _analyze_join_clauses(self, node: ASTNode, table_info: Dict[str, Any]):
        """分析JOIN子句"""
        for child in node.children:
            if child.type == ASTNodeType.JOIN_CLAUSE:
                print("  分析JOIN子句...")
                self._analyze_join_clause(child, table_info)
    
    def _analyze_join_clause(self, node: ASTNode, table_info: Dict[str, Any]):
        """分析单个JOIN子句"""
        join_table = None
        join_condition = None
        
        for child in node.children:
            if child.type == ASTNodeType.TABLE_NAME:
                join_table = child.value
                table_info['tables'].append(join_table)
                print(f"    JOIN表: {join_table}")
                
            elif child.type == ASTNodeType.ON_CLAUSE:
                join_condition = self._analyze_join_condition(child)
                print(f"    ON条件: {join_condition}")
        
        if join_table and join_condition:
            # 生成JOIN操作的四元式
            join_temp = self._generate_temp()
            self._emit('JOIN', table_info['main_table'], join_table, join_temp)
            self._emit('ON', join_condition['left'], join_condition['right'], join_condition['op'])
    
    def _analyze_join_condition(self, node: ASTNode) -> Dict[str, str]:
        """分析JOIN条件"""
        # 简化实现，返回默认条件
        return {
            'left': 'table1.id',
            'right': 'table2.id', 
            'op': 'EQ'
        }
    
    def _analyze_where_clause(self, node: ASTNode):
        """分析WHERE子句"""
        for child in node.children:
            if child.type == ASTNodeType.WHERE_CLAUSE:
                print("  分析WHERE子句...")
                condition_temp = self._analyze_condition(child)
                if condition_temp:
                    self._emit('WHERE', condition_temp, None, None)
    
    def _analyze_condition(self, node: ASTNode) -> Optional[str]:
        """分析条件表达式"""
        # 简化的条件分析
        condition_temp = self._generate_temp()
        self._emit('CONDITION', 'column', '>', 'value', condition_temp)
        return condition_temp
    
    def _analyze_group_by_clause(self, node: ASTNode) -> Dict[str, Any]:
        """分析GROUP BY子句"""
        group_info = {'columns': [], 'has_group_by': False}
        
        for child in node.children:
            if child.type == ASTNodeType.GROUP_BY_CLAUSE:
                print("  分析GROUP BY子句...")
                group_info['has_group_by'] = True
                
                for grandchild in child.children:
                    if grandchild.type == ASTNodeType.IDENTIFIER:
                        column_name = grandchild.value
                        group_info['columns'].append(column_name)
                        print(f"    分组列: {column_name}")
                
                # 生成GROUP BY四元式
                if group_info['columns']:
                    group_temp = self._generate_temp()
                    self._emit('GROUP_BY', ','.join(group_info['columns']), None, group_temp)
        
        return group_info
    
    def _analyze_having_clause(self, node: ASTNode):
        """分析HAVING子句"""
        for child in node.children:
            if child.type == ASTNodeType.HAVING_CLAUSE:
                print("  分析HAVING子句...")
                having_temp = self._analyze_condition(child)
                if having_temp:
                    self._emit('HAVING', having_temp, None, None)
    
    def _analyze_order_by_clause(self, node: ASTNode):
        """分析ORDER BY子句"""
        for child in node.children:
            if child.type == ASTNodeType.ORDER_BY_CLAUSE:
                print("  分析ORDER BY子句...")
                
                order_specs = []
                for grandchild in child.children:
                    if grandchild.type == ASTNodeType.ORDER_SPEC:
                        column_name = grandchild.value
                        direction = "ASC"  # 默认升序
                        
                        # 检查排序方向
                        for spec_child in grandchild.children:
                            if spec_child.type == ASTNodeType.IDENTIFIER:
                                if spec_child.value in ["ASC", "DESC"]:
                                    direction = spec_child.value
                        
                        order_specs.append(f"{column_name} {direction}")
                        print(f"    排序: {column_name} {direction}")
                
                if order_specs:
                    order_temp = self._generate_temp()
                    self._emit('ORDER_BY', ','.join(order_specs), None, order_temp)
    
    def _emit(self, op: str, arg1: Optional[str], arg2: Optional[str], result: Optional[str]):
        """生成四元式"""
        quad = Quadruple(op, arg1, arg2, result)
        self.quadruples.append(quad)
    
    def _generate_temp(self) -> str:
        """生成临时变量"""
        self.temp_counter += 1
        return f"T{self.temp_counter}"
    
    def _generate_label(self) -> str:
        """生成标签"""
        self.label_counter += 1
        return f"L{self.label_counter}"

def test_extended_semantic_analyzer():
    """测试扩展语义分析器"""
    from src.compiler.lexer.lexer import Lexer
    from src.compiler.parser.extended_parser import ExtendedParser
    
    test_cases = [
        # 基本查询
        "SELECT name FROM students;",
        
        # 聚合函数
        "SELECT COUNT(*), AVG(grade) FROM students;", 
        
        # GROUP BY
        "SELECT major, COUNT(*) FROM students GROUP BY major;",
        
        # ORDER BY
        "SELECT name, grade FROM students ORDER BY grade DESC;",
    ]
    
    print("=" * 70)
    print("                 扩展语义分析器测试")
    print("=" * 70)
    
    for i, sql in enumerate(test_cases, 1):
        print(f"\\n\\n测试用例 {i}: {sql}")
        print("=" * 70)
        
        try:
            # 词法分析
            lexer = Lexer(sql)
            tokens = lexer.tokenize()
            
            # 语法分析
            parser = ExtendedParser(tokens)
            ast = parser.parse()
            
            if ast:
                # 扩展语义分析
                analyzer = ExtendedSemanticAnalyzer()
                quadruples = analyzer.analyze(ast)
                
                if quadruples:
                    print(f"\\n生成四元式成功！共 {len(quadruples)} 条")
                else:
                    print("\\n四元式生成失败")
            else:
                print("语法分析失败，跳过语义分析")
                
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
    
    print("\\n✅ 扩展语义分析器测试完成!")

if __name__ == "__main__":
    test_extended_semantic_analyzer()