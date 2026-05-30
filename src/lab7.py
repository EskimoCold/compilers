from mini_compiler.interpreter import Interpreter
from mini_compiler.lexer import Lexer
from mini_compiler.optimizer import DeadCodeOptimizer
from mini_compiler.parser import Parser


# 1. Code after return inside a function
AFTER_RETURN = """
fun classify(x) {
    if (x > 0) {
        return 1;
    } else {
        return -1;
    }
    print "this line is unreachable";
    print "so is this one";
}
var r = classify(5);
print r;
"""

# 2. Code after an if/else where both branches return
AFTER_ALWAYS_RETURN_IF = """
fun sign(x) {
    if (x > 0) {
        return 1;
    } else {
        return 0;
    }
    print "dead: both branches returned";
}
print sign(42);
print sign(-3);
"""

# 3. if with a literal-false condition (no else)
IF_FALSE_NO_ELSE = """
var x = 10;
if (0) {
    print "never printed";
    x = 999;
}
print x;
"""

# 4. if with a literal-false condition, has else -> else survives
IF_FALSE_WITH_ELSE = """
var result = 0;
if (0) {
    result = 1;
} else {
    result = 2;
}
print result;
"""

# 5. if with a literal-true condition -> else branch is dead
IF_TRUE_WITH_ELSE = """
var result = 0;
if (1) {
    result = 10;
} else {
    result = 99;
}
print result;
"""

# 6. while with a literal-false condition -> loop removed
WHILE_FALSE = """
var i = 0;
while (0) {
    i = i + 1;
    print "never";
}
print i;
"""

# 7. Constant-folded condition  (1 == 2 -> false, 3 > 1 -> true)
CONSTANT_FOLDED_CONDITION = """
if (1 == 2) {
    print "math is broken";
} else {
    print "1 != 2  (else survived)";
}

if (3 > 1) {
    print "3 > 1  (then survived)";
} else {
    print "math is broken";
}
"""

# 8. Nested: dead code inside a function body, combined patterns
NESTED = """
fun demo(n) {
    while (0) {
        print "loop never runs";
    }
    if (0) {
        print "if-false branch";
    } else {
        return n * 2;
    }
    print "unreachable after guaranteed return";
}
print demo(7);
"""


def _run(title: str, source: str) -> None:
    print(f"--- {title} ---")

    tokens = Lexer(source).tokenize()
    ast = Parser(tokens, source).parse()

    optimizer = DeadCodeOptimizer()
    optimized_ast, warnings = optimizer.optimize(ast)

    if warnings:
        for w in warnings:
            print(f"  [optimizer] {w}")
    else:
        print("  [optimizer] no dead code found")

    print("  Output:")
    interpreter = Interpreter(output=lambda s: print(f"    {s}"))
    interpreter.interpret(optimized_ast)
    print()


def main() -> None:
    print("=== Lab 7: Dead-code optimizer ===\n")

    _run("1. Code after return in a function", AFTER_RETURN)
    _run("2. Code after if/else that always returns", AFTER_ALWAYS_RETURN_IF)
    _run("3. if(0) with no else — statement removed", IF_FALSE_NO_ELSE)
    _run("4. if(0) with else — else branch kept", IF_FALSE_WITH_ELSE)
    _run("5. if(1) with else — else branch dead", IF_TRUE_WITH_ELSE)
    _run("6. while(0) — loop removed", WHILE_FALSE)
    _run("7. Constant-folded conditions (1==2, 3>1)", CONSTANT_FOLDED_CONDITION)
    _run("8. Nested: multiple patterns inside a function", NESTED)


if __name__ == "__main__":
    main()
