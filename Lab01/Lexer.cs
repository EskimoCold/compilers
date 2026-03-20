/*
 Example language fragment:
   var x = 2;
   print x + 5;
   print "hello world";

 ops: + - * /
 strings: "..."
 keywords: var print if else while
*/

namespace Lab01;

public sealed class Lexer
{
    private readonly string _input;
    private readonly int _length;
    private int _position;

    public Lexer(string input)
    {
        _input = input;
        _length = input.Length;
        _position = 0;
    }

    public List<Token> Tokenize()
    {
        var result = new List<Token>();

        while (_position < _length)
        {
            var current = Peek();

            if (char.IsWhiteSpace(current))
            {
                Next();
                continue;
            }

            if (char.IsDigit(current))
            {
                TokenizeNumber(result);
                continue;
            }

            if (char.IsLetter(current))
            {
                TokenizeWord(result);
                continue;
            }

            if (current == '"')
            {
                TokenizeString(result);
                continue;
            }

            TokenizeOperator(result);
        }

        return result;
    }

    private void TokenizeNumber(List<Token> result)
    {
        var start = _position;

        while (char.IsDigit(Peek()))
            Next();

        var numberStr = _input.Substring(start, _position - start);
        result.Add(new Token(TokenType.NUMBER, numberStr, start));
    }

    private void TokenizeWord(List<Token> result)
    {
        var start = _position;

        while (char.IsLetterOrDigit(Peek()))
            Next();

        var word = _input.Substring(start, _position - start);

        switch (word)
        {
            case "var":
                AddToken(result, TokenType.VAR, word, start);
                break;
            case "print":
                AddToken(result, TokenType.PRINT, word, start);
                break;
            case "if":
                AddToken(result, TokenType.IF, word, start);
                break;
            case "else":
                AddToken(result, TokenType.ELSE, word, start);
                break;
            case "while":
                AddToken(result, TokenType.WHILE, word, start);
                break;
            default:
                AddToken(result, TokenType.ID, word, start);
                break;
        }
    }

    /// <summary>Double-quoted string: <c>"hello world"</c> → value is the inner text (no quotes).</summary>
    private void TokenizeString(List<Token> result)
    {
        var start = _position;
        Next(); // opening "

        var contentStart = _position;
        while (_position < _length && Peek() != '"')
            Next();

        if (_position >= _length)
            throw new InvalidOperationException($"Unterminated string starting at position {start}");

        var inner = _input.Substring(contentStart, _position - contentStart);
        Next(); // closing "

        result.Add(new Token(TokenType.STRING, inner, start));
    }

    private void TokenizeOperator(List<Token> result)
    {
        var current = Peek();
        var start = _position;

        switch (current)
        {
            case '+':
                Next();
                AddToken(result, TokenType.PLUS, "+", start);
                break;
            case '-':
                Next();
                AddToken(result, TokenType.MINUS, "-", start);
                break;
            case '*':
                Next();
                AddToken(result, TokenType.STAR, "*", start);
                break;
            case '/':
                Next();
                AddToken(result, TokenType.SLASH, "/", start);
                break;
            case '=':
                Next();
                AddToken(result, TokenType.EQ, "=", start);
                break;
            case ';':
                Next();
                AddToken(result, TokenType.SEMICOLON, ";", start);
                break;

            default:
                throw new InvalidOperationException(
                    $"Unexpected character '{current}' at position {_position}");
        }
    }

    /// <summary>Current character without consuming it.</summary>
    private char Peek()
    {
        if (_position >= _length)
            return '\0';

        return _input[_position];
    }

    /// <summary>Consume and return current character.</summary>
    private char Next()
    {
        if (_position >= _length)
            return '\0';

        return _input[_position++];
    }

    private static void AddToken(List<Token> result, TokenType type, string value, int start) =>
        result.Add(new Token(type, value, start));
}
