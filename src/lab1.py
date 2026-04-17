#!/usr/bin/env python3

from mini_compiler.lexer import Lexer


def main() -> None:
    sample = """
            var x = 1;
            print x + 5;
            print "hello";
            """

    print("=== Lab 1: Lexer ===")
    print()

    lexer = Lexer(sample)
    for token in lexer.tokenize():
        print(token)


if __name__ == "__main__":
    main()
