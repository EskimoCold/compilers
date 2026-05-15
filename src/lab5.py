#!/usr/bin/env python3

from mini_compiler.interpreter import Interpreter
from mini_compiler.lexer import Lexer
from mini_compiler.parser import Parser


def main() -> None:
    acceptance_sample = """
            var limit = 10;
            var current = 0;

            while (current < limit) {
                if (current == 5) {
                    print current * 100;
                } else {
                    print current;
                }
                current = current + 1;
            }
            """

    scope_sample = """
            var x = 1;
            {
                var x = 100;
                print x;
            }
            print x;
            """

    print("=== Lab 5: Tree-walking interpreter ===")
    print()

    print("--- Acceptance sample output ---")
    _run(acceptance_sample)
    print()

    print("--- Block scoping sample output ---")
    _run(scope_sample)
    print()


def _run(source: str) -> None:
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    parser = Parser(tokens, source)
    ast = parser.parse()

    interpreter = Interpreter()
    interpreter.interpret(ast)


if __name__ == "__main__":
    main()
