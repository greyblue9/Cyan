from tokens import t

from utils import InvalidSyntaxError


# for type hinting
from tokens import Token


class Node:
    pos_start = None
    pos_end = None
    
    def set_pos(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self


class NumberNode(Node):
    def __init__(self, tok):
        self.tok = tok
        
        self.pos_start = tok.pos_start
        self.pos_end = tok.pos_end
    
    def __repr__(self):
        return str(self.tok)


class LiteralNode(Node):
    def __init__(self, tok):
        self.tok = tok
        
        self.pos_start = tok.pos_start
        self.pos_end = tok.pos_end
    
    def __repr__(self):
        return self.tok.value


class BinOpNode(Node):
    def __init__(self, left, oper, right):
        self.left = left
        self.oper = oper
        self.right = right
        
        self.pos_start = left.pos_start
        self.pos_end = right.pos_end
    
    def __repr__(self):
        return f"({self.left}, {self.oper}, {self.right})"


class UnaryOpNode(Node):
    def __init__(self, oper, node):
        self.oper = oper
        self.node = node
        
        self.pos_start = oper.pos_start
        self.pos_end = node.pos_end
    
    def __repr__(self):
        return f'({self.oper}, {self.node})'


class VarAccessNode(Node):
    def __init__(self, var_name):
        self.var_name = var_name
        
        self.pos_start = var_name.pos_start
        self.pos_end = var_name.pos_end
    
    def __repr__(self):
        return f'({self.var_name})'


class VarAssignNode(Node):
    def __init__(self, var_name, value):
        self.var_name = var_name
        self.value = value
        
        self.pos_start = var_name.pos_start
        self.pos_end = value.pos_end
    
    def __repr__(self):
        return f'({self.var_name} = {self.value})'


class IfBlockNode(Node):
    def __init__(self, case: tuple, else_expr):
        self.case = case
        self.else_expr = else_expr
        
        self.pos_start = case[0].pos_start
    
    def __repr__(self):
        return f'(if {self.case[0]} then {self.case[1]} else {self.else_expr})'


class FuncDefNode(Node):
    def __init__(self, name: str, parameters: list[Token], body: Node):
        self.name = name or '[lambda]'
        self.parameters = parameters
        self.body = body


class FuncCallNode(Node):
    def __init__(self, node_to_call: Node, arguments: list[Node]):
        self.node_to_call = node_to_call
        self.arguments = arguments


class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advancements = 0
    
    def register_adv(self):
        self.advancements += 1
    
    def register(self, res) -> Node:
        self.advancements += res.advancements
        if res.error: self.error = res.error
        return res.node
    
    def success(self, node):
        self.node = node
        return self
    
    def failure(self, error):
        if error is not None or self.advancements == 0:
            self.error = error
        return self


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.cur_index = -1
        self.cur_tok: Token = None
        self.advance()  # self.cur_tok will be set up in this call
    
    def advance(self):
        self.cur_index += 1
        if self.cur_index < len(self.tokens):
            self.cur_tok: Token = self.tokens[self.cur_index]
        return self.cur_tok
    
    def next_tok(self):
        if self.cur_index+1 < len(self.tokens):
            return self.tokens[self.cur_index+1]

    def parse(self):
        res = self.expr()
        if res.error is None and (not self.cur_tok.is_type(t.EOF, t.NEWLINE)):
            res.failure(
                InvalidSyntaxError(self.cur_tok.pos_start, self.cur_tok.pos_end, 'Invalid Syntax').set_ecode('p')
            )
            return res
        return res

    def expr(self):
        res = ParseResult()

        if self.cur_tok.is_equals(t.KW, 'let'):
            res.register_adv()
            self.advance()

            if not self.cur_tok.is_type(t.IDENTIFIER):
                return res.failure(
                    InvalidSyntaxError(self.cur_tok.pos_start, self.cur_tok.pos_end, "Expected identifier")
                )

            var_name = self.cur_tok
            res.register_adv()
            self.advance()

            if not self.cur_tok.is_type(t.EQ):
                return res.failure(
                    InvalidSyntaxError(self.cur_tok.pos_start, self.cur_tok.pos_end, "Expected '='")
                )

            res.register_adv()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res

            return res.success(
                VarAssignNode(var_name, expr)
            )

        node = res.register(self.bin_oper(self.comp_expr, ((t.KW, 'and'), (t.KW, 'or'))))
        if res.error: return res

        return res.success(node)
    
    def call(self):
        res = ParseResult()
        
        atom = res.register(self.atom())
        if res.error: return res
        
        if self.cur_tok.is_type(t.L_PAREN):
            args = []
            res.register_adv()
            self.advance()
            
            if not self.cur_tok.is_type(t.R_PAREN):
                arg = res.register(self.expr())
                if res.error: return res
                args.append(arg)
                
                while self.cur_tok.is_type(t.COMMA):
                    res.register_adv()
                    self.advance()
                    
                    arg = res.register(self.expr())
                    if res.error: return res
                    args.append(arg)
                    
                    if self.cur_tok.is_type(t.R_PAREN):
                        break
                    elif not self.cur_tok.is_type(t.COMMA):
                        return res.failure(
                            InvalidSyntaxError(self.cur_tok.pos_start, self.cur_tok.pos_end, "Expected ',' or ')'")
                        )
                
                if not self.cur_tok.is_type(t.R_PAREN):
                    return res.failure(
                        InvalidSyntaxError(self.cur_tok.pos_start, self.cur_tok.pos_end, "Expected ')'")
                    )
            pos_end = self.cur_tok.pos_end.copy()
            res.register_adv()
            self.advance()
            
            return res.success(FuncCallNode(atom, args).set_pos(atom.pos_start, pos_end))
        return res.success(atom)

    def atom(self):
        res = ParseResult()
        tok = self.cur_tok
        
        if tok.is_type(t.INT, t.FLOAT):
            res.register_adv()
            self.advance()
            return res.success(NumberNode(tok))
        
        elif tok.is_type(t.LITERAL):
            res.register_adv()
            self.advance()
            return res.success(LiteralNode(tok))
        
        elif tok.is_type(t.L_PAREN):
            res.register_adv()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            if self.cur_tok.is_type(t.R_PAREN):
                res.register_adv()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(self.cur_tok.pos_start, self.cur_tok.pos_end, "Expected ')'"))
        
        elif tok.is_type(t.IDENTIFIER):
            res.register_adv()
            self.advance()
            return res.success(VarAccessNode(tok))
        
        elif tok.is_equals(t.KW, 'if'):
            node = res.register(self.if_expr())
            
            return res.success(node)
        
        elif tok.is_equals(t.KW, 'fun'):
            node = res.register(self.func_def())
            
            return res.success(node)
        
        return res.failure(
            InvalidSyntaxError(tok.pos_start, tok.pos_end, "Expected Value: identifier, int, float, '+', '-' or '('")
        )
    
    def factor(self):
        res = ParseResult()
        tok = self.cur_tok
        
        if tok.is_type(t.PLUS, t.MINUS):
            res.register_adv()
            self.advance()
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))
        
        return self.power()
    
    def term(self):
        return self.bin_oper(self.factor, (t.MUL, t.DIV))

    def power(self):
        return self.bin_oper(self.call, (t.POW,), self.factor)

    def arith_expr(self):
        return self.bin_oper(self.term, (t.PLUS, t.MINUS))
    
    def comp_expr(self):
        res = ParseResult()
        if self.cur_tok.is_equals(t.KW, 'not'):
            op_tok = self.cur_tok
            res.register_adv()
            self.advance()
            
            node = res.register(self.comp_expr())
            if res.error: return res
            
            return res.success(UnaryOpNode(op_tok, node))
        node = res.register(self.bin_oper(self.arith_expr, (t.EE, t.NE, t.LT, t.GT, t.LTE, t.GTE)))
        
        if res.error: return res
        
        return res.success(node)

    def bin_oper(self, func_left, operators, func_right=None):
        if func_right is None:
            func_right = func_left
        
        res = ParseResult()
        
        left = res.register(func_left())
        if res.error:
            return res
        
        while self.cur_tok.is_type(*operators) or (self.cur_tok.type_, self.cur_tok.value) in operators:
            op_tok = self.cur_tok
            res.register_adv()
            self.advance()
            right = res.register(func_right())
            if res.error: return res
            
            left = BinOpNode(left, op_tok, right)
        
        return res.success(left)

    def if_expr(self):
        # self.cur_tok is KW:if
        res = ParseResult()
        res.register_adv()
        self.advance()
    
        cond = res.register(self.comp_expr())
        if res.error: return res
    
        if not self.cur_tok.is_equals(t.KW, 'then'):
            return res.failure(
                InvalidSyntaxError(self.cur_tok.pos_start, self.cur_tok.pos_end, "Expected 'then'")
            )
        res.register_adv()
        self.advance()
    
        expr = res.register(self.expr())
        if res.error: return res
    
        if not self.cur_tok.is_equals(t.KW, 'else'):
            return res.failure(
                InvalidSyntaxError(self.cur_tok.pos_start, self.cur_tok.pos_end, "Expected 'else'")
            )
    
        res.register_adv()
        self.advance()
    
        else_expr = res.register(self.expr())
        if res.error: return res
    
        return res.success(IfBlockNode((cond, expr), else_expr))
    
    def func_def(self):
        # self.cur_tok is KW:fun
        res = ParseResult()
        res.register_adv()
        name = ''
        pos_start = self.cur_tok.pos_start
        res.register_adv()
        self.advance()
        
        if self.cur_tok.is_type(t.IDENTIFIER):
            name = self.cur_tok.value
            res.register_adv()
            self.advance()

        if not self.cur_tok.is_type(t.L_PAREN):
            return res.failure(
                InvalidSyntaxError(self.cur_tok.pos_start, self.cur_tok.pos_end,
                                   "Expected '('" if name else "Expected Identifier or '('")
            )
        res.register_adv()
        self.advance()
        
        parameters = []
        if self.cur_tok.is_type(t.IDENTIFIER):
            parameters.append(self.cur_tok)
            res.register_adv()
            self.advance()

            while self.cur_tok.is_type(t.COMMA):
                res.register_adv()
                self.advance()
                
                if self.cur_tok.is_type(t.IDENTIFIER):
                    parameters.append(self.cur_tok)
                    res.register_adv()
                    self.advance()
                elif self.cur_tok.is_type(t.R_PAREN):
                    break
                else:
                    return res.failure(
                        InvalidSyntaxError(self.cur_tok.pos_start, self.cur_tok.pos_end, "Expected ',' or ')'")
                    )
        
        if not self.cur_tok.is_type(t.R_PAREN):
            return res.failure(
                InvalidSyntaxError(self.cur_tok.pos_start, self.cur_tok.pos_end, "Invalid Syntax").set_ecode('fd')
            )
        
        res.register_adv()
        self.advance()
        if not self.cur_tok.is_type(t.COLON):
            return res.failure(
                InvalidSyntaxError(self.cur_tok.pos_start, self.cur_tok.pos_end, "Expected ':'")
            )
        res.register_adv()
        self.advance()
        
        expr = res.register(self.expr())
        if res.error:
            return res

        return res.success(
            FuncDefNode(name, parameters, expr).set_pos(pos_start, expr.pos_end)
        )


def make_ast(tokens):
    parser = Parser(tokens)
    res = parser.parse()
    return res.node, res.error
