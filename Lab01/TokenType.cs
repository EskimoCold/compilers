namespace Lab01;

public enum TokenType
{
    NUMBER,
    ID,
    STRING,
    VAR,

    PRINT,
    IF,
    ELSE,
    WHILE,

    // Operators
    PLUS,
    MINUS,
    STAR,
    SLASH, // + - * /
    EQ,
    EQEQ,
    EXCL,
    NEQ, // = == ! !=
    LT,
    GT,
    LTEQ,
    GTEQ, // < > <= >=
    AND,
    OR, // && ||

    // Grouping & Punctuation
    LPAREN,
    RPAREN, // ( )
    LBRACE,
    RBRACE, // { }
    SEMICOLON, // ;

    EOF // end of input
}
