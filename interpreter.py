from tokens import t

from utils import RTError

# for type hinting
import ast_parser

# for run function
from tokenizer import tokenize
from ast_parser import make_ast


class Object:
    def __init__(self, type_name='Object'):
        self.type_name = type_name
        self.pos_start = None
        self.pos_end = None
        self.context = None

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self
    
    def is_truthy(self):
        return Bool(True)
    
    def __repr__(self):
        return f"<object-of-type-{self.type_name}>"

    # arithmetic operations
    def operate_plus(self, other):
        return None, self.not_supported('+ operator', other)
    
    def operate_minus(self, other):
        return None, self.not_supported('- operator', other)

    def operate_mul(self, other):
        return None, self.not_supported('* operator', other)

    def operate_div(self, other):
        return None, self.not_supported('/ operator', other)

    def operate_pow(self, other):
        return None, self.not_supported('^ operator', other)

    # boolean operations
    def compare_eq(self, other):
        return None, self.not_supported('== operator', other)

    def compare_ne(self, other):
        return None, self.not_supported('!= operator', other)
    
    def compare_gt(self, other):
        return None, self.not_supported('> operator', other)
    
    def compare_lt(self, other):
        return None, self.not_supported('< operator', other)
    
    def compare_gte(self, other):
        return None, self.not_supported('>= operator', other)
    
    def compare_lte(self, other):
        return None, self.not_supported('<= operator', other)

    # logical operations
    def logic_and(self, other):
        return None, self.not_supported("'and' logic", other)

    def logic_or(self, other):
        return None, self.not_supported("'or' logic", other)

    def logic_not(self):
        return None, self.not_supported("'not' logic", self)
    
    def not_supported(self, what_is_not_supported, other=None):
        return RTError(self.pos_start, self.pos_end,
                       f"{self.type_name} does not support {what_is_not_supported} with {other.type_name}", self.context)


class Bool(Object):
    def __init__(self, value):
        Object.__init__(self)
        self.value = bool(value)
        self.type_name = 'Bool'
        
        self.pos_start = None
        self.pos_end = None
        self.context = None
    
    def __repr__(self):
        return 'true' if self.value else 'false'
    
    def __bool__(self):
        return self.value
    
    def is_truthy(self):
        return Bool(self.value)
    
    def copy(self):
        return Bool(self.value).set_pos(self.pos_start, self.pos_end).set_context(self.context)
    
    def logic_and(self, other):
        return Bool(self.value and other.value).set_context(self.context), None
    
    def logic_or(self, other):
        return Bool(self.value or other.value).set_context(self.context), None
    
    def logic_not(self):
        return Bool(not self.value).set_context(self.context)


