import math

from Scriptorium.ScriptoriumParser import ScriptoriumParser
from Scriptorium.ScriptoriumVisitor import ScriptoriumVisitor
from var import Var

class Visitor(ScriptoriumVisitor):
    var_map = {}
    recursion_level = 0

    def __init__(self, var_map):
        self.var_map = var_map
        super().__init__()

    # PRINT

    def visitPrint(self, ctx):
        print(self.visit(ctx.printExpr()))

    def visitPrintAdd(self, ctx):
        return self.visit(ctx.printExpr(0))+', '+self.visit(ctx.printExpr(1))        
    
    def visitExprInPrint(self, ctx):
        return str(self.visit(ctx.expr()))

    # STRING

    def visitString(self, ctx):
        text = ctx.STRING().getText()[1:-1]
        text = text.replace("\\\\", "\\")
        text = text.replace("\\\"", "\"")
        return text

    def visitStringAdd(self, ctx):
        return self.visit(ctx.stringExpr(0))+self.visit(ctx.stringExpr(1))

    # NUMERIC

    def visitNumericInt(self, ctx):
        return float(ctx.INT().getText())
    def visitNumericFloat(self, ctx):
        return float(ctx.FLOAT().getText().replace(",", "."))

    def visitNumericPlusMinus(self, ctx):
        match ctx.op.type:
            case ScriptoriumParser.PLUS:
                return self.visit(ctx.numericExpr())
            case ScriptoriumParser.MINUS:
                return -self.visit(ctx.numericExpr())

    def visitNumericBrackets(self, ctx):
        return self.visit(ctx.numericExpr())

    def visitNumericPow(self, ctx):
        primary = self.visit(ctx.numericExpr(0))
        secondary = self.visit(ctx.numericExpr(1))
        return math.pow(primary, secondary)
            
    def visitNumericMulDiv(self, ctx):
        primary = self.visit(ctx.numericExpr(0))
        secondary = self.visit(ctx.numericExpr(1))
        match ctx.op.type:
            case ScriptoriumParser.MUL:
                return primary * secondary
            case ScriptoriumParser.DIV:
                return primary / secondary
            case ScriptoriumParser.FDIV:
                return primary // secondary

    def visitNumericAddSub(self, ctx):
        primary = self.visit(ctx.numericExpr(0))
        secondary = self.visit(ctx.numericExpr(1))
        match ctx.op.type:
            case ScriptoriumParser.ADD:
                return primary+secondary
            case ScriptoriumParser.SUB:
                return primary-secondary

    def visitNumericMod(self, ctx):
        primary = self.visit(ctx.numericExpr(0))
        secondary = self.visit(ctx.numericExpr(1))
        return primary % secondary
    
    # INT

    def visitInt(self, ctx):
        return int(self.visit(ctx.numericExpr()))
    
    # FLOAT
    
    def visitFloat(self, ctx):
        return float(str(self.visit(ctx.numericExpr())).replace(",", "."))   

    # NULL
    
    def visitNull(self, ctx):
        return None

    # BOOL

    def visitBool(self, ctx):
        match ctx.BOOL().getText():
            case 'verum':
                return True
            case 'falsum':
                return False
            
    def visitBoolBrackets(self, ctx):
        return self.visit(ctx.boolExpr())

    def visitStringLogic(self, ctx):
        primary:str = self.visit(ctx.stringExpr(0))
        secondary:str = self.visit(ctx.stringExpr(1))
        match ctx.op.type:
            case ScriptoriumParser.EQ:
                return primary == secondary
            case ScriptoriumParser.NEQ:
                return primary != secondary
            case ScriptoriumParser.LT:
                return primary < secondary
            case ScriptoriumParser.GT:
                return primary > secondary
            case ScriptoriumParser.LE:
                return primary <= secondary
            case ScriptoriumParser.GE:
                return primary >= secondary

    def visitNumericLogic(self, ctx):
        primary:float = self.visit(ctx.numericExpr(0))
        secondary:float = self.visit(ctx.numericExpr(1))
        match ctx.op.type:
            case ScriptoriumParser.EQ:
                return primary == secondary
            case ScriptoriumParser.NEQ:
                return primary != secondary
            case ScriptoriumParser.LT:
                return primary < secondary
            case ScriptoriumParser.GT:
                return primary > secondary
            case ScriptoriumParser.LE:
                return primary <= secondary
            case ScriptoriumParser.GE:
                return primary >= secondary

    def visitBoolLogic(self, ctx):
        primary:bool = self.visit(ctx.boolExpr(0))
        secondary:bool = self.visit(ctx.boolExpr(1))
        match ctx.op.type:
            case ScriptoriumParser.AND:
                return primary and secondary
            case ScriptoriumParser.OR:
                return primary or secondary
            case ScriptoriumParser.EQ:
                return primary == secondary
            case ScriptoriumParser.NEQ:
                return primary != secondary

    def visitBoolNot(self, ctx):
        primary:bool = self.visit(ctx.boolExpr())
        return not primary

    # VAR
    
    def visitVariableDefinition(self, ctx):
        def changeOrAppend(list: list[any], index: int, value: any):
            try: var.value[self.recursion_level] = value
            except: var.value.append(value)

        parentCtx = ctx.parentCtx.parentCtx
        parentCtx = parentCtx if type(parentCtx) != ScriptoriumParser.ActionContext else parentCtx.parentCtx

        var: Var = self.var_map[parentCtx][ctx.NAME().getText()]

        value = self.visit(ctx.expr())
        try:
            match var.typeId:
                case ScriptoriumParser.INT_TYPE:
                    value = trans if type(value) == str and (trans:=str(value).replace(',', '.')) else value
                    changeOrAppend(var.value, self.recursion_level, int(float(value)))
                case ScriptoriumParser.FLOAT_TYPE:
                    value = trans if type(value) == str and (trans:=str(value).replace(',', '.')) else value
                    changeOrAppend(var.value, self.recursion_level, float(value))
                case ScriptoriumParser.STRING_TYPE:
                    changeOrAppend(var.value, self.recursion_level, str(value))
                case ScriptoriumParser.BOOL_TYPE:
                    changeOrAppend(var.value, self.recursion_level, bool(value))
        except:
            raise Exception(f"CULPA: linea {ctx.start.line}:{ctx.start.column} - type transformation error")

    def visitVarExpr(self, ctx):
        return Var.nearestScopeVariable(ctx, self.var_map, self.recursion_level)
    
    # INPUT

    def visitInputExpr(self, ctx):
        return input(self.visit(ctx.printExpr()))