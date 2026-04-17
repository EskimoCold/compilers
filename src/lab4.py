#!/usr/bin/env python3

from mini_compiler.lexer import Lexer
from mini_compiler.parser import Parser
from mini_compiler.type_checker import TypeChecker


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

    error_sample = """
            var n = 1;
            var s = "hi";
            var flag = n < 10;

            n = s;
            print n + s;
            print flag + 1;

            if (n) {
                print "bad condition";
            }

            while (s) {
                print "also bad";
            }

            print !n;
            print -s;
            print n == s;
            """

    print("=== Lab 4: Type checking ===")
    print()

    print("--- Valid program ---")
    _check(acceptance_sample)
    print()

    print("--- Program with type errors ---")
    _check(error_sample)
    print()


def _check(source: str) -> None:
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    parser = Parser(tokens, source)
    ast = parser.parse()

    checker = TypeChecker()
    errors = checker.check(ast)

    if not errors:
        print("No type issues found.")
        return

    for message in errors:
        print(message)


if __name__ == "__main__":
    main()