class Number(Object):
    def __init__(self, value):
        Object.__init__(self)
        self.value = value
        self.type_name = 'Number'
        
        self.pos_start = None
        self.pos_end = None
        self.context = None
    
    def __repr__(self):
        return str(self.value)
    
    def __bool__(self):
        return bool(self.value)

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def is_truthy(self):
        return Bool(bool(self.value))
    
    # arithmetic operations
    def operate_plus(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return Object.operate_plus(self, other)  # makes not supported error
    
    def operate_minus(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return Object.operate_minus(self, other)  # makes not supported error
    
    def operate_mul(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return Object.operate_mul(self, other)  # makes not supported error
    
    def operate_div(self, other):
        if not isinstance(other, Number):
            return Object.operate_div(self, other)  # makes not supported error
        if other.value == 0:
            return None, RTError(other.pos_start, other.pos_end, "Division by Zero", self.context)
        return Number(self.value / other.value).set_context(self.context), None
    
    def operate_pow(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None
        else:
            return Object.operate_pow(self, other)  # makes not supported error
    
    # boolean operations
    def compare_eq(self, other):
        if isinstance(other, Number):
            return Bool(self.value == other.value).set_context(self.context), None
        else:
            return Object.compare_eq(self, other)  # makes not supported error

    def compare_ne(self, other):
        if isinstance(other, Number):
            return Bool(self.value != other.value).set_context(self.context), None
        else:
            return Object.compare_ne(self, other)  # makes not supported error

    def compare_gt(self, other):
        if isinstance(other, Number):
            return Bool(self.value > other.value).set_context(self.context), None
        else:
            return Object.compare_gt(self, other)  # makes not supported error
        
    def compare_lt(self, other):
        if isinstance(other, Number):
            return Bool(self.value < other.value).set_context(self.context), None
        else:
            return Object.compare_lt(self, other)  # makes not supported error

    def compare_gte(self, other):
        if isinstance(other, Number):
            return Bool(self.value >= other.value).set_context(self.context), None
        else:
            return Object.compare_gte(self, other)  # makes not supported error

    def compare_lte(self, other):
        if isinstance(other, Number):
            return Bool(self.value <= other.value).set_context(self.context), None
        else:
            return Object.compare_lte(self, other)  # makes not supported error
    
    # logical operations
    def logic_and(self, other):
        if isinstance(other, Number):
            return Bool(int(self.value and other.value)).set_context(self.context), None
        else:
            return Object.logic_and(self, other)  # makes not supported error

    def logic_or(self, other):
        if isinstance(other, Number):
            return Bool(int(self.value or other.value)).set_context(self.context), None
        else:
            return Object.logic_or(self, other)  # makes not supported error
    
    def logic_not(self):
        return Bool(int(not self.value)).set_context(self.context), None


class Function(Object):
    def __init__(self, name, parameters, body):
        Object.__init__(self)
        self.type_name = "Function"
        self.name = name
        self.parameters = parameters
        self.n_parameters = len(parameters)
        self.body = body
    
    def __repr__(self):
        return f"<Function {self.name}>"
    
    def execute(self, args):
        res = RTResult()
        context = Context(self.name, self.context, self.pos_start, SymbolMap(self.context.symbol_map))
        
        if self.n_parameters != len(args):
            return res.failure(
                RTError(self.pos_start, self.pos_end, ("Too many" if len(args) > self.n_parameters else "Not enough") +
                        f" arguments given into {self.name}, takes {len(self.parameters)}", context)
            )
        
        interpreter = Interpreter()
        
        # setting parameters to given values
        for i in range(self.n_parameters):
            parameter = self.parameters[i]
            arg = args[i]
            context.symbol_map.set(parameter.value, arg)
        
        value = res.register(interpreter.visit(self.body, context))
        if res.error: return res
        return res.success(value)
    
    def copy(self):
        return (
            Function(self.name, self.parameters, self.body)
            .set_context(self.context)
            .set_pos(self.pos_start, self.pos_end)
        )


class RTResult:
    def __init__(self):
        self.value = None
        self.error = None
    
    def register(self, res):
        if res.error: self.error = res.error
        return res.value

    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return self


class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None, symbol_map=None):
        self.display_name: str = display_name
        self.parent: Context = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_map: SymbolMap = symbol_map


class SymbolMap:
    def __init__(self, parent=None):
        self.symbol_map = {}
        self.parent = parent
    
    def get(self, var_name):
        value = self.symbol_map.get(var_name, None)
        if value is None and self.parent:
            return self.parent.get(var_name)
        return value
    
    def set(self, var_name, value):
        self.symbol_map[var_name] = value
    
    def remove(self, var_name):
        del self.symbol_map[var_name]


class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f'visit_{type(node).__name__} method is not defined')
    
    def visit_NumberNode(self, node: ast_parser.NumberNode, context):
        return RTResult().success(
            Number(node.tok.value).set_pos(node.pos_start, node.pos_end).set_context(context)
        )
    
    def visit_LiteralNode(self, node: ast_parser.LiteralNode, context):
        res = RTResult()
        if node.tok.value == 'true':
            return res.success(Bool(True).set_pos(node.pos_start, node.pos_end).set_context(context))
        if node.tok.value == 'false':
            return res.success(Bool(False).set_pos(node.pos_start, node.pos_end).set_context(context))
    
    def visit_VarAccessNode(self, node: ast_parser.VarAccessNode, context):
        res = RTResult()
        var_name = node.var_name.value
        value = context.symbol_map.get(var_name)
        
        if not value:
            return res.failure(
                RTError(node.pos_start, node.pos_end, f"'{var_name}' not defined", context)
            )
        
        value = value.copy().set_pos(node.pos_start, node.pos_end)
        
        return res.success(value)
    
    def visit_VarAssignNode(self, node: ast_parser.VarAssignNode, context):
        res = RTResult()
        var_name = node.var_name.value
        
        value = res.register(self.visit(node.value, context))
        if res.error: return res

        context.symbol_map.set(var_name, value)
        return res.success(value)
        
    def visit_BinOpNode(self, node: ast_parser.BinOpNode, context):
        res = RTResult()
        left = res.register(self.visit(node.left, context))
        if res.error: return res
        right = res.register(self.visit(node.right, context))
        if res.error: return res
        
        oper = node.oper
        
        if oper.is_type(t.PLUS):
            result, error = left.operate_plus(right)
        elif oper.is_type(t.MINUS):
            result, error = left.operate_minus(right)
        elif oper.is_type(t.MUL):
            result, error = left.operate_mul(right)
        elif oper.is_type(t.DIV):
            result, error = left.operate_div(right)
        elif oper.is_type(t.POW):
            result, error = left.operate_pow(right)
            
        elif oper.is_type(t.EE):
            result, error = left.compare_eq(right)
        elif oper.is_type(t.NE):
            result, error = left.compare_ne(right)
        elif oper.is_type(t.LT):
            result, error = left.compare_lt(right)
        elif oper.is_type(t.GT):
            result, error = left.compare_gt(right)
        elif oper.is_type(t.LTE):
            result, error = left.compare_lte(right)
        elif oper.is_type(t.GTE):
            result, error = left.compare_gte(right)
        
        elif oper.is_equals(t.KW, 'and'):
            result, error = left.logic_and(right)
        elif oper.is_equals(t.KW, 'or'):
            result, error = left.logic_or(right)
        
        if error:
            return res.failure(error.set_pos(node.pos_start, node.pos_end))
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))
    
    def visit_UnaryOpNode(self, node: ast_parser.UnaryOpNode, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.error: return res
        
        error = None
        if node.oper.is_type(t.MINUS):
            number, error = number.operate_mul(Number(-1))
        elif node.oper.is_equals(t.KW, 'not'):
            number, error = number.logic_not()
        
        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))
    
    def visit_IfBlockNode(self, node: ast_parser.IfBlockNode, context):
        res = RTResult()
        cond = res.register(self.visit(node.case[0], context))
        if res.error: return res
        if cond.is_truthy():
            value = res.register(self.visit(node.case[1], context))
        else:
            value = res.register(self.visit(node.else_expr, context))
        
        if res.error: return res
        return res.success(value)
    
    def visit_FuncDefNode(self, node: ast_parser.FuncDefNode, context):
        res = RTResult()
        
        func = Function(node.name, node.parameters, node.body).set_pos(node.pos_start, node.pos_end).set_context(context)
        context.symbol_map.set(node.name, func)
        
        return res.success(
            func
        )
    
    def visit_FuncCallNode(self, node: ast_parser.FuncCallNode, context):
        res = RTResult()
        args = []
    
        value_to_call = res.register(self.visit(node.node_to_call, context))
        if res.error: return res
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)
    
        for arg_node in node.arguments:
            args.append(res.register(self.visit(arg_node, context)))
            if res.error: return res
        
        value_to_call: Function
        return_value = res.register(value_to_call.execute(args))
        if res.error:
            res.error.set_pos(node.pos_start, node.pos_end)
            return res
        return res.success(return_value)


GLOBAL_SYMBOL_MAP = SymbolMap()


def interpret(node, context) -> RTResult:
    interpreter = Interpreter()
    return interpreter.visit(node, context)


def run(file_name, text, debug_mode=False):
    tokens, error = tokenize(file_name, text)
    if debug_mode:
        print('TOKENS:', *tokens)

    if error is not None:
        return None, error

    node, parse_error = make_ast(tokens)

    if debug_mode:
        print('NODE  :', node)
        print('------')

    if parse_error is not None:
        return None, parse_error

    context = Context("<module>", symbol_map=GLOBAL_SYMBOL_MAP)
    res = interpret(node, context)
    return (None, res.error) if res.error else (res.value, None)
