#!/usr/bin/env python3

from mini_compiler.ast_printer import format_tree
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

    print("=== Lab 2: Parser - AST tree ===")
    print()

    lexer = Lexer(acceptance_sample)
    tokens = lexer.tokenize()

    parser = Parser(tokens, acceptance_sample)
    ast = parser.parse()

    print(format_tree(ast))
    print()


if __name__ == "__main__":
    main()
