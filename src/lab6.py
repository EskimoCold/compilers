#!/usr/bin/env python3

from mini_compiler.interpreter import Interpreter
from mini_compiler.lexer import Lexer
from mini_compiler.parser import Parser
from mini_compiler.semantic_analyzer import SemanticAnalyzer


def main() -> None:
    basic_sample = """
        fun add(x, y) {
            return x + y;
        }

        var result = add(5, 10);
        print "Expected: 15";
        print result;
        """

    assign_result_sample = """
        fun square(n) {
            return n * n;
        }

        var a = square(4);
        var b = square(3);
        print "4^2 =";
        print a;
        print "3^2 =";
        print b;
        print "Sum =";
        print a + b;
        """

    call_as_stmt_sample = """
        fun greet(name) {
            print name;
        }

        greet("Hello, functions!");
        """

    no_return_sample = """
        fun nothing() {
            var x = 42;
        }

        var r = nothing();
        print "Result of void function:";
        print r;
        """

    print("=== Lab 6: Functions ===")
    print()

    print("--- Basic function call + assignment ---")
    _run(basic_sample)
    print()

    print("--- Function result used in expressions ---")
    _run(assign_result_sample)
    print()

    print("--- Function call as statement ---")
    _run(call_as_stmt_sample)
    print()

    print("--- Function with no return (returns null) ---")
    _run(no_return_sample)
    print()


def _run(source: str) -> None:
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    parser = Parser(tokens, source)
    ast = parser.parse()

    analyzer = SemanticAnalyzer()
    errors = analyzer.analyze(ast)
    for error in errors:
        print(f"  [semantic] {error}")

    interpreter = Interpreter()
    interpreter.interpret(ast)


if __name__ == "__main__":
    main()
