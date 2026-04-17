#!/usr/bin/env python3

from mini_compiler.lexer import Lexer
from mini_compiler.parser import Parser
from mini_compiler.semantic_analyzer import SemanticAnalyzer


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
            var x = 1;
            var x = 2;
            y = 5;
            print z;
            var unused = 42;
            {
                var inner = 10;
            }
            """

    print("=== Lab 3: Semantic analysis ===")
    print()

    print("--- Valid program ---")
    _analyze(acceptance_sample)
    print()

    print("--- Program with semantic errors ---")
    _analyze(error_sample)
    print()


def _analyze(source: str) -> None:
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    parser = Parser(tokens, source)
    ast = parser.parse()

    analyzer = SemanticAnalyzer()
    errors = analyzer.analyze(ast)

    if not errors:
        print("No semantic issues found.")
        return

    for message in errors:
        print(message)


if __name__ == "__main__":
    main()
