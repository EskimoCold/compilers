from mini_compiler.interpreter import Interpreter
from mini_compiler.lexer import Lexer
from mini_compiler.parser import Parser
from mini_compiler.semantic_analyzer import SemanticAnalyzer


BASIC = """
var a = [10, 20, 30];
print a;
print a[0];
print a[1];
print a[2];
"""

WRITE_ELEMENT = """
var a = [1, 2, 3];
a[1] = 99;
print a;
"""

EXPRESSION = """
var a = [3, 7, 5];
print a[0] + a[1];
print a[2] * 2;
"""

INLINE_LITERAL = """
print [100, 200, 300][1];
"""

WHILE_TRAVERSAL = """
var nums = [4, 8, 15, 16, 23, 42];
var i = 0;
var sum = 0;
while (i < 6) {
    sum = sum + nums[i];
    i = i + 1;
}
print "Sum:";
print sum;
"""

FUNCTION_WITH_ARRAY = """
fun first(arr) {
    return arr[0];
}

fun last3(arr) {
    return arr[2];
}

var data = [10, 20, 30];
print first(data);
print last3(data);
"""

NESTED_ARRAY_WRITE = """
var matrix = [0, 0, 0, 0];
matrix[0] = 1;
matrix[1] = 2;
matrix[2] = 3;
matrix[3] = 4;
print matrix;
"""

def _run(title: str, source: str) -> None:
    print(f"--- {title} ---")

    tokens = Lexer(source).tokenize()
    ast = Parser(tokens, source).parse()

    analyzer = SemanticAnalyzer()
    errors = analyzer.analyze(ast)
    for e in errors:
        print(f"  [semantic] {e}")

    interpreter = Interpreter(output=lambda s: print(f"  {s}"))
    interpreter.interpret(ast)
    print()


def main() -> None:
    print("=== Lab 8: Arrays ===\n")

    _run("1. Basic array + read elements", BASIC)
    _run("2. Write element (index assignment)", WRITE_ELEMENT)
    _run("3. Array elements in expressions", EXPRESSION)
    _run("4. Inline literal indexing [100,200,300][1]", INLINE_LITERAL)
    _run("5. While loop traversal + sum", WHILE_TRAVERSAL)
    _run("6. Array as function argument", FUNCTION_WITH_ARRAY)
    _run("7. Building array by index writes", NESTED_ARRAY_WRITE)


if __name__ == "__main__":
    main()
